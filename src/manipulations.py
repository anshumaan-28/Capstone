
import os
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt


class INSATBandManipulator:
    def __init__(self, cog_directory="../../output/converted_cogs", output_directory="../../output/manipulations"):
        """
        Initialize the band manipulator with paths to COG files and output directory
        """
        self.cog_directory = cog_directory
        self.output_directory = output_directory
        
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
    
    def get_available_cogs(self):
        """
        Get a list of available COG files in the directory
        """
        cog_files = {}
        if os.path.exists(self.cog_directory):
            for filename in os.listdir(self.cog_directory):
                if filename.endswith("_cog.tif"):
                    band_name = filename.split("_cog.tif")[0]
                    cog_files[band_name] = os.path.join(self.cog_directory, filename)
        
        return cog_files
    
    def load_band_data(self, band_name):
        """
        Load data from a specific band
        """
        cogs = self.get_available_cogs()
        
        if band_name not in cogs:
            print(f"Band {band_name} not found as a COG file")
            return None, None
        
        with rasterio.open(cogs[band_name]) as src:
            band_data = src.read(1)
            profile = src.profile.copy()
            
        return band_data, profile
    
    def normalize_data(self, data):
        """
        Normalize data to 0-1 range for visualization
        """
        min_val = np.min(data)
        max_val = np.max(data)
        
        if max_val > min_val:
            return (data - min_val) / (max_val - min_val)
        else:
            return data * 0
    
    def band_difference(self, band1, band2, output_name=None):
        """
        Calculate the difference between two bands (band1 - band2)
        Useful for change detection or highlighting specific features
        """
        if output_name is None:
            output_name = f"diff_{band1}_{band2}"
            
        output_path = os.path.join(self.output_directory, f"{output_name}.tif")
        
        # Load band data
        data1, profile1 = self.load_band_data(band1)
        data2, profile2 = self.load_band_data(band2)
        
        if data1 is None or data2 is None:
            print("Could not load band data")
            return None
            
        if data1.shape != data2.shape:
            print("Band shapes do not match")
            return None
            
        # Calculate difference
        diff_data = data1.astype(np.float32) - data2.astype(np.float32)
        
        # Write output
        profile1.update(dtype=rasterio.float32)
        with rasterio.open(output_path, 'w', **profile1) as dst:
            dst.write(diff_data, 1)
            dst.update_tags(
                OPERATION="DIFFERENCE",
                BAND1=band1,
                BAND2=band2
            )
            
        # Create visualization
        plt.figure(figsize=(10, 8))
        plt.title(f"Band Difference: {band1} - {band2}")
        plt.imshow(diff_data, cmap='coolwarm')
        plt.colorbar(label='Difference')
        plt.axis('off')
        plt.tight_layout()
        
        # Save visualization
        vis_path = os.path.join(self.output_directory, f"{output_name}_vis.png")
        plt.savefig(vis_path, dpi=300, bbox_inches='tight')
        plt.close()
            
        print(f"✅ Band difference calculated: {output_path}")
        print(f"✅ Visualization saved: {vis_path}")
        
        return output_path
    
    def band_ratio(self, band_numerator, band_denominator, output_name=None):
        """
        Calculate the ratio between two bands (numerator / denominator)
        Useful for indices like NDVI, NDWI, etc.
        """
        if output_name is None:
            output_name = f"ratio_{band_numerator}_{band_denominator}"
            
        output_path = os.path.join(self.output_directory, f"{output_name}.tif")
        
        # Load band data
        data1, profile1 = self.load_band_data(band_numerator)
        data2, profile2 = self.load_band_data(band_denominator)
        
        if data1 is None or data2 is None:
            print("Could not load band data")
            return None
            
        if data1.shape != data2.shape:
            print("Band shapes do not match")
            return None
            
        # Avoid division by zero
        valid_mask = data2 != 0
        ratio_data = np.zeros_like(data1, dtype=np.float32)
        ratio_data[valid_mask] = data1[valid_mask].astype(np.float32) / data2[valid_mask].astype(np.float32)
        
        # Write output
        profile1.update(dtype=rasterio.float32)
        with rasterio.open(output_path, 'w', **profile1) as dst:
            dst.write(ratio_data, 1)
            dst.update_tags(
                OPERATION="RATIO",
                NUMERATOR=band_numerator,
                DENOMINATOR=band_denominator
            )
            
        # Create visualization (with normalization for better display)
        # Clip extreme values for better visualization
        p2, p98 = np.percentile(ratio_data[valid_mask], (2, 98))
        display_data = np.clip(ratio_data, p2, p98)
        
        plt.figure(figsize=(10, 8))
        plt.title(f"Band Ratio: {band_numerator} / {band_denominator}")
        plt.imshow(display_data, cmap='viridis')
        plt.colorbar(label='Ratio')
        plt.axis('off')
        plt.tight_layout()
        
        # Save visualization
        vis_path = os.path.join(self.output_directory, f"{output_name}_vis.png")
        plt.savefig(vis_path, dpi=300, bbox_inches='tight')
        plt.close()
            
        print(f"✅ Band ratio calculated: {output_path}")
        print(f"✅ Visualization saved: {vis_path}")
        
        return output_path
    
    def normalized_difference_index(self, band1, band2, output_name=None):
        """
        Calculate normalized difference index between two bands: (band1 - band2) / (band1 + band2)
        This is the generalized form of indices like NDVI, NDWI, etc.
        """
        if output_name is None:
            output_name = f"NDI_{band1}_{band2}"
            
        output_path = os.path.join(self.output_directory, f"{output_name}.tif")
        
        # Load band data
        data1, profile1 = self.load_band_data(band1)
        data2, profile2 = self.load_band_data(band2)
        
        if data1 is None or data2 is None:
            print("Could not load band data")
            return None
            
        if data1.shape != data2.shape:
            print("Band shapes do not match")
            return None
            
        # Convert to float
        data1 = data1.astype(np.float32)
        data2 = data2.astype(np.float32)
        
        # Calculate normalized difference index
        sum_data = data1 + data2
        diff_data = data1 - data2
        
        # Avoid division by zero
        valid_mask = sum_data != 0
        ndi_data = np.zeros_like(sum_data, dtype=np.float32)
        ndi_data[valid_mask] = diff_data[valid_mask] / sum_data[valid_mask]
        
        # NDI ranges from -1 to 1
        
        # Write output
        profile1.update(dtype=rasterio.float32)
        with rasterio.open(output_path, 'w', **profile1) as dst:
            dst.write(ndi_data, 1)
            dst.update_tags(
                OPERATION="NORMALIZED_DIFFERENCE_INDEX",
                BAND1=band1,
                BAND2=band2
            )
            
        # Create visualization
        plt.figure(figsize=(10, 8))
        plt.title(f"Normalized Difference Index: {band1} & {band2}")
        plt.imshow(ndi_data, cmap='RdYlGn', vmin=-1, vmax=1)
        plt.colorbar(label='NDI (-1 to 1)')
        plt.axis('off')
        plt.tight_layout()
        
        # Save visualization
        vis_path = os.path.join(self.output_directory, f"{output_name}_vis.png")
        plt.savefig(vis_path, dpi=300, bbox_inches='tight')
        plt.close()
            
        print(f"✅ Normalized Difference Index calculated: {output_path}")
        print(f"✅ Visualization saved: {vis_path}")
        
        return output_path
    
    def extract_region(self, band_name, x_start, y_start, width, height, output_name=None):
        """
        Extract a spatial subset from a band
        
        Args:
            band_name: Name of the band to extract from
            x_start, y_start: Starting coordinates (in pixels)
            width, height: Size of the region (in pixels)
            output_name: Custom name for the output file
        """
        if output_name is None:
            output_name = f"{band_name}_region_{x_start}_{y_start}_{width}x{height}"
            
        output_path = os.path.join(self.output_directory, f"{output_name}.tif")
        
        cogs = self.get_available_cogs()
        if band_name not in cogs:
            print(f"Band {band_name} not found as a COG file")
            return None
            
        # Read the windowed region
        with rasterio.open(cogs[band_name]) as src:
            window = Window(x_start, y_start, width, height)
            region_data = src.read(1, window=window)
            
            # Get transform for the window
            window_transform = src.window_transform(window)
            
            # Create profile for the output
            profile = src.profile.copy()
            profile.update({
                'height': height,
                'width': width,
                'transform': window_transform
            })
            
            # Write the region to a new file
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(region_data, 1)
                dst.update_tags(
                    PARENT_BAND=band_name,
                    REGION_X=x_start,
                    REGION_Y=y_start,
                    REGION_WIDTH=width,
                    REGION_HEIGHT=height
                )
        
        # Create visualization
        plt.figure(figsize=(10, 8))
        plt.title(f"Region from {band_name}")
        plt.imshow(region_data, cmap='gray')
        plt.colorbar(label='Value')
        plt.axis('off')
        plt.tight_layout()
        
        # Save visualization
        vis_path = os.path.join(self.output_directory, f"{output_name}_vis.png")
        plt.savefig(vis_path, dpi=300, bbox_inches='tight')
        plt.close()
            
        print(f"✅ Region extracted: {output_path}")
        print(f"✅ Visualization saved: {vis_path}")
        
        return output_path


def demo_manipulations():
    """
    Demo function to test the manipulations
    """
    manipulator = INSATBandManipulator()
    
    # Check for available COGs
    cogs = manipulator.get_available_cogs()
    if not cogs:
        print("No COG files found. Please convert bands to COG format first.")
        return
    
    print(f"Found {len(cogs)} COG files: {list(cogs.keys())}")
    
    if len(cogs) >= 2:
        # Get first two bands for demonstration
        bands = list(cogs.keys())[:2]
        
        # Band difference
        print(f"\nCalculating difference between {bands[0]} and {bands[1]}...")
        manipulator.band_difference(bands[0], bands[1])
        
        # Band ratio
        print(f"\nCalculating ratio of {bands[0]} to {bands[1]}...")
        manipulator.band_ratio(bands[0], bands[1])
        
        # Normalized difference
        print(f"\nCalculating normalized difference index...")
        manipulator.normalized_difference_index(bands[0], bands[1])
        
    # Extract region from first band
    if cogs:
        first_band = list(cogs.keys())[0]
        print(f"\nExtracting region from {first_band}...")
        # Extract a central region (adjust based on typical image sizes)
        with rasterio.open(cogs[first_band]) as src:
            width = src.width
            height = src.height
            
        # Extract central region (1/4 of the image)
        x_start = width // 4
        y_start = height // 4
        extract_width = width // 2
        extract_height = height // 2
        
        manipulator.extract_region(
            first_band, x_start, y_start, 
            extract_width, extract_height
        )
    
    print(f"\n✅ All manipulations saved to: {manipulator.output_directory}")

if __name__ == "__main__":
    demo_manipulations()

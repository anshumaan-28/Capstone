import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import rasterio
from rasterio.plot import show
import h5py
from PIL import Image

class INSATVisualizer:
    def __init__(self, cog_directory="../../output/converted_cogs", output_directory="../../output/visualizations"):
        """
        Initialize the visualizer with paths to COG files and output directory
        """
        self.cog_directory = cog_directory
        self.output_directory = output_directory
        
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Define common band combinations
        self.band_combinations = {
            "natural_color": ["IMG_VIS", "IMG_SWIR", "IMG_TIR1"],
            "false_color": ["IMG_SWIR", "IMG_VIS", "IMG_WV"],
            "thermal": ["IMG_TIR1", "IMG_TIR2", "IMG_MIR"]
        }
    
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
    
    def visualize_single_band(self, band_name, colormap='gray', stretch=True):
        """
        Create a grayscale visualization of a single band
        
        Args:
            band_name: Name of the band to visualize (e.g. 'IMG_VIS')
            colormap: Matplotlib colormap name to use
            stretch: Apply contrast stretching to enhance visibility
        """
        cogs = self.get_available_cogs()
        
        if band_name not in cogs:
            print(f"Band {band_name} not found as a COG file")
            return None
        
        output_path = os.path.join(self.output_directory, f"{band_name}_visualization.png")
        
        with rasterio.open(cogs[band_name]) as src:
            # Read the data
            band_data = src.read(1)
            
            # Apply contrast stretching if requested
            if stretch:
                p2, p98 = np.percentile(band_data, (2, 98))
                band_data = np.clip(band_data, p2, p98)
                band_data = (band_data - p2) / (p98 - p2)
            
            # Create the plot
            plt.figure(figsize=(10, 10))
            plt.title(f"{band_name} Band Visualization")
            plt.imshow(band_data, cmap=colormap)
            plt.colorbar(label=f"{band_name} Values")
            plt.axis('off')
            plt.tight_layout()
            
            # Save the figure
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Visualization saved to {output_path}")
            
        return output_path
    
    def create_rgb_composite(self, red_band, green_band, blue_band, output_name=None, stretch=True):
        """
        Create an RGB composite from three different bands
        
        Args:
            red_band: Name of the band to use as red channel
            green_band: Name of the band to use as green channel
            blue_band: Name of the band to use as blue channel
            output_name: Custom name for the output file
            stretch: Apply contrast stretching to enhance visibility
        """
        cogs = self.get_available_cogs()
        
        # Check if all bands exist
        for band in [red_band, green_band, blue_band]:
            if band not in cogs:
                print(f"Band {band} not found as a COG file")
                return None
        
        if output_name is None:
            output_name = f"RGB_{red_band}_{green_band}_{blue_band}"
        
        output_path = os.path.join(self.output_directory, f"{output_name}.png")
        
        # Create RGB array
        red_data = None
        green_data = None
        blue_data = None
        
        # Read data for each channel
        with rasterio.open(cogs[red_band]) as src:
            red_data = src.read(1).astype(np.float32)
            profile = src.profile
        
        with rasterio.open(cogs[green_band]) as src:
            green_data = src.read(1).astype(np.float32)
        
        with rasterio.open(cogs[blue_band]) as src:
            blue_data = src.read(1).astype(np.float32)
        
        # Apply contrast stretching if requested
        if stretch:
            for data in [red_data, green_data, blue_data]:
                p2, p98 = np.percentile(data, (2, 98))
                data = np.clip(data, p2, p98)
                data = (data - p2) / (p98 - p2)
        
        # Stack bands to create RGB
        rgb = np.dstack((red_data, green_data, blue_data))
        
        # Normalize to 0-1 range if not already
        if rgb.max() > 1:
            rgb = rgb / rgb.max()
        
        # Create the plot
        plt.figure(figsize=(12, 12))
        plt.title(f"RGB Composite: {red_band}(R), {green_band}(G), {blue_band}(B)")
        plt.imshow(rgb)
        plt.axis('off')
        plt.tight_layout()
        
        # Save the figure
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ RGB composite saved to {output_path}")
        
        return output_path
    
    def visualize_band_combination(self, combination_name):
        """
        Visualize a predefined band combination
        
        Args:
            combination_name: Name of the combination to visualize ('natural_color', 'false_color', 'thermal')
        """
        if combination_name not in self.band_combinations:
            print(f"Combination '{combination_name}' not defined")
            return None
        
        bands = self.band_combinations[combination_name]
        return self.create_rgb_composite(
            bands[0], bands[1], bands[2], 
            output_name=combination_name
        )
    
    def compare_original_vs_cog(self, band_name, h5_file_path):
        """
        Create a side-by-side comparison of original h5 data vs COG version
        
        Args:
            band_name: Name of the band to compare
            h5_file_path: Path to the original H5 file
        """
        cogs = self.get_available_cogs()
        output_path = os.path.join(self.output_directory, f"{band_name}_comparison.png")
        
        if band_name not in cogs:
            print(f"Band {band_name} not found as a COG file")
            return None
        
        # Read original H5 data
        with h5py.File(h5_file_path, 'r') as f:
            if band_name not in f:
                print(f"Band {band_name} not found in original H5 file")
                return None
            
            original_data = f[band_name]
            
            # Handle 3D data (time, y, x)
            if len(original_data.shape) == 3:
                original_data = original_data[0, :, :]
            else:
                original_data = original_data[:, :]
        
        # Read COG data
        with rasterio.open(cogs[band_name]) as src:
            cog_data = src.read(1)
        
        # Create the comparison plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # Plot original data
        p2, p98 = np.percentile(original_data, (2, 98))
        orig_img = ax1.imshow(original_data, cmap='gray', vmin=p2, vmax=p98)
        ax1.set_title(f"Original {band_name} (H5)")
        ax1.axis('off')
        fig.colorbar(orig_img, ax=ax1)
        
        # Plot COG data
        p2, p98 = np.percentile(cog_data, (2, 98))
        cog_img = ax2.imshow(cog_data, cmap='gray', vmin=p2, vmax=p98)
        ax2.set_title(f"COG {band_name}")
        ax2.axis('off')
        fig.colorbar(cog_img, ax=ax2)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Comparison saved to {output_path}")
        
        return output_path
    
    def create_all_visualizations(self, h5_file_path):
        """
        Create all possible visualizations from the available COG files
        
        Args:
            h5_file_path: Path to the original H5 file for comparison
        """
        cogs = self.get_available_cogs()
        
        if not cogs:
            print("No COG files found to visualize")
            return {}
        
        results = {}
        
        # Create single band visualizations
        print("\nCreating single band visualizations...")
        for band_name in cogs:
            results[f"{band_name}_grayscale"] = self.visualize_single_band(band_name)
        
        # Create predefined band combinations
        print("\nCreating band combinations...")
        for combo_name in self.band_combinations:
            results[combo_name] = self.visualize_band_combination(combo_name)
        
        # Create comparisons
        print("\nCreating original vs COG comparisons...")
        for band_name in cogs:
            results[f"{band_name}_comparison"] = self.compare_original_vs_cog(band_name, h5_file_path)
        
        return results


def demo_visualization():
    """
    Demo function to test the visualization
    """
    h5_file = "data/sample.h5"
    
    if not os.path.exists(h5_file):
        print(f"❌ File {h5_file} not found!")
        return
    
    vis = INSATVisualizer()
    
    # Check for available COGs
    cogs = vis.get_available_cogs()
    if not cogs:
        print("No COG files found. Please convert bands to COG format first.")
        return
    
    print(f"Found {len(cogs)} COG files: {list(cogs.keys())}")
    
    # Create visualizations for a band
    first_band = list(cogs.keys())[0]
    print(f"\nVisualizing band: {first_band}")
    vis.visualize_single_band(first_band)
    
    # Create RGB composite if we have at least 3 bands
    if len(cogs) >= 3:
        bands = list(cogs.keys())[:3]
        print(f"\nCreating RGB composite from bands: {bands}")
        vis.create_rgb_composite(bands[0], bands[1], bands[2])
    
    # Compare original vs COG
    print(f"\nCreating comparison for {first_band}")
    vis.compare_original_vs_cog(first_band, h5_file)

if __name__ == "__main__":
    demo_visualization()

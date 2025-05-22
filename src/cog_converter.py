import h5py
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from rasterio.warp import calculate_default_transform, reproject, Resampling
import os

class INSATCOGConverter:
    def __init__(self, h5_file_path):
        self.h5_file_path = h5_file_path
        self.output_dir = "output/converted_cogs"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define the main spectral bands we want to convert
        self.spectral_bands = {
            'IMG_VIS': {'name': 'Visible', 'wavelength': '0.65μm'},
            'IMG_SWIR': {'name': 'Short Wave IR', 'wavelength': '1.625μm'},
            'IMG_MIR': {'name': 'Middle IR', 'wavelength': '3.907μm'},
            'IMG_WV': {'name': 'Water Vapor', 'wavelength': '6.866μm'},
            'IMG_TIR1': {'name': 'Thermal IR1', 'wavelength': '10.785μm'},
            'IMG_TIR2': {'name': 'Thermal IR2', 'wavelength': '11.966μm'}
        }
    
    def get_projection_info(self):
        """
        Extract projection and coordinate information from the HDF5 file
        """
        with h5py.File(self.h5_file_path, 'r') as f:
            # Get coordinate arrays
            x_coords = f['X'][:]
            y_coords = f['Y'][:]
            
            # Get projection information
            proj_info = f['Projection_Information']
            
            # Extract key projection parameters
            proj_attrs = dict(proj_info.attrs)
            
            # Calculate bounds
            x_min, x_max = float(x_coords[0]), float(x_coords[-1])
            y_min, y_max = float(y_coords[-1]), float(y_coords[0])  # Y is often flipped
            
            # Calculate pixel size
            x_res = (x_max - x_min) / len(x_coords)
            y_res = (y_max - y_min) / len(y_coords)
            
            # Create affine transform
            transform = from_bounds(x_min, y_min, x_max, y_max, 
                                  len(x_coords), len(y_coords))
            
            # Define CRS (Mercator projection)
            crs = CRS.from_proj4(f"+proj=merc +lon_0={proj_attrs['longitude_of_projection_origin'][0]} "
                               f"+datum=WGS84 +units=m +no_defs")
            
            return {
                'transform': transform,
                'crs': crs,
                'width': len(x_coords),
                'height': len(y_coords),
                'bounds': (x_min, y_min, x_max, y_max)
            }
    
    def convert_band_to_cog(self, band_name):
        """
        Convert a single spectral band to Cloud Optimized GeoTIFF
        """
        print(f"Converting {band_name} to COG...")
        
        with h5py.File(self.h5_file_path, 'r') as f:
            if band_name not in f:
                print(f"Band {band_name} not found in file!")
                return None
            
            # Read the band data
            band_data = f[band_name]
            
            # Handle 3D data (time, y, x) by taking the first time slice
            if len(band_data.shape) == 3:
                data_array = band_data[0, :, :]
            else:
                data_array = band_data[:, :]
            
            # Get projection info
            proj_info = self.get_projection_info()
            
            # Output file path
            output_path = os.path.join(self.output_dir, f"{band_name}_cog.tif")
            
            # COG creation profile
            cog_profile = {
                'driver': 'GTiff',
                'dtype': data_array.dtype,
                'width': proj_info['width'],
                'height': proj_info['height'],
                'count': 1,
                'crs': proj_info['crs'],
                'transform': proj_info['transform'],
                'tiled': True,
                'blockxsize': 512,
                'blockysize': 512,
                'compress': 'lzw',
                'interleave': 'pixel',
                'BIGTIFF': 'IF_SAFER'
            }
            
            # Write the COG
            with rasterio.open(output_path, 'w', **cog_profile) as dst:
                dst.write(data_array, 1)
                
                # Add band metadata
                dst.set_band_description(1, f"{self.spectral_bands.get(band_name, {}).get('name', band_name)}")
                
                # Add tags
                dst.update_tags(
                    BAND_NAME=band_name,
                    WAVELENGTH=self.spectral_bands.get(band_name, {}).get('wavelength', 'Unknown'),
                    SOURCE_FILE=os.path.basename(self.h5_file_path),
                    CREATED_BY='INSAT COG Converter'
                )
            
            # Add overviews for efficient zoom
            self._add_overviews(output_path)
            
            print(f"✅ Converted {band_name} -> {output_path}")
            return output_path
    
    def _add_overviews(self, file_path):
        """
        Add overviews (pyramids) to the GeoTIFF for efficient zooming
        """
        with rasterio.open(file_path, 'r+') as dst:
            # Calculate overview factors (2, 4, 8, 16)
            factors = [2, 4, 8, 16]
            dst.build_overviews(factors, Resampling.average)
            dst.update_tags(ns='rio_overview', resampling='average')
    
    def convert_all_bands(self):
        """
        Convert all main spectral bands to COG format
        """
        print("Starting COG conversion for all spectral bands...")
        print("=" * 50)
        
        converted_files = {}
        
        for band_name in self.spectral_bands.keys():
            output_path = self.convert_band_to_cog(band_name)
            if output_path:
                converted_files[band_name] = output_path
        
        print(f"\n✅ Conversion completed! {len(converted_files)} bands converted.")
        print(f"Output directory: {self.output_dir}")
        
        return converted_files
    
    def get_band_info(self):
        """
        Get information about available bands
        """
        with h5py.File(self.h5_file_path, 'r') as f:
            band_info = {}
            for band_name in self.spectral_bands.keys():
                if band_name in f:
                    data = f[band_name]
                    band_info[band_name] = {
                        'shape': data.shape,
                        'dtype': data.dtype,
                        'description': self.spectral_bands[band_name]['name'],
                        'wavelength': self.spectral_bands[band_name]['wavelength']
                    }
            return band_info

def demo_conversion():
    """
    Demo function to test the conversion
    """
    h5_file = "data/sample.h5"
    
    if not os.path.exists(h5_file):
        print(f"❌ File {h5_file} not found!")
        return
    
    # Create converter
    converter = INSATCOGConverter(h5_file)
    
    # Show band info
    print("Available bands:")
    band_info = converter.get_band_info()
    for band, info in band_info.items():
        print(f"  {band}: {info['description']} ({info['wavelength']}) - {info['shape']}")
    
    print("\n" + "="*50)
    
    # Convert first band as demo
    first_band = list(band_info.keys())[0]
    print(f"Converting sample band: {first_band}")
    converter.convert_band_to_cog(first_band)

if __name__ == "__main__":
    demo_conversion()
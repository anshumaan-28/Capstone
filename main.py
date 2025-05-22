#!/usr/bin/env python3

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from h5_reader import explore_h5_structure, get_basic_info, sample_data_preview
from cog_converter import INSATCOGConverter

def main():
    """
    Main function to explore the INSAT sample data
    """
    print("INSAT COG Demo - Data Explorer")
    print("=" * 40)
    
    # Path to sample file
    file_path = "data/sample.h5"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found!")
        print("Please make sure your sample.h5 file is in the data/ directory")
        return
    
    try:
        # Explore the file structure
        explore_h5_structure(file_path)
        
        # Get basic information
        datasets = get_basic_info(file_path)
        
        # Show sample data
        sample_data_preview(file_path)
        
        print("\n✅ File exploration completed!")
        
        # Ask user if they want to proceed with COG conversion
        print("\nNext steps:")
        print("1. Convert bands to COG format")
        print("2. Perform band manipulations")
        print("3. Visualize results")
        
        # Demo COG conversion
        choice = input("\nWould you like to convert a sample band to COG? (y/n): ").lower().strip()
        if choice == 'y':
            print("\n" + "="*50)
            print("COG CONVERSION DEMO")
            print("="*50)
            
            converter = INSATCOGConverter(file_path)
            
            # Show available bands
            band_info = converter.get_band_info()
            print("Available spectral bands:")
            for i, (band, info) in enumerate(band_info.items(), 1):
                print(f"  {i}. {band}: {info['description']} ({info['wavelength']})")
            
            # Convert first band as demo
            first_band = list(band_info.keys())[0]
            print(f"\nConverting sample band: {first_band}")
            converted_file = converter.convert_band_to_cog(first_band)
            
            if converted_file:
                file_size = os.path.getsize(converted_file) / (1024 * 1024)
                print(f"✅ COG file created: {converted_file}")
                print(f"   File size: {file_size:.2f} MB")
                print(f"   Features: Tiled, Compressed, Overviews added")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        print("Make sure the file is a valid HDF5 file")

if __name__ == "__main__":
    main()
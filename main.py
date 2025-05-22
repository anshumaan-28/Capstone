#!/usr/bin/env python3

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from h5_reader import explore_h5_structure, get_basic_info, sample_data_preview
from cog_converter import INSATCOGConverter
from visualizer import INSATVisualizer
from manipulations import INSATBandManipulator

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
        print("2. Visualize results")
        print("3. Perform band manipulations")
        
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
                
                # Ask if user wants to convert all bands
                all_choice = input("\nWould you like to convert all spectral bands? (y/n): ").lower().strip()
                if all_choice == 'y':
                    print("\nConverting all bands to COG format...")
                    converter.convert_all_bands()
        
        # Visualization step
        vis_choice = input("\nWould you like to visualize the converted bands? (y/n): ").lower().strip()
        if vis_choice == 'y':
            print("\n" + "="*50)
            print("VISUALIZATION DEMO")
            print("="*50)
            
            visualizer = INSATVisualizer()
            cogs = visualizer.get_available_cogs()
            
            if not cogs:
                print("No COG files found. Please convert bands to COG format first.")
            else:
                print(f"Found {len(cogs)} COG files: {list(cogs.keys())}")
                
                # Visualization options
                print("\nVisualization options:")
                print("1. Single band visualization")
                print("2. RGB composite")
                print("3. Predefined band combinations")
                print("4. Compare original vs COG")
                print("5. Generate all visualizations")
                
                vis_option = input("\nEnter your choice (1-5): ").strip()
                
                if vis_option == "1":
                    # Single band visualization
                    print("\nAvailable bands:")
                    for i, band in enumerate(cogs.keys(), 1):
                        print(f"{i}. {band}")
                    
                    band_idx = input("\nEnter band number to visualize: ").strip()
                    try:
                        band_name = list(cogs.keys())[int(band_idx) - 1]
                        print(f"Visualizing {band_name}...")
                        visualizer.visualize_single_band(band_name)
                    except (ValueError, IndexError):
                        print("Invalid band number")
                
                elif vis_option == "2":
                    # RGB composite
                    if len(cogs) >= 3:
                        print("\nAvailable bands:")
                        for i, band in enumerate(cogs.keys(), 1):
                            print(f"{i}. {band}")
                            
                        print("\nSelect three bands for RGB composite (red, green, blue):")
                        try:
                            r_idx = int(input("Red band number: ").strip()) - 1
                            g_idx = int(input("Green band number: ").strip()) - 1
                            b_idx = int(input("Blue band number: ").strip()) - 1
                            
                            bands = list(cogs.keys())
                            visualizer.create_rgb_composite(bands[r_idx], bands[g_idx], bands[b_idx])
                        except (ValueError, IndexError):
                            print("Invalid band number")
                    else:
                        print("Need at least 3 COG files for RGB composite")
                
                elif vis_option == "3":
                    # Predefined band combinations
                    print("\nAvailable band combinations:")
                    for i, combo in enumerate(visualizer.band_combinations.keys(), 1):
                        bands = visualizer.band_combinations[combo]
                        print(f"{i}. {combo}: {' + '.join(bands)}")
                    
                    try:
                        combo_idx = int(input("\nEnter combination number: ").strip()) - 1
                        combo_name = list(visualizer.band_combinations.keys())[combo_idx]
                        visualizer.visualize_band_combination(combo_name)
                    except (ValueError, IndexError):
                        print("Invalid combination number")
                
                elif vis_option == "4":
                    # Compare original vs COG
                    print("\nAvailable bands:")
                    for i, band in enumerate(cogs.keys(), 1):
                        print(f"{i}. {band}")
                    
                    band_idx = input("\nEnter band number to compare: ").strip()
                    try:
                        band_name = list(cogs.keys())[int(band_idx) - 1]
                        print(f"Comparing {band_name}...")
                        visualizer.compare_original_vs_cog(band_name, file_path)
                    except (ValueError, IndexError):
                        print("Invalid band number")
                
                elif vis_option == "5":
                    # Generate all visualizations
                    print("\nGenerating all possible visualizations...")
                    results = visualizer.create_all_visualizations(file_path)
                    print(f"\n✅ Generated {len(results)} visualizations in {visualizer.output_directory}")
                
                else:
                    print("Invalid option")
                
                print(f"\nVisualizations saved to: {visualizer.output_directory}")
        
        # Band manipulation step
        manip_choice = input("\nWould you like to perform band manipulations? (y/n): ").lower().strip()
        if manip_choice == 'y':
            print("\n" + "="*50)
            print("BAND MANIPULATION DEMO")
            print("="*50)
            
            manipulator = INSATBandManipulator()
            cogs = manipulator.get_available_cogs()
            
            if not cogs:
                print("No COG files found. Please convert bands to COG format first.")
            else:
                print(f"Found {len(cogs)} COG files: {list(cogs.keys())}")
                
                # Manipulation options
                print("\nManipulation options:")
                print("1. Band difference")
                print("2. Band ratio")
                print("3. Normalized difference index")
                print("4. Extract region")
                print("5. Run all manipulations")
                
                manip_option = input("\nEnter your choice (1-5): ").strip()
                
                if manip_option == "1":
                    # Band difference
                    if len(cogs) >= 2:
                        print("\nAvailable bands:")
                        for i, band in enumerate(cogs.keys(), 1):
                            print(f"{i}. {band}")
                        
                        try:
                            print("\nSelect two bands for difference (band1 - band2):")
                            band1_idx = int(input("First band number: ").strip()) - 1
                            band2_idx = int(input("Second band number: ").strip()) - 1
                            
                            bands = list(cogs.keys())
                            manipulator.band_difference(bands[band1_idx], bands[band2_idx])
                        except (ValueError, IndexError):
                            print("Invalid band number")
                    else:
                        print("Need at least 2 COG files for band difference")
                
                elif manip_option == "2":
                    # Band ratio
                    if len(cogs) >= 2:
                        print("\nAvailable bands:")
                        for i, band in enumerate(cogs.keys(), 1):
                            print(f"{i}. {band}")
                        
                        try:
                            print("\nSelect two bands for ratio (band1 / band2):")
                            band1_idx = int(input("Numerator band number: ").strip()) - 1
                            band2_idx = int(input("Denominator band number: ").strip()) - 1
                            
                            bands = list(cogs.keys())
                            manipulator.band_ratio(bands[band1_idx], bands[band2_idx])
                        except (ValueError, IndexError):
                            print("Invalid band number")
                    else:
                        print("Need at least 2 COG files for band ratio")
                
                elif manip_option == "3":
                    # Normalized difference
                    if len(cogs) >= 2:
                        print("\nAvailable bands:")
                        for i, band in enumerate(cogs.keys(), 1):
                            print(f"{i}. {band}")
                        
                        try:
                            print("\nSelect two bands for normalized difference (band1-band2)/(band1+band2):")
                            band1_idx = int(input("First band number: ").strip()) - 1
                            band2_idx = int(input("Second band number: ").strip()) - 1
                            
                            bands = list(cogs.keys())
                            manipulator.normalized_difference_index(bands[band1_idx], bands[band2_idx])
                        except (ValueError, IndexError):
                            print("Invalid band number")
                    else:
                        print("Need at least 2 COG files for normalized difference")
                
                elif manip_option == "4":
                    # Extract region
                    print("\nAvailable bands:")
                    for i, band in enumerate(cogs.keys(), 1):
                        print(f"{i}. {band}")
                    
                    try:
                        band_idx = int(input("\nEnter band number to extract region from: ").strip()) - 1
                        band_name = list(cogs.keys())[band_idx]
                        
                        # Get band dimensions
                        with rasterio.open(cogs[band_name]) as src:
                            width = src.width
                            height = src.height
                        
                        print(f"\nBand dimensions: {width}x{height}")
                        print("Enter region coordinates (pixels):")
                        
                        x_start = int(input("X start: ").strip())
                        y_start = int(input("Y start: ").strip())
                        region_width = int(input("Width: ").strip())
                        region_height = int(input("Height: ").strip())
                        
                        if (x_start < 0 or y_start < 0 or 
                            x_start + region_width > width or 
                            y_start + region_height > height):
                            print("Invalid region coordinates")
                        else:
                            manipulator.extract_region(band_name, x_start, y_start, region_width, region_height)
                    except (ValueError, IndexError):
                        print("Invalid input")
                
                elif manip_option == "5":
                    # Run all manipulations
                    print("\nRunning all band manipulations...")
                    if len(cogs) >= 2:
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
                    else:
                        print("Need at least 2 COG files for band arithmetic operations")
                    
                    # Extract region from first band
                    if cogs:
                        first_band = list(cogs.keys())[0]
                        print(f"\nExtracting region from {first_band}...")
                        
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
                
                else:
                    print("Invalid option")
                
                print(f"\nManipulations saved to: {manipulator.output_directory}")
        
        print("\n" + "="*50)
        print("INSAT COG DEMO COMPLETED")
        print("=" * 50)
        print("\nSummary:")
        print("✓ Analyzed sample INSAT H5 data structure")
        print("✓ Converted bands to Cloud Optimized GeoTIFFs")
        print("✓ Created visualizations of the data")
        print("✓ Performed band manipulations and analyses")
        print("\nOutput directories:")
        print(f"- Converted COGs: {os.path.abspath('output/converted_cogs')}")
        print(f"- Visualizations: {os.path.abspath('output/visualizations')}")
        print(f"- Manipulations: {os.path.abspath('output/manipulations')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("Make sure the file is a valid HDF5 file")

if __name__ == "__main__":
    main()
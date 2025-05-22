import h5py
import numpy as np
import os

def explore_h5_structure(file_path):
    """
    Explore and print the structure of an HDF5 file
    """
    print(f"Exploring: {file_path}")
    print("=" * 50)
    
    with h5py.File(file_path, 'r') as f:
        print(f"File keys: {list(f.keys())}")
        print("\nDetailed structure:")
        
        def print_structure(name, obj):
            indent = "  " * name.count('/')
            if isinstance(obj, h5py.Dataset):
                print(f"{indent}{name} (Dataset): shape={obj.shape}, dtype={obj.dtype}")
                # Print attributes if any
                if obj.attrs:
                    for attr_name, attr_value in obj.attrs.items():
                        print(f"{indent}  - {attr_name}: {attr_value}")
            elif isinstance(obj, h5py.Group):
                print(f"{indent}{name} (Group): {len(obj.keys())} items")
                # Print group attributes if any
                if obj.attrs:
                    for attr_name, attr_value in obj.attrs.items():
                        print(f"{indent}  - {attr_name}: {attr_value}")
        
        f.visititems(print_structure)

def get_basic_info(file_path):
    """
    Get basic information about the HDF5 file
    """
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
    print(f"\nFile size: {file_size:.2f} MB")
    
    with h5py.File(file_path, 'r') as f:
        # Try to find datasets that look like image bands
        datasets = []
        
        def find_datasets(name, obj):
            if isinstance(obj, h5py.Dataset):
                datasets.append((name, obj.shape, obj.dtype))
        
        f.visititems(find_datasets)
        
        print(f"\nFound {len(datasets)} datasets:")
        for name, shape, dtype in datasets:
            print(f"  {name}: {shape} ({dtype})")
        
        return datasets

def sample_data_preview(file_path, dataset_name="IMG_VIS", sample_size=5):
    """
    Show a small sample of data from a dataset
    """
    with h5py.File(file_path, 'r') as f:
        # Default to visible band for preview
        if dataset_name in f:
            data = f[dataset_name]
            print(f"\nSample data from '{dataset_name}':")
            print(f"Shape: {data.shape}")
            
            # Show a small sample
            if len(data.shape) == 3:
                sample = data[0, :sample_size, :sample_size]  # First band
                data_array = data[0, :, :]  # Get 2D array for stats
            elif len(data.shape) == 2:
                sample = data[:sample_size, :sample_size]
                data_array = data[:, :]
            else:
                sample = data.flat[:sample_size]
                data_array = data[:]
            
            print(f"Sample values:\n{sample}")
            print(f"Data range: {np.min(data_array)} to {np.max(data_array)}")
            
            # Show some key bands info
            bands_info = {
                'IMG_VIS': 'Visible (0.65μm)',
                'IMG_SWIR': 'Short Wave IR (1.625μm)', 
                'IMG_MIR': 'Middle IR (3.907μm)',
                'IMG_WV': 'Water Vapor (6.866μm)',
                'IMG_TIR1': 'Thermal IR1 (10.785μm)',
                'IMG_TIR2': 'Thermal IR2 (11.966μm)'
            }
            
            print(f"\nAvailable spectral bands:")
            for band, desc in bands_info.items():
                if band in f:
                    shape = f[band].shape
                    print(f"  {band}: {desc} - {shape}")
        else:
            print(f"Dataset '{dataset_name}' not found")

if __name__ == "__main__":
    # Test with sample file
    file_path = "../data/sample.h5"
    
    if os.path.exists(file_path):
        explore_h5_structure(file_path)
        datasets = get_basic_info(file_path)
        sample_data_preview(file_path)
    else:
        print(f"File not found: {file_path}")
        print("Please make sure sample.h5 is in the data/ directory")
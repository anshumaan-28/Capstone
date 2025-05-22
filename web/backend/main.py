from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sys
import os
from pathlib import Path
import json

# Add the parent directory to Python path to import our existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.h5_reader import explore_h5_structure, get_basic_info
from src.cog_converter import INSATCOGConverter
from src.visualizer import INSATVisualizer
from src.manipulations import INSATBandManipulator

app = FastAPI(title="INSAT COG Explorer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our components
h5_file_path = "../../data/Sample.h5"
converter = INSATCOGConverter(h5_file_path)
visualizer = INSATVisualizer()
manipulator = INSATBandManipulator()

@app.get("/api/bands")
async def get_bands():
    """Get available spectral bands information"""
    try:
        band_info = converter.get_band_info()
        return {
            "status": "success",
            "data": {
                name: {
                    "description": info["description"],
                    "wavelength": info["wavelength"],
                    "dimensions": "1616×1737"  # You might want to get this dynamically
                }
                for name, info in band_info.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/convert/{band_name}")
async def convert_band(band_name: str):
    """Convert a specific band to COG format"""
    try:
        # Print debugging information
        print(f"Converting band: {band_name}")
        print(f"H5 file path: {converter.h5_file_path}")
        print(f"Output directory: {converter.output_dir}")
        print(f"Output directory exists: {os.path.exists(converter.output_dir)}")
        
        result = converter.convert_band_to_cog(band_name)
        
        print(f"Conversion result: {result}")
        print(f"File exists: {os.path.exists(result) if result else False}")
        
        # Check if the COG file is in the output directory
        expected_cog_file = os.path.join(converter.output_dir, f"{band_name}_cog.tif")
        print(f"Expected COG file: {expected_cog_file}")
        print(f"Expected file exists: {os.path.exists(expected_cog_file)}")
        
        return {
            "status": "success",
            "data": {
                "file_path": result,
                "message": f"Successfully converted {band_name} to COG format"
            }
        }
    except Exception as e:
        print(f"ERROR in conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visualize/{band_name}")
async def visualize_band(band_name: str):
    """Get visualization for a specific band"""
    try:
        output_path = visualizer.visualize_single_band(band_name)
        if output_path and os.path.exists(output_path):
            return FileResponse(output_path)
        raise HTTPException(status_code=404, detail="Visualization not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/visualize/rgb")
async def create_rgb_composite(bands: dict):
    """Create RGB composite from selected bands"""
    try:
        output_path = visualizer.create_rgb_composite(
            bands["red"], bands["green"], bands["blue"]
        )
        if output_path and os.path.exists(output_path):
            return FileResponse(output_path)
        raise HTTPException(status_code=404, detail="RGB composite not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/manipulate/difference")
async def calculate_difference(bands: dict):
    """Calculate difference between two bands"""
    try:
        # Print debugging info
        print(f"Calculating difference for bands: {bands}")
        print(f"Available COGs: {manipulator.get_available_cogs()}")
        
        output_path = manipulator.band_difference(bands["band1"], bands["band2"])
        
        print(f"Output path: {output_path}")
        print(f"Output file exists: {os.path.exists(output_path) if output_path else False}")
        
        if output_path and os.path.exists(output_path):
            vis_path = f"{os.path.splitext(output_path)[0]}_vis.png"
            print(f"Visualization path: {vis_path}")
            print(f"Visualization exists: {os.path.exists(vis_path)}")
            
            return {
                "status": "success",
                "data": {
                    "visualization": f"/api/files/manipulations/{os.path.basename(vis_path)}",
                    "message": "Band difference calculated successfully"
                }
            }
        raise HTTPException(status_code=404, detail="Result not found")
    except Exception as e:
        print(f"ERROR in difference calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/manipulate/ratio")
async def calculate_ratio(bands: dict):
    """Calculate ratio between two bands"""
    try:
        # Print debugging info
        print(f"Calculating ratio for bands: {bands}")
        print(f"Available COGs: {manipulator.get_available_cogs()}")
        print(f"Output directory: {manipulator.output_directory}")
        print(f"Output directory exists: {os.path.exists(manipulator.output_directory)}")
        
        output_path = manipulator.band_ratio(bands["numerator"], bands["denominator"])
        
        print(f"Output path: {output_path}")
        print(f"Output file exists: {os.path.exists(output_path) if output_path else False}")
        
        if output_path and os.path.exists(output_path):
            vis_path = f"{os.path.splitext(output_path)[0]}_vis.png"
            print(f"Visualization path: {vis_path}")
            print(f"Visualization exists: {os.path.exists(vis_path)}")
            
            return {
                "status": "success",
                "data": {
                    "visualization": f"/api/files/manipulations/{os.path.basename(vis_path)}",
                    "message": "Band ratio calculated successfully"
                }
            }
        raise HTTPException(status_code=404, detail="Result not found")
    except Exception as e:
        print(f"ERROR in ratio calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{directory}/{filename}")
async def serve_file(directory: str, filename: str):
    """Serve files from output directories"""
    base_path = Path("../../output")
    file_path = base_path / directory / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path))

@app.get("/api/statistics/{band_name}")
async def get_band_statistics(band_name: str):
    """Get statistical information for a band"""
    try:
        data, _ = manipulator.load_band_data(band_name)
        if data is None:
            raise HTTPException(status_code=404, detail="Band data not found")
        
        stats = {
            "minimum": float(data.min()),
            "maximum": float(data.max()),
            "mean": float(data.mean()),
            "std": float(data.std())
        }
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
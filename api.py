import os
import tempfile
import base64
import zipfile
import shutil
import urllib.request
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from run import run_change_detection

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def download_and_setup_checkpoints():
    """
    Download pretrained weights if they don't exist in checkpoints/ChangeFormer_DSIFN
    """
    checkpoint_dir = Path("checkpoints/ChangeFormer_DSIFN")
    checkpoint_file = checkpoint_dir / "best_ckpt.pt"
    
    # Check if checkpoint already exists
    if checkpoint_file.exists():
        print(f"Checkpoints already exist at {checkpoint_dir}")
        return
    
    print("Checkpoints not found. Downloading pretrained weights...")
    
    # Create checkpoint directory
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # URL for pretrained weights
    checkpoint_url = "https://github.com/wgcban/ChangeFormer/releases/download/v0.1.0/CD_ChangeFormerV6_DSIFN_b16_lr0.00006_adamw_train_test_200_linear_ce_multi_train_True_multi_infer_False_shuffle_AB_False_embed_dim_256.zip"
    
    # Download zip file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        zip_path = tmp_file.name
        print(f"Downloading from {checkpoint_url}...")
        urllib.request.urlretrieve(checkpoint_url, zip_path)
        print("Download complete. Extracting...")
    
    # Extract zip file
    extract_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the checkpoint files in subdirectories
        # Look for best_ckpt.pt in any subdirectory
        checkpoint_files = ['best_ckpt.pt', 'last_ckpt.pt', 'log.txt', 'val_acc.npy', 'train_acc.npy']
        
        found_checkpoint_dir = None
        for root, dirs, files in os.walk(extract_dir):
            if 'best_ckpt.pt' in files:
                found_checkpoint_dir = root
                break
        
        if found_checkpoint_dir is None:
            raise FileNotFoundError("Could not find checkpoint files in downloaded zip")
        
        print(f"Found checkpoint files in: {found_checkpoint_dir}")
        
        # Copy checkpoint files to the target directory
        for filename in checkpoint_files:
            src_path = os.path.join(found_checkpoint_dir, filename)
            if os.path.exists(src_path):
                dst_path = checkpoint_dir / filename
                shutil.copy2(src_path, dst_path)
                print(f"Copied {filename} to {checkpoint_dir}")
            else:
                print(f"Warning: {filename} not found in extracted files")
        
        print(f"Checkpoints successfully set up at {checkpoint_dir}")
        
    finally:
        # Clean up temporary files
        os.unlink(zip_path)
        shutil.rmtree(extract_dir, ignore_errors=True)

@app.on_event("startup")
async def startup_event():
    """Download checkpoints on startup if they don't exist"""
    download_and_setup_checkpoints()

@app.post("/change-detection")
async def change_detection(
    images_a: List[UploadFile] = File(...), 
    images_b: List[UploadFile] = File(...),
    img_size: int = Form(1024, description="Image size for processing"),
    n: int = Form(2, description="Number of crops per side (total crops = n x n)"),
    combine_masks: bool = Form(True, description="Combine cropped masks back into full images"),
    calls_nb: int = Form(2, description="Number of model calls with decreasing img_size"),
    crop_image: bool = Form(True, description="Crop images for calls > 1")
):
    """
    Crop images in data_dir into n x n square pieces and run change detection.
    """
    if len(images_a) != len(images_b):
        return JSONResponse(
            status_code=400,
            content={"error": "Number of images in A and B must be equal"}
        )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create directory structure
        a_dir = os.path.join(temp_dir, 'A')
        b_dir = os.path.join(temp_dir, 'B')
        list_dir = os.path.join(temp_dir, 'list')
        os.makedirs(a_dir)
        os.makedirs(b_dir)
        os.makedirs(list_dir)

        # Save uploaded images
        filenames = []
        for i in range(len(images_a)):
            filename = images_a[i].filename
            filenames.append(filename)
            with open(os.path.join(a_dir, filename), 'wb') as f:
                f.write(await images_a[i].read())
            with open(os.path.join(b_dir, filename), 'wb') as f:
                f.write(await images_b[i].read())

        # Create list/demo.txt
        with open(os.path.join(list_dir, 'demo.txt'), 'w') as f:
            for name in filenames:
                f.write(name + '\n')

        # Run change detection with provided values
        output_folder = os.path.join(temp_dir, 'predicted')
        run_change_detection(
            data_dir=temp_dir,
            calls_nb=calls_nb,
            img_size=img_size,
            crop_image=crop_image,
            output_folder=output_folder,
            project_name='ChangeFormer_DSIFN',
            checkpoint_name='best_ckpt.pt',
            gpu_ids='0',
            n=n
        )

        # Prepare results with base64 encoded images
        results = []
        for filename in filenames:
            base = os.path.splitext(filename)[0]
            mask_path = os.path.join(output_folder, f"{base}.png")
            color_mask_path = os.path.join(output_folder, f"{base}_color.png")
            overlay_a_path = os.path.join(output_folder, f"{base}_A_overlay.png")
            overlay_b_path = os.path.join(output_folder, f"{base}_B_overlay.png")

            result_item = {
                "filename": base,
                "mask": None,
                "color_mask": None,
                "overlay_a": None,
                "overlay_b": None
            }

            # Encode images to base64
            if os.path.exists(mask_path):
                with open(mask_path, 'rb') as f:
                    result_item["mask"] = base64.b64encode(f.read()).decode('utf-8')
            
            if os.path.exists(color_mask_path):
                with open(color_mask_path, 'rb') as f:
                    result_item["color_mask"] = base64.b64encode(f.read()).decode('utf-8')
            
            if os.path.exists(overlay_a_path):
                with open(overlay_a_path, 'rb') as f:
                    result_item["overlay_a"] = base64.b64encode(f.read()).decode('utf-8')
            
            if os.path.exists(overlay_b_path):
                with open(overlay_b_path, 'rb') as f:
                    result_item["overlay_b"] = base64.b64encode(f.read()).decode('utf-8')

            results.append(result_item)

        return JSONResponse(content={"results": results})


# uvicorn api:app --reload  
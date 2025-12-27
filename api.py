import os
import tempfile
import base64
import zipfile
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List
from run import run_change_detection

app = FastAPI()

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
        return {"error": "Number of images in A and B must be equal"}
    
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

        # Create a zip file with all outputs
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in filenames:
                base = os.path.splitext(filename)[0]
                mask_path = os.path.join(output_folder, f"{base}.png")
                color_mask_path = os.path.join(output_folder, f"{base}_color.png")
                overlay_a_path = os.path.join(output_folder, f"{base}_A_overlay.png")
                overlay_b_path = os.path.join(output_folder, f"{base}_B_overlay.png")

                if os.path.exists(mask_path):
                    zip_file.write(mask_path, f"{base}_mask.png")
                if os.path.exists(color_mask_path):
                    zip_file.write(color_mask_path, f"{base}_color_mask.png")
                if os.path.exists(overlay_a_path):
                    zip_file.write(overlay_a_path, f"{base}_overlay_a.png")
                if os.path.exists(overlay_b_path):
                    zip_file.write(overlay_b_path, f"{base}_overlay_b.png")

        zip_buffer.seek(0)

        return StreamingResponse(zip_buffer, media_type='application/zip', headers={"Content-Disposition": "attachment; filename=change_detection_results.zip"})
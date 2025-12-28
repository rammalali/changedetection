import argparse
from PIL import Image
import os
import numpy as np
import cv2

import utils
import torch
from models.basic_model import CDEvaluator
from align import align_images

def run_inference(data_dir, args, gpu_ids):
    # Set up device
    args.gpu_ids = gpu_ids
    utils.get_device(args)
    device = torch.device("cuda:%s" % args.gpu_ids[0]
                          if torch.cuda.is_available() and len(args.gpu_ids)>0
                        else "cpu")
    args.checkpoint_dir = os.path.join(args.checkpoint_root, args.project_name)
    os.makedirs(args.output_folder, exist_ok=True)

    # Set dataset to ImageDataset for custom data_dir
    args.dataset = 'ImageDataset'

    data_loader = utils.get_loader(args.data_name, img_size=args.img_size,
                                   batch_size=args.batch_size,
                                   split=args.split, is_train=False,
                                   dataset=args.dataset, root_dir=data_dir)

    model = CDEvaluator(args)
    model.load_checkpoint(args.checkpoint_name)
    model.eval()

    masks = {}
    for i, batch in enumerate(data_loader):
        name = batch['name']
        if isinstance(name, list):
            name = name[0]
        print('process: %s' % name)
        score_map = model._forward_pass(batch)
        # Assuming score_map is (1,1,H,W), squeeze to (H,W)
        mask = score_map.squeeze().cpu().numpy().astype(np.float32)
        masks[name] = mask

    return masks

def main():
    parser = argparse.ArgumentParser(description='Crop images in data_dir into n x n square pieces and run change detection.')
    parser.add_argument('--data_dir', default='data_dir', help='Data directory with A/, B/, list/demo.txt')
    parser.add_argument('--output_folder', default='predicted', help='Output folder for predictions')
    parser.add_argument('--n', type=int, default=2, help='Number of crops per side (total crops = n x n)')
    parser.add_argument('--combine_masks', action='store_true', default=True, help='Combine cropped masks back into full images')
    parser.add_argument('--calls_nb', type=int, default=2, help='Number of model calls with decreasing img_size')
    parser.add_argument('--crop_image', action='store_true',default=True, help='Crop images for calls > 1')
    
    # Model arguments
    parser.add_argument('--project_name', default='ChangeFormer_DSIFN', type=str)
    parser.add_argument('--gpu_ids', type=str, default='0', help='gpu ids: e.g. 0  0,1,2, 0,2. use -1 for CPU')
    parser.add_argument('--checkpoint_root', default='checkpoints/', type=str)
    parser.add_argument('--num_workers', default=12, type=int)
    parser.add_argument('--dataset', default='CDDataset', type=str, choices=['CDDataset', 'ImageDataset'])
    parser.add_argument('--data_name', default='quick_start_DSIFN', type=str)
    parser.add_argument('--batch_size', default=1, type=int)
    parser.add_argument('--split', default="demo", type=str)
    parser.add_argument('--img_size', default=1024, type=int)
    parser.add_argument('--n_class', default=2, type=int)
    parser.add_argument('--embed_dim', default=256, type=int)
    parser.add_argument('--net_G', default='ChangeFormerV6', type=str,
                        help='ChangeFormerV6 | CD_SiamUnet_diff | SiamUnet_conc | Unet | DTCDSCN | base_resnet18 | base_transformer_pos_s4_dd8 | base_transformer_pos_s4_dd8_dedim8|')
    parser.add_argument('--checkpoint_name', default='best_ckpt.pt', type=str)
    
    args = parser.parse_args()

    run_change_detection(args.data_dir, args.calls_nb, args.img_size, args.crop_image, args.output_folder, args.project_name, args.checkpoint_name, args.gpu_ids)

def run_change_detection(data_dir, calls_nb=1, img_size=512, crop_image=False, output_folder='predicted', project_name='ChangeFormer_DSIFN', checkpoint_name='best_ckpt.pt', gpu_ids='0', n=2):
    # Set up args
    class Args:
        pass
    args = Args()
    args.data_dir = data_dir
    args.output_folder = output_folder
    args.project_name = project_name
    args.checkpoint_name = checkpoint_name
    args.gpu_ids = gpu_ids
    args.checkpoint_root = 'checkpoints/'
    args.num_workers = 12
    args.dataset = 'ImageDataset'
    args.data_name = 'quick_start_DSIFN'
    args.batch_size = 1
    args.split = "demo"
    args.n_class = 2
    args.embed_dim = 256
    args.net_G = 'ChangeFormerV6'

    # Read the list
    list_path = os.path.join(data_dir, 'list', 'demo.txt')
    if not os.path.exists(list_path):
        print(f"Error: {list_path} not found")
        return

    with open(list_path, 'r') as f:
        image_names = [line.strip() for line in f if line.strip()]

    # Align images
    aligned_data_dir = f"{data_dir}_aligned"
    a_dir = os.path.join(aligned_data_dir, 'A')
    b_dir = os.path.join(aligned_data_dir, 'B')
    list_dir = os.path.join(aligned_data_dir, 'list')
    os.makedirs(a_dir, exist_ok=True)
    os.makedirs(b_dir, exist_ok=True)
    os.makedirs(list_dir, exist_ok=True)

    for image_name in image_names:
        img_a_path = os.path.join(data_dir, 'A', image_name)
        img_b_path = os.path.join(data_dir, 'B', image_name)
        if os.path.exists(img_a_path) and os.path.exists(img_b_path):
            print(f"Aligning {image_name}")
            img_a_aligned, img_b_aligned = align_images(img_a_path, img_b_path)
            # Convert BGR to RGB for PIL
            img_a_rgb = cv2.cvtColor(img_a_aligned, cv2.COLOR_BGR2RGB)
            img_b_rgb = cv2.cvtColor(img_b_aligned, cv2.COLOR_BGR2RGB)
            img_a_pil = Image.fromarray(img_a_rgb)
            img_b_pil = Image.fromarray(img_b_rgb)
            img_a_pil.save(os.path.join(a_dir, image_name))
            img_b_pil.save(os.path.join(b_dir, image_name))

    # Copy the list
    with open(os.path.join(list_dir, 'demo.txt'), 'w') as f:
        for name in image_names:
            f.write(name + '\n')

    # Use aligned data
    data_dir = aligned_data_dir

    # Get original sizes from aligned
    original_sizes = {}
    for image_name in image_names:
        img_path = os.path.join(data_dir, 'A', image_name)
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                original_sizes[image_name] = img.size[::-1]  # (h, w)

    os.makedirs(output_folder, exist_ok=True)

    all_masks = {}  # name -> list of masks

    for call in range(1, calls_nb + 1):
        current_img_size = img_size // (2 ** (call - 1))
        args.img_size = current_img_size
        print(f"Call {call}: img_size = {current_img_size}")

        if call == 1 or not crop_image:
            # Run on full images
            masks = run_inference(data_dir, args, gpu_ids)
            for name, mask in masks.items():
                if name in original_sizes:
                    h, w = original_sizes[name]
                    mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)
                if name not in all_masks:
                    all_masks[name] = []
                all_masks[name].append(mask)
        else:
            # Crop into pieces where each piece size equals current_img_size
            cropped_data_dir = f"{data_dir}_cropped_{call}"
            a_dir = os.path.join(cropped_data_dir, 'A')
            b_dir = os.path.join(cropped_data_dir, 'B')
            list_dir = os.path.join(cropped_data_dir, 'list')
            os.makedirs(a_dir, exist_ok=True)
            os.makedirs(b_dir, exist_ok=True)
            os.makedirs(list_dir, exist_ok=True)

            crop_names = []
            original_sizes = {}
            for image_name in image_names:
                img_before_path = os.path.join(data_dir, 'A', image_name)
                img_after_path = os.path.join(data_dir, 'B', image_name)

                if not os.path.exists(img_before_path) or not os.path.exists(img_after_path):
                    continue

                img_before = Image.open(img_before_path)
                img_after = Image.open(img_after_path)
                width, height = img_before.size

                if width != height:
                    continue

                # Calculate number of crops per side based on current_img_size
                # Each piece should be current_img_size
                crops_per_side = width // current_img_size
                if crops_per_side < 1:
                    crops_per_side = 1
                crop_size = current_img_size
                
                base_name = os.path.splitext(image_name)[0]
                original_sizes[image_name] = (height, width)  # (h, w)

                for j in range(crops_per_side):
                    for i in range(crops_per_side):
                        left = i * crop_size
                        upper = j * crop_size
                        right = min(left + crop_size, width)
                        lower = min(upper + crop_size, height)

                        crop_before = img_before.crop((left, upper, right, lower))
                        crop_after = img_after.crop((left, upper, right, lower))

                        crop_name = f"{base_name}_{j*crops_per_side + i + 1}.png"
                        crop_names.append(crop_name)

                        crop_before.save(os.path.join(a_dir, crop_name))
                        crop_after.save(os.path.join(b_dir, crop_name))

            # Create list/demo.txt
            with open(os.path.join(list_dir, 'demo.txt'), 'w') as f:
                for name in crop_names:
                    f.write(name + '\n')

            # Run inference on cropped
            masks = run_inference(cropped_data_dir, args, gpu_ids)

            # Combine crops back
            combined_masks = {}
            for original in image_names:
                if original not in original_sizes:
                    continue
                base = os.path.splitext(original)[0]
                full_h, full_w = original_sizes[original]
                
                # Calculate number of crops per side based on current_img_size
                crops_per_side = full_w // current_img_size
                if crops_per_side < 1:
                    crops_per_side = 1
                crop_size = current_img_size
                total_crops = crops_per_side * crops_per_side
                
                crop_bases = [f"{base}_{k+1}" for k in range(total_crops)]
                crop_masks = []
                for cb in crop_bases:
                    crop_name = cb + '.png'
                    if crop_name in masks:
                        mask = masks[crop_name]
                        mask = cv2.resize(mask, (crop_size, crop_size), interpolation=cv2.INTER_LINEAR)
                        crop_masks.append(mask)
                
                if len(crop_masks) == total_crops:
                    full_mask = np.zeros((full_h, full_w), dtype=np.float32)
                    for idx, mask in enumerate(crop_masks):
                        i = idx // crops_per_side
                        j = idx % crops_per_side
                        start_h = i * crop_size
                        start_w = j * crop_size
                        end_h = min((i + 1) * crop_size, full_h)
                        end_w = min((j + 1) * crop_size, full_w)
                        full_mask[start_h:end_h, start_w:end_w] = mask[:end_h-start_h, :end_w-start_w]
                    combined_masks[original] = full_mask

            for name, mask in combined_masks.items():
                if name not in all_masks:
                    all_masks[name] = []
                all_masks[name].append(mask)

    # Combine masks with detection levels
    for name in all_masks:
        masks_list = all_masks[name]
        if masks_list:
            h, w = masks_list[0].shape
            # Count detections per pixel
            detection_count = np.zeros((h, w), dtype=int)
            for mask in masks_list:
                detection_count += (mask > 0.5).astype(int)
            
            # Assign levels: 0=black, 1=50% white, 2=100% white
            bw_mask = np.zeros((h, w), dtype=np.uint8)
            bw_mask[detection_count == 1] = 128  # 50% white
            bw_mask[detection_count >= 2] = 255  # 100% white
            
            mask_img = Image.fromarray(bw_mask, 'L')
            mask_path = os.path.join(output_folder, f"{os.path.splitext(name)[0]}.png")
            mask_img.save(mask_path)
            print(f"Saved BW mask: {mask_path}")

            # Also save color mask
            colors = [(0, 255, 0), (0, 0, 255)]  # green for call 1, blue for call 2
            color_mask = np.zeros((h, w, 3), dtype=np.float32)
            for i, mask in enumerate(masks_list):
                color = np.array(colors[i % len(colors)], dtype=np.float32) / 255.0
                for c in range(3):
                    color_mask[..., c] += mask * color[c]
            color_mask = np.clip(color_mask, 0, 1)
            color_mask_uint8 = (color_mask * 255).astype(np.uint8)
            color_mask_img = Image.fromarray(color_mask_uint8, 'RGB')
            color_mask_path = os.path.join(output_folder, f"{os.path.splitext(name)[0]}_color.png")
            color_mask_img.save(color_mask_path)
            print(f"Saved color mask: {color_mask_path}")

    # Create overlays
    create_overlays(data_dir, output_folder, image_names)

def create_overlays(data_dir, output_folder, image_names):
    for image_name in image_names:
        base = os.path.splitext(image_name)[0]
        mask_path = os.path.join(output_folder, f"{base}.png")
        
        if not os.path.exists(mask_path):
            print(f"Warning: Mask {mask_path} not found, skipping overlay")
            continue
        
        # Load images
        a_path = os.path.join(data_dir, 'A', image_name)
        b_path = os.path.join(data_dir, 'B', image_name)
        
        if not os.path.exists(a_path) or not os.path.exists(b_path):
            print(f"Warning: A or B image not found for {image_name}, skipping overlay")
            continue
        
        img_a = Image.open(a_path).convert('RGB')
        img_b = Image.open(b_path).convert('RGB')
        mask_img = Image.open(mask_path).convert('L')
        mask_array = np.array(mask_img).astype(np.float32) / 255.0  # 0-1
        
        # Create overlays
        overlay_a = create_overlay(img_a, mask_array)
        overlay_b = create_overlay(img_b, mask_array)
        
        # Save overlays
        overlay_a_path = os.path.join(output_folder, f"{base}_A_overlay.png")
        overlay_b_path = os.path.join(output_folder, f"{base}_B_overlay.png")
        overlay_a.save(overlay_a_path)
        overlay_b.save(overlay_b_path)
        print(f"Created overlays: {overlay_a_path}, {overlay_b_path}")

def create_overlay(image, mask_array):
    # mask_array is np.array (H,W) 0-1
    # Resize mask to match image size if necessary
    if mask_array.shape[:2] != image.size[::-1]:
        mask_pil = Image.fromarray((mask_array * 255).astype(np.uint8), 'L')
        mask_pil = mask_pil.resize(image.size, Image.NEAREST)
        mask_array = np.array(mask_pil).astype(np.float32) / 255.0
    
    # Convert mask to RGBA for overlay
    mask_rgba_array = np.zeros((image.size[1], image.size[0], 4), dtype=np.uint8)
    mask_rgba_array[..., :3] = [255, 0, 0]  # Red
    mask_rgba_array[..., 3] = (mask_array * 255).astype(np.uint8)  # Alpha based on mask value
    
    mask_overlay = Image.fromarray(mask_rgba_array, 'RGBA')
    
    # Composite overlay on image
    return Image.alpha_composite(image.convert('RGBA'), mask_overlay)

if __name__ == '__main__':
    main()
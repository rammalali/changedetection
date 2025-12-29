from lightglue.light_glue.lightglue import LightGlue, SuperPoint, DISK, SIFT, ALIKED, DoGHardNet
from lightglue.light_glue.lightglue.utils import load_image, rbd

import numpy as np
import cv2
import torch
import os
import argparse


def align_images(img1: str, img2: str):
    # -----------------------------
    # Helper function
    # -----------------------------
    def torch_to_cv_u8(img_t: torch.Tensor) -> np.ndarray:
        # img_t: (3,H,W), float [0,1]
        img = (img_t.permute(1, 2, 0).detach().cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img

    # --- Detect device (GPU if available, else CPU) ---
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if device.type == 'cpu':
        print("⚠️  GPU not available, using CPU for image alignment (this will be slower)")

    # --- extractor & matcher (DISK example) ---
    extractor = DISK(max_num_keypoints=2048).eval().to(device)
    matcher = LightGlue(features='disk').eval().to(device)

    # --- load images ---
    image0 = load_image(img1).to(device)
    image1 = load_image(img2).to(device)

    # --- extract features ---
    feats0 = extractor.extract(image0)
    feats1 = extractor.extract(image1)

    # --- match ---
    matches01 = matcher({'image0': feats0, 'image1': feats1})

    # remove batch dimension
    feats0, feats1, matches01 = [rbd(x) for x in [feats0, feats1, matches01]]

    score_thresh = 0.85

    scores  = matches01['scores']     # (K,)
    matches = matches01['matches']    # (K, 2)

    mask = scores > score_thresh

    matches = matches[mask]
    scores  = scores[mask]

    # update matches01 so viz2d uses filtered matches
    matches01['matches'] = matches
    matches01['scores']  = scores

    # matched keypoints
    points0 = feats0['keypoints'][matches[:, 0]]
    points1 = feats1['keypoints'][matches[:, 1]]

    print(f"Kept {len(matches)} matches with score > {score_thresh}")

    # -----------------------------
    # 1) Prepare matched points
    # -----------------------------
    pts0 = points0.detach().cpu().numpy().astype(np.float32)  # in image0 coords
    pts1 = points1.detach().cpu().numpy().astype(np.float32)  # in image1 coords

    if len(pts0) < 10:
        print(f"Not enough matches for homography: {len(pts0)}. Skipping alignment.")
        # Return original images
        img0_cv = torch_to_cv_u8(image0)
        img1_cv = torch_to_cv_u8(image1)
        return img0_cv, img1_cv

    # -----------------------------
    # 2) Estimate homography H: image1 -> image0
    # -----------------------------
    H, inlier_mask = cv2.findHomography(pts1, pts0, cv2.RANSAC, 5.0)

    if H is None:
        print("Homography estimation failed. Using original images.")
        img0_cv = torch_to_cv_u8(image0)
        img1_cv = torch_to_cv_u8(image1)
        return img0_cv, img1_cv

    inliers = int(inlier_mask.sum()) if inlier_mask is not None else 0
    print("Homography inliers:", inliers, "/", len(pts0))

    # -----------------------------
    # 3) Convert torch images to OpenCV uint8
    # -----------------------------
    img0_cv = torch_to_cv_u8(image0)
    img1_cv = torch_to_cv_u8(image1)

    h0, w0 = img0_cv.shape[:2]
    h1, w1 = img1_cv.shape[:2]

    # -----------------------------
    # 4) Warp image1 to image0's coordinate system
    # -----------------------------
    img1_warp = cv2.warpPerspective(img1_cv, H, (w0, h0), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))

    # -----------------------------
    # 5) Create validity mask for warped image1 (where pixels are not black)
    # -----------------------------
    mask = (img1_warp.sum(axis=2) > 0).astype(np.uint8) * 255

    # -----------------------------
    # 6) Apply mask to img0 to remove areas not present in warped img1
    # -----------------------------
    img0_aligned = cv2.bitwise_and(img0_cv, img0_cv, mask=mask)
    img1_aligned = img1_warp  # already has black areas

    print("Aligned image sizes:", img0_aligned.shape, img1_aligned.shape)

    return img0_aligned, img1_aligned
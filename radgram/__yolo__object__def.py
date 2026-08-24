import cv2 
import numpy as np
from rembg import remove, new_session 
from PIL import Image # For accessory/FX layering if needed
import os
import time

# --- CONFIGURATION ---
BG_IMAGE_PATH = 'custom_bg.png' # Static image background
OUTPUT_FILE = 'cinewiz_output.mp4'
YOLO_CONFIG = 'yolov3.cfg'       # Path to YOLO config file
YOLO_WEIGHTS = 'yolov3.weights'   # Path to YOLO weights file
YOLO_CLASSES = 'coco.names'      # Path to COCO class names file

# rembg session (pre-trained model)
REMBG_SESSION = new_session('u2net') 

# --- YOLO Detection Setup (Essential for Accessory/Clothes Change) ---
try:
    net = cv2.dnn.readNetFromDarknet(YOLO_CONFIG, YOLO_WEIGHTS)
    with open(YOLO_CLASSES, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    # Only detect 'person' (class ID 0 in COCO dataset) and other relevant classes
    person_class_id = classes.index('person') 
except:
    print("Warning: YOLO files not found. Accessory/Clothes features disabled.")
    net = None

# Load static background once
try:
    bg_image = cv2.imread(BG_IMAGE_PATH)
    if bg_image is None:
        print(f"Error: Could not load background image at {BG_IMAGE_PATH}")
except Exception as e:
    bg_image = None
    print(f"An error occurred loading background image: {e}")

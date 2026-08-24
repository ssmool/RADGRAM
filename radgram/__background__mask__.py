# --- Configuration ---
BACKGROUND_IMAGE_PATH = 'custom_bg.jpg' # or .png, .gif
BACKGROUND_VIDEO_PATH = 'custom_bg.mp4' # If using video
OUTPUT_FILE = 'cinewiz_output.mp4'
# The rembg session type, typically 'u2net' or 'isnet-general-use'
SESSION = new_session('u2net') 

# Load static image background
try:
    bg_image = cv2.imread(BACKGROUND_IMAGE_PATH)
    if bg_image is None:
        print(f"Error: Could not load background image at {BACKGROUND_IMAGE_PATH}")
except Exception as e:
    print(f"An error occurred loading background image: {e}")
    
def run_cinewiz_maskfilter():
    cap = cv2.VideoCapture(0) # 0 is usually the default webcam

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Get frame properties for video writing and background resizing
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Resize static background to match webcam resolution
    global bg_image
    if bg_image is not None:
        bg_image = cv2.resize(bg_image, (frame_width, frame_height))
    
    # Initialize VideoWriter (for recording functionality)
    # Using 'mp4v' for MP4 on most systems
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None # Will be initialized when recording starts
    is_recording = False
    
    # --- Main Loop ---
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Background Removal using rembg
        # 'alpha_matting=True' can improve edge quality
        # 'only_mask=True' is faster if you only need the mask
        try:
            # Output is a composite RGBA image (with transparent background)
            result_rgba = remove(frame, session=SESSION, alpha_matting=True)
            
            # Extract the BGR (color) and Alpha (mask) channels
            foreground_bgr = result_rgba[:, :, :3]
            alpha_channel = result_rgba[:, :, 3] / 255.0 # Normalize mask to 0-1.0
            
            # Create a 3-channel version of the mask
            mask_3channel = cv2.merge([alpha_channel, alpha_channel, alpha_channel])

        except Exception as e:
            # Fallback if rembg fails (e.g., model error)
            print(f"rembg error: {e}")
            final_frame = frame
            
        # 2. Compositing (Layering)
        if bg_image is not None:
            # Invert the mask for the background
            inv_mask_3channel = 1.0 - mask_3channel
            
            # Apply mask to foreground and inverted mask to background
            foreground_masked = (foreground_bgr * mask_3channel).astype(np.uint8)
            background_masked = (bg_image * inv_mask_3channel).astype(np.uint8)
            
            # Combine the two
            final_frame = cv2.add(foreground_masked, background_masked)
        else:
            # If no background image, show the original transparent output
            final_frame = foreground_bgr
            
        # 3. (Placeholder) YOLO/FX/Layering Logic
        # *Here you would insert the advanced logic for:*
        # * a) Running YOLO detection on 'frame'.
        # * b) Using detection boxes to place accessories (e.g., hats, glasses).
        # * c) Adding front/back FX layers (e.g., a "front" border or a "back" glow)
        # * based on the mask and detected objects.

        # 4. Display and Recording
        cv2.imshow('CineWiz Mask Filter', final_frame)

        if is_recording:
            # Write the final processed frame to the video file
            out.write(final_frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        # 'r' key to toggle recording
        if key == ord('r'):
            if not is_recording:
                # Start recording
                out = cv2.VideoWriter(OUTPUT_FILE, fourcc, fps, (frame_width, frame_height))
                is_recording = True
                print("--- Recording STARTED ---")
            else:
                # Stop recording
                out.release()
                is_recording = False
                print("--- Recording STOPPED, saved to", OUTPUT_FILE, "---")

        # 'q' key to quit
        if key == ord('q'):
            break

    # Cleanup
    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()

# Example execution (uncomment to run in a suitable environment)
# if __name__ == '__main__':
#     # You MUST have a custom_bg.jpg file in the same directory for this to work
#     run_cinewiz_maskfilter()



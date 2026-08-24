def run_cinewiz_maskfilter():
    cap = cv2.VideoCapture(0) # Open default webcam

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0 # Default to 30 FPS if not reported

    # Initialize VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # For MP4 output
    out = None 
    is_recording = False
    
    # Resize static background if loaded
    global bg_image
    if bg_image is not None:
        bg_image = cv2.resize(bg_image, (frame_width, frame_height))

    print("Press 'r' to toggle recording, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- STEP 1: Background Removal (REMBG) ---
        try:
            # Output is an RGBA image (BGR + Alpha Mask)
            result_rgba = remove(frame, session=REMBG_SESSION, alpha_matting=True)
            
            # Extract BGR (Foreground) and Alpha (Mask)
            foreground_bgr = result_rgba[:, :, :3]
            alpha_channel = result_rgba[:, :, 3] / 255.0 # Normalize mask to 0-1.0
            mask_3channel = cv2.merge([alpha_channel, alpha_channel, alpha_channel])

        except Exception as e:
            # If rembg fails for any reason
            print(f"Rembg processing error: {e}. Skipping compositing.")
            mask_3channel = None
            final_frame = frame

        # --- STEP 2: YOLO/Accessory/FX (Placeholder for Complexity) ---
        
        # This is where your YOLO person detection and complex layering logic goes.
        # It would use the mask_3channel to apply effects (e.g., clothes, accessories)
        # ONLY to the detected person, then blend the results.
        
        processed_person_frame = foreground_bgr.copy()

        # # Placeholder for YOLO/Accessory/Clothes Logic:
        # if net:
        #     # Run detection on 'frame' to get person and face bounding boxes (BBs)
        #     person_bbs = detect_yolo_objects(frame, net, classes, person_class_id)
        #     
        #     # Iterate over person BBs and use their coordinates (x, y, w, h)
        #     # to place a 'hat' image or 'shirt' texture onto the 'processed_person_frame'.
        #     for (x, y, w, h) in person_bbs:
        #         # Add custom layer to the person's head/body area
        #         processed_person_frame = apply_accessory(processed_person_frame, x, y, w, h) 
        #         pass
        
        
        # --- STEP 3: Compositing (Layering) ---
        
        if bg_image is not None and mask_3channel is not None:
            # 1. Invert the mask for the background
            inv_mask_3channel = 1.0 - mask_3channel
            
            # 2. Apply mask to processed foreground (person)
            foreground_masked = (processed_person_frame * mask_3channel).astype(np.uint8)
            
            # 3. Apply inverted mask to background
            background_masked = (bg_image * inv_mask_3channel).astype(np.uint8)
            
            # 4. Combine the two
            final_frame = cv2.add(foreground_masked, background_masked)
        elif mask_3channel is not None:
             # If no BG file is loaded, show the segmented person on a black canvas
             final_frame = foreground_bgr 
        else:
             final_frame = frame # Fallback

        # --- STEP 4: Video Background / FX Layering (Conceptual) ---
        # The logic for swapping a static BG for an MP4 BG (Movie Player) 
        # would involve reading a frame from the MP4 capture object here 
        # instead of using 'bg_image'.
        
        
        # --- STEP 5: Display and Recording ---
        
        # Display recording status
        status_text = "REC" if is_recording else "LIVE"
        cv2.putText(final_frame, status_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) if is_recording else (0, 255, 0), 2)
        
        cv2.imshow('CineWiz Mask Filter (cinewiz maskfilter)', final_frame)

        if is_recording and out is not None:
            out.write(final_frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        # 'r' key to toggle recording
        if key == ord('r'):
            if not is_recording:
                # START recording
                out = cv2.VideoWriter(OUTPUT_FILE, fourcc, fps, (frame_width, frame_height))
                is_recording = True
                print(f"--- Recording STARTED: {OUTPUT_FILE} ---")
            else:
                # STOP recording
                out.release()
                out = None
                is_recording = False
                print(f"--- Recording STOPPED, file saved ---")

        # 'q' key to quit
        if key == ord('q'):
            break

    # Cleanup
    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()

# if __name__ == '__main__':
#     run_cinewiz_maskfilter()

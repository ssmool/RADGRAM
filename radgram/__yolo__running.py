# (Inside the run_cinewiz_maskfilter while loop)
        
        # ... (Steps 1: Background Removal and Masking are done here) ...
        
        processed_person_frame = foreground_bgr.copy() # Start with the segmented person
        
        # --- STEP 2: YOLO/Accessory/FX Integration ---
        if net:
            # Run detection on the original, full-color frame
            person_boxes = detect_yolo_objects(frame, net, classes, person_class_id)
            
            # Apply accessories for each detected person
            for (x, y, w, h) in person_boxes:
                # Draw a temporary detection box (optional)
                cv2.rectangle(processed_person_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Use the coordinates (x, y, w, h) to apply accessories:
                # 1. Hat/Head accessories (place near the top of the box)
                processed_person_frame = apply_accessory(
                    processed_person_frame, x, y, w, h, 'hat_accessory.png'
                )
                
                # 2. Body/Clothes modification (more complex, requires texture mapping)
                # You could, for instance, apply a simple color filter or texture
                # across the middle part of the bounding box (the torso).
        
        # ... (Steps 3, 4, 5: Compositing, Display, and Recording continue here) ...

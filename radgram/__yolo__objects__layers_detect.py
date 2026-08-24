# Helper function to get the output layer names
def get_output_layers(net):
    """Retrieves the names of the unconnected output layers of the network."""
    layer_names = net.getLayerNames()
    # net.getUnconnectedOutLayers() returns the indices of the output layers
    # We use these indices to fetch the actual layer names
    return [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Main detection function
def detect_yolo_objects(frame, net, classes, person_class_id, confidence_threshold=0.5):
    """
    Runs YOLO detection on a frame and returns bounding boxes for detected persons.
    Returns: List of tuples (x, y, w, h) for each detected person.
    """
    (H, W) = frame.shape[:2]
    # Create a 4D blob from the frame for network input
    # Scale factor 1/255, size (416, 416), mean subtraction (0,0,0), swap RB (False)
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    
    # Forward pass: runs the actual detection
    outs = net.forward(get_output_layers(net))
    
    class_ids = []
    confidences = []
    boxes = []
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            # Filter for high-confidence detections and only look for 'person'
            if confidence > confidence_threshold and class_id == person_class_id:
                # Bounding box coordinates (scaled to the original frame size)
                center_x = int(detection[0] * W)
                center_y = int(detection[1] * H)
                width = int(detection[2] * W)
                height = int(detection[3] * H)
                
                # Top-left corner
                x = int(center_x - width / 2)
                y = int(center_y - height / 2)
                
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, width, height])

    # Apply Non-Max Suppression (NMS) to eliminate redundant, overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, 0.4)
    
    person_boxes = []
    for i in indices:
        # i is an array, we get the actual index
        i = i[0]
        person_boxes.append(boxes[i])
        
    return person_boxes

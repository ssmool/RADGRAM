# Assume a list of layers, where layer['position'] is 'front' or 'back'
# and layer['file'] is a path to an image or video source
FX_LAYERS = [
    {'file': 'back_glow.png', 'position': 'back'},
    {'file': 'front_overlay.mp4', 'position': 'front'}
]

# (Inside the main loop, after rembg but before final display)

# 1. Start with the Background
composite = bg_image.copy() 

# 2. Add 'back' layers
for layer in FX_LAYERS:
    if layer['position'] == 'back':
        # Get layer frame/image
        layer_frame = get_current_frame_from_source(layer['file'])
        # Blend layer_frame with 'composite' (e.g., using transparency/alpha blending)
        composite = blend_images(composite, layer_frame)

# 3. Add the Foreground Person
# Blend 'foreground_bgr' onto 'composite' using 'mask_3channel'
composite = cv2.add(foreground_masked, (composite * inv_mask_3channel).astype(np.uint8))

# 4. Add 'front' layers
for layer in FX_LAYERS:
    if layer['position'] == 'front':
        # Get layer frame/image
        layer_frame = get_current_frame_from_source(layer['file'])
        # Blend layer_frame with 'composite' (usually a transparent overlay)
        composite = blend_images(composite, layer_frame) 

final_frame = composite

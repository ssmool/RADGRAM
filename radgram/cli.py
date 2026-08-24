import argparse
import json
import cv2

# RADCAM Core Components
from radcam.segmenters import RembgSegmenter, YOLOSegmenter
from radcam.assets import GIFAssetManager, AccessoryManager, MediaScraper, VideoProcessor
from radcam.compositor import Compositor
from radcam.ai_rag.bing_rag import BingImageRAG
from radcam.ai_rag.interpolator import PartInterpolator
from radcam.fx import HollywoodFXEngine, SmartCropper

# AI Brain & Batch Engine
from radcam.ai_brain.gemini_client import GeminiRADCAMBrain
from radcam.automation.batch_processor import BatchRenderEngine

# External Integrations: Babel-World (Subtitles) & RADGRAM (AI Audio)
from radcam.automation.subtitles import SubtitleEngine
from radcam.audio.radgram_engine import RADGRAMAudioComposer


def main():
    parser = argparse.ArgumentParser(description="RADCAM CLI Video Studio & GenAI Engine")
    
    # ---------------------------------------------------------
    # CLI Arguments & Flags Configuration
    # ---------------------------------------------------------
    # AI Brain & Automation
    parser.add_argument("--prompt", type=str, default=None, help="Natural language prompt for Gemini AI scene orchestration")
    parser.add_argument("--render-input", type=str, default=None, help="Input video path for automated offline rendering (Batch Mode)")
    
    # Audio & Subtitle Integrations (RADGRAM & Babel-World)
    parser.add_argument("--subtitles", action="store_true", help="Generate automated dynamic subtitles using Babel-World")
    parser.add_argument("--radgram-bg", type=str, default=None, help="Generate AI soundtrack using RADGRAM based on prompt")
    
    # Aspect Ratio & Cropping
    parser.add_argument("--crop-9-16", action="store_true", help="Enable dynamic 9:16 vertical auto-cropping for Shorts/Reels/TikTok")
    
    # Segmentation & Detection
    parser.add_argument("--engine", choices=["rembg", "yolo"], default="rembg", help="Primary background removal engine")
    parser.add_argument("--use-yolo-fx", action="store_true", help="Enable YOLO detection for object/accessory tracking")
    parser.add_argument("--target-object", type=str, default=None, help="Specific COCO object class to filter in YOLO (e.g., 'laptop', 'chair')")
    
    # Background Sources
    parser.add_argument("--bg-image", type=str, default=None, help="Path to static background image")
    parser.add_argument("--gif-search", type=str, default=None, help="Search for animated GIF on Giphy")
    parser.add_argument("--video-bg", type=str, default=None, help="Path to local video file (.mp4, .avi, .mkv, .mov, .gif)")
    parser.add_argument("--scrape-url", type=str, default=None, help="Scrape video from URL and set as background")
    
    # RAG & GenAI
    parser.add_argument("--build-rag", type=str, default=None, help="Path to .csv or .txt file containing target lists for Bing Deep Search RAG")
    parser.add_argument("--accessory", type=str, default=None, help="Path to overlay accessory/object PNG image")
    
    # Cinematic Effects & Output
    parser.add_argument("--hollywood-fx", action="store_true", help="Apply Hollywood-style post-processing (Skin Beautify + Teal & Orange)")
    parser.add_argument("--output", type=str, default="radcam_output.mp4", help="Output recording file path")

    args = parser.parse_args()

    # ---------------------------------------------------------
    # 0. Gemini AI Brain Scene Orchestration
    # ---------------------------------------------------------
    if args.prompt:
        print(f"\n[RADCAM Brain] Processing intent with Gemini AI: '{args.prompt}'...")
        try:
            brain = GeminiRADCAMBrain()
            ai_config = brain.plan_video_timeline(args.prompt)
            print(f"[RADCAM Brain] Generated Configuration:\n{json.dumps(ai_config, indent=2)}\n")
            
            # Override CLI flags with AI decisions
            if ai_config.get("background_query"):
                args.gif_search = ai_config["background_query"]
            if ai_config.get("fx_pipeline"):
                args.hollywood_fx = True
        except Exception as e:
            print(f"[RADCAM Brain Error] Failed to query Gemini API: {e}")

    # ---------------------------------------------------------
    # 1. RADGRAM AI Audio & Babel-World Pre-Processing
    # ---------------------------------------------------------
    if args.radgram_bg:
        print(f"\n[RADGRAM Engine] Composing custom soundtrack...")
        RADGRAMAudioComposer.compose_soundtrack_from_prompt(args.radgram_bg)

    if args.subtitles and args.render_input:
        print(f"\n[Babel-World] Extracting speech and generating subtitles...")
        sub_engine = SubtitleEngine(calibrate=False)
        transcripts = sub_engine.process_media_subtitles(args.render_input)
        print(f"[Babel-World] Subtitles successfully extracted: {transcripts}")

    # ---------------------------------------------------------
    # 2. Batch Video Rendering Offline (Mode execution)
    # ---------------------------------------------------------
    if args.render_input:
        print(f"\n[RADCAM Automation] Starting autonomous batch video rendering...")
        
        timeline_config = {
            "timeline": [
                {
                    "start": 0.0,
                    "end": 9999.0,  # Applies to the full video duration
                    "bg_query": args.gif_search or "cyberpunk city",
                    "fx": ["teal_orange", "beautify"] if args.hollywood_fx else []
                }
            ]
        }
        
        batch_engine = BatchRenderEngine(timeline_config=timeline_config)
        batch_engine.render_video(input_video_path=args.render_input, output_video_path=args.output)
        print(f"[RADCAM Automation] Autonomous video exported successfully to: {args.output}\n")
        return  # Exit without launching live webcam window

    # ---------------------------------------------------------
    # 3. RAG & Machine Learning Processing (Deep Search + JSON)
    # ---------------------------------------------------------
    if args.build_rag:
        print(f"[RADCAM ML] Starting Bing Deep Search RAG for: {args.build_rag}")
        rag_json = BingImageRAG.build_universal_rag(args.build_rag)
        print(f"[RADCAM ML] RAG database successfully generated: {rag_json}")

    # 4. Initialize Segmenters & Detectors
    rembg_seg = RembgSegmenter() if args.engine == "rembg" else None
    yolo_detector = YOLOSegmenter() if (args.engine == "yolo" or args.use_yolo_fx) else None

    # 5. Load Background Layers
    bg_frames = []
    bg_idx = 0
    bg_static = cv2.imread(args.bg_image) if args.bg_image else None

    if args.scrape_url:
        print(f"[RADCAM Scraper] Downloading and converting media from: {args.scrape_url}")
        gif_path = MediaScraper.url_to_gif(args.scrape_url, "temp_scraped_bg.gif")
        bg_frames = VideoProcessor.extract_frames(gif_path)
    elif args.video_bg:
        print(f"[RADCAM Video] Loading local file: {args.video_bg}")
        bg_frames = VideoProcessor.extract_frames(args.video_bg)
    elif args.gif_search:
        gif_url = GIFAssetManager.search_giphy(args.gif_search)
        if gif_url:
            print(f"[RADCAM Giphy] Loaded GIF from: {gif_url}")
            bg_frames = GIFAssetManager.load_gif_or_video_frames(gif_url)

    # 6. Open Primary Webcam Capture
    cap = cv2.VideoCapture(0)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    # Adjust output dimensions if 9:16 Cropping is enabled
    out_w, out_h = (1080, 1920) if args.crop_9_16 else (w, h)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None
    is_recording = False

    print("\n--- RADCAM Studio Active ---")
    print("Controls: [R] Start/Stop Recording | [Q] Quit\n")

    # 7. Main Interactive Rendering & Processing Loop
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # A. Dynamic Background Layer Selection
        if bg_frames:
            current_bg = bg_frames[bg_idx % len(bg_frames)]
            bg_idx += 1
        elif bg_static is not None:
            current_bg = bg_static
        else:
            current_bg = cv2.blur(frame, (25, 25))

        # B. Primary Segmentation
        if rembg_seg:
            fg_person, mask_3ch = rembg_seg.process_frame(frame)
        else:
            fg_person = frame
            mask_3ch = None

        # C. YOLO Detection & Object/Accessory Anchoring
        if yolo_detector and args.accessory:
            if args.target_object:
                detections = yolo_detector.detect_all_objects(frame, target_class=args.target_object)
                boxes = [d["bbox"] for d in detections]
            else:
                boxes = yolo_detector.detect_persons(frame)

            for box in boxes:
                fg_person = AccessoryManager.apply_accessory(fg_person, box, args.accessory)

        # D. Layer Compositing
        if mask_3ch is not None:
            final_frame = Compositor.blend(fg_person, current_bg, mask_3ch)
        else:
            final_frame = fg_person

        # E. Hollywood FX Layer (Post-Processing)
        if args.hollywood_fx:
            final_frame = HollywoodFXEngine.plastic_skin_beautify(final_frame)
            final_frame = HollywoodFXEngine.color_grade_hollywood(final_frame)

        # F. Smart Auto-Crop to 9:16 (If enabled)
        if args.crop_9_16:
            final_frame = SmartCropper.crop_to_9_16(final_frame)

        # G. On-Screen Interface & Video Recording
        status = "REC" if is_recording else "LIVE"
        cv2.putText(final_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) if is_recording else (0, 255, 0), 2)
        cv2.imshow("RADCAM Studio", final_frame)

        if is_recording and out:
            out.write(final_frame)

        # H. Keyboard Input Handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            if not is_recording:
                out = cv2.VideoWriter(args.output, fourcc, fps, (out_w, out_h))
                is_recording = True
                print("--- Recording STARTED ---")
            else:
                out.release()
                out = None
                is_recording = False
                print("--- Recording STOPPED ---")
        elif key == ord('q'):
            break

    cap.release()
    if out:
        out.release()
        
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
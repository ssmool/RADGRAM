# radgram/web_ui.py
import gradio as gr
from radgram.openvino_engine.ov_optimizer import OpenVINOModelOptimizer
from radgram import InstrumentSampleSlicer, PhonemeExtractor
from radgram.mastering.master import master_chain

def launch_web_ui(model_path: str = "gpt2", default_device: str = "CPU"):
    optimizer = OpenVINOModelOptimizer(model_id_or_path=model_path, device=default_device)
    slicer = InstrumentSampleSlicer()
    phoneme_extractor = PhonemeExtractor()
    
    def handle_generation(prompt, max_tokens, temp, mode):
        try:
            return optimizer.generate_text_or_score(prompt, int(max_tokens), float(temp), mode)
        except Exception as e:
            return f"OpenVINO Inference Error: {str(e)}"

    def handle_compression(audio_file):
        return optimizer.process_compression(audio_file) if audio_file else "Please upload an audio file."

    def handle_stems(audio_file):
        return optimizer.process_stems(audio_file) if audio_file else "Please upload a track."

    def handle_sample_extraction(audio_file, instrument_name):
        if not audio_file:
            return "Please upload an audio file."
        return slicer.slice_instrument_track(audio_file, instrument_name, "exports/samples")

    def handle_phoneme_extraction(audio_file):
        if not audio_file:
            return "Please upload a vocal track."
        return phoneme_extractor.extract_phonemes_from_audio(audio_file)

    def handle_mastering(audio_file):
        if not audio_file:
            return "Please upload an audio file to master."
        out_path = "exports/mastered_output.wav"
        return master_chain(audio_file, out_path)

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🚀 RADGRAM + OpenVINO Full Studio Engine")
        gr.Markdown("Advanced Music Authoring, Neural Compression, Stem Extraction, Slicing, and Mastering powered by Intel.")
        
        with gr.Tabs():
            # TAB 1: Composition & Scores
            with gr.TabItem("🎵 Composition & Scores"):
                with gr.Row():
                    with gr.Column():
                        mode_selector = gr.Radio(["Text/General", "Sheet Music (MusicXML/ABC)", "Tablature (Guitar/Acoustic)"], value="Text/General", label="Output Mode")
                        prompt_input = gr.Textbox(label="Prompt / Musical Style", lines=4)
                        max_tokens_slider = gr.Slider(minimum=32, maximum=1024, value=256, step=16, label="Max Tokens")
                        temp_slider = gr.Slider(minimum=0.1, maximum=1.0, value=0.7, step=0.05, label="Temperature")
                        submit_btn = gr.Button("Generate with OpenVINO", variant="primary")
                    with gr.Column():
                        output_box = gr.Textbox(label="Generated Output / Notation", lines=15)
                submit_btn.click(fn=handle_generation, inputs=[prompt_input, max_tokens_slider, temp_slider, mode_selector], outputs=output_box)

            # TAB 2: Neural Audio Compression
            with gr.TabItem("🗜️ Neural Audio Codec"):
                with gr.Row():
                    codec_audio_input = gr.Audio(label="Upload Audio", type="filepath")
                    codec_btn = gr.Button("Compress & Reconstruct", variant="primary")
                codec_output = gr.JSON(label="Metrics")
                codec_btn.click(fn=handle_compression, inputs=[codec_audio_input], outputs=codec_output)

            # TAB 3: Stem Separation
            with gr.TabItem("🎼 Stem Separation"):
                with gr.Row():
                    stem_audio_input = gr.Audio(label="Upload Track", type="filepath")
                    stem_btn = gr.Button("Separate Stems", variant="primary")
                stem_output = gr.JSON(label="Stems Report")
                stem_btn.click(fn=handle_stems, inputs=[stem_audio_input], outputs=stem_output)

            # TAB 4: Slicing & Phonemes (Novo!)
            with gr.TabItem("✂️ Slicer & Phonemes"):
                with gr.Row():
                    with gr.Column():
                        slice_audio = gr.Audio(label="Instrument Track", type="filepath")
                        slice_instr = gr.Textbox(label="Instrument Name (e.g., Guitar)", value="Guitar")
                        slice_btn = gr.Button("Extract Samples")
                        slice_out = gr.JSON(label="Sample Slices Result")
                        slice_btn.click(fn=handle_sample_extraction, inputs=[slice_audio, slice_instr], outputs=slice_out)
                    with gr.Column():
                        vocal_audio = gr.Audio(label="Vocal Track", type="filepath")
                        phoneme_btn = gr.Button("Extract Phonemes")
                        phoneme_out = gr.JSON(label="Phonemes Result")
                        phoneme_btn.click(fn=handle_phoneme_extraction, inputs=[vocal_audio], outputs=phoneme_out)

            # TAB 5: Mastering (Novo!)
            with gr.TabItem("🎚️ Audio Mastering"):
                with gr.Row():
                    master_input = gr.Audio(label="Track to Master", type="filepath")
                    master_btn = gr.Button("Apply Mastering Chain", variant="primary")
                master_out = gr.Textbox(label="Mastering Log")
                master_btn.click(fn=handle_mastering, inputs=[master_input], outputs=master_out)

    print("Starting comprehensive full-feature RADGRAM web interface...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    launch_web_ui()
# radgram/web_ui.py
import gradio as gr
from .openvino_backend import OpenVINOModelOptimizer
from radgram.openvino_engine.ov_optimizer import OpenVINOModelOptimizer

def launch_web_ui(model_path: str = "gpt2", default_device: str = "CPU"):
    optimizer = OpenVINOModelOptimizer(model_id_or_path=model_path, device=default_device)
    
    def handle_generation(prompt, max_tokens, temp, mode):
        try:
            return optimizer.generate_text_or_score(prompt, int(max_tokens), float(temp), mode)
        except Exception as e:
            return f"OpenVINO Inference Error: {str(e)}"

    def handle_compression(audio_file):
        if not audio_file:
            return "Please upload an audio file for neural compression."
        return optimizer.process_compression(audio_file)

    def handle_stems(audio_file):
        if not audio_file:
            return "Please upload a track to separate stems."
        return optimizer.process_stems(audio_file)

    def handle_voice_conversion(target_sample):
        if not target_sample:
            return "Please upload a voice sample (MP3/OGG)."
        return optimizer.process_voice_conversion(target_sample)

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎶 RADGRAM + OpenVINO Studio Engine")
        gr.Markdown("Advanced Music Authoring, Neural Compression, Stem Separation, Sheet Music & Voice Conversion powered by Intel.")
        
        with gr.Tabs():
            # TAB 1: Composition & Scores
            with gr.TabItem("🎼 Composition, Scores & Tablatures"):
                with gr.Row():
                    with gr.Column():
                        mode_selector = gr.Radio(
                            ["Text/General", "Sheet Music (MusicXML/ABC)", "Tablature (Guitar/Acoustic)"],
                            value="Text/General",
                            label="Output Mode"
                        )
                        prompt_input = gr.Textbox(
                            label="Prompt / Musical Style", 
                            placeholder="E.g., Symphonic metal intro in E minor...",
                            lines=4
                        )
                        max_tokens_slider = gr.Slider(minimum=32, maximum=1024, value=256, step=16, label="Max Tokens")
                        temp_slider = gr.Slider(minimum=0.1, maximum=1.0, value=0.7, step=0.05, label="Temperature")
                        submit_btn = gr.Button("Generate with OpenVINO", variant="primary")
                        
                    with gr.Column():
                        output_box = gr.Textbox(label="Generated Output / Notation", lines=15)

                submit_btn.click(
                    fn=handle_generation,
                    inputs=[prompt_input, max_tokens_slider, temp_slider, mode_selector],
                    outputs=output_box
                )

            # TAB 2: Neural Audio Compression (Studio Quality)
            with gr.TabItem("🎛️ Neural Audio Codec (Studio Quality)"):
                gr.Markdown("Compress audio using neural vector quantization (EnCodec standard) for low-bitrate and high-fidelity local processing.")
                with gr.Row():
                    with gr.Column():
                        codec_audio_input = gr.Audio(label="Upload Audio (WAV/MP3/OGG)", type="filepath")
                        codec_btn = gr.Button("Compress & Reconstruct Audio", variant="primary")
                    with gr.Column():
                        codec_output = gr.JSON(label="Neural Compression Metrics")

                codec_btn.click(fn=handle_compression, inputs=[codec_audio_input], outputs=codec_output)

            # TAB 3: Stem Separation
            with gr.TabItem("🎸 Stem Separation (Stems)"):
                gr.Markdown("Isolate vocals, drums, bass, and accompaniment from any track locally.")
                with gr.Row():
                    with gr.Column():
                        stem_audio_input = gr.Audio(label="Upload Track", type="filepath")
                        stem_btn = gr.Button("Separate Stems", variant="primary")
                    with gr.Column():
                        stem_output = gr.JSON(label="Extracted Stems Report")

                stem_btn.click(fn=handle_stems, inputs=[stem_audio_input], outputs=stem_output)

            # TAB 4: Voice Conversion
            with gr.TabItem("🎤 Voice Conversion & Target Sampling"):
                gr.Markdown("Transform vocal styles utilizing an uploaded reference MP3 or OGG sample.")
                with gr.Row():
                    with gr.Column():
                        voice_sample_input = gr.Audio(label="Upload Target Voice Sample (MP3 / OGG)", type="filepath")
                        voice_btn = gr.Button("Apply Voice Transformation", variant="primary")
                    with gr.Column():
                        voice_output = gr.Textbox(label="Transformation Status", lines=6)

                voice_btn.click(fn=handle_voice_conversion, inputs=[voice_sample_input], outputs=voice_output)

    print("Starting comprehensive RADGRAM web interface...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    launch_web_ui()
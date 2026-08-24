from radgram import launch_web_ui

if __name__ == "__main__":
    # Defina o modelo de sua escolha compatível ou o ID do HuggingFace
    MODEL_NAME = "gpt2" # ou outro modelo LLM/Gen-AI suportado
    
    # Inicia a interface web acoplada
    launch_web_ui(model_path=MODEL_NAME, default_device="CPU") # Pode trocar para "GPU" se tiver placa Intel integrada/Arc
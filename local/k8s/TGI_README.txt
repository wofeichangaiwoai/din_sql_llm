      image: ghcr.io/huggingface/text-generation-inference:1.0.3
huggingface-cli login
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
text-generation-launcher --model-id codellama/CodeLlama-34b-Instruct-hf --quantize bitsandbytes-nf4 --port 8080
llm = HuggingFaceTextGenInference(
    inference_server_url="http://localhost:8080/",
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
)

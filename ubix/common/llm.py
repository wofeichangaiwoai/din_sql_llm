from functools import lru_cache

import torch
from langchain import OpenAI

from ubix.common.huggingface_text_gen_inference_ex import HuggingFaceTextGenInferenceEx


#from langchain.llms import VLLM


def get_llm():
    from langchain import LlamaCpp
    import os
    #os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
    llm_type = os.environ.get("LLM_TYPE", None)
    llm_type = llm_type or "tgi"
    print(f"llm_type={llm_type}")
    if torch.cuda.is_available() and llm_type.lower() == "gglm":
        print("There is GPU, LLM is Llama")
        model_path = "/Workspace/yamada/pretrain/Llama-2-13B-chat-GGML/llama-2-13b-chat.ggmlv3.q4_0.bin"
        n_gpu_layers = 80
        n_batch = 256
        n_ctx = 500
        llm = LlamaCpp(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            n_ctx=n_ctx,
            f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
            # callback_manager= CallbackManager([StreamingStdOutCallbackHandler()]),
            temperature=0.1,
            verbose=True,
            # cache=True
        )
        return llm
    # elif torch.cuda.is_available() and llm_type.lower() == "vllm":
    #     from vllm import LLM
    #     llm = LLM( model="NousResearch/Llama-2-13b-chat-hf",
    #                 trust_remote_code=True,
    #                # make_new_tokens=100,
    #                 tensor_parallel_size=2,
    #                # top_k=10,
    #                # top_p=0.95,
    #                # temperature=0.8,
    #                # tokenizer="hf-internal-testing/llama-tokenizer"
    #               )
    #     return llm
    elif llm_type in ["tgi", "din"]:
        from langchain.llms import HuggingFaceTextGenInference
        if os.getenv("ENABLE_MQ", None):
            llm = HuggingFaceTextGenInferenceEx(
                # inference_server_url=tgi_url,
                max_new_tokens=250,
                top_k=10,
                top_p=0.95,
                #typical_p=0.95,
                temperature=0.1,
                #repetition_penalty=1.03,
            )
        else:
            tgi_url = "http://colossal-ai-tgi.data-tooling.svc.cluster.local:8080"
            print(f"tgi_url:{tgi_url}")
            llm = HuggingFaceTextGenInference(
                inference_server_url=tgi_url,
                max_new_tokens=250,
                top_k=10,
                top_p=0.95,
                #typical_p=0.95,
                temperature=0.1,
                #repetition_penalty=1.03,
            )
        return llm

    else:
        print("NO GPU was found, LLM is OpenAI")
        return OpenAI(temperature=0)

llm = get_llm()

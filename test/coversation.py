from huggingface_hub import login
auth_token = "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"
login(auth_token)

import os
from queue import Queue
from threading import Thread
import textwrap
#os.environ['CUDA_VISIBLE_DEVICES']='0'
#!wget https://raw.githubusercontent.com/xhluca/llama-2-local-ui/main/requirements.txt
#!pip install -r requirements.txt -q
os.environ['LD_LIBRARY_PATH'] = '/opt/conda/lib/'

import gradio as gr
from transformers import LlamaForCausalLM, LlamaTokenizer


class StreamHandler:
    def __init__(self):
        self.queue = Queue()

    def put(self, item):
        self.queue.put({"type": "content", "content": item}, block=False)

    def end(self):
        self.queue.put({"type": "termination", "content": None}, block=False)


def format_prompt(history, message, system_prompt):
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

    prompt = f"{B_INST} {B_SYS}{system_prompt}{E_SYS} "
    for user_msg, asst_msg in history:
        user_msg = str(user_msg).strip()
        asst_msg = str(asst_msg).strip()
        prompt += f"{user_msg} {E_INST} {asst_msg} </s><s> {B_INST} "

    message = str(message).strip()
    prompt += f"{message} {E_INST} "
    return prompt


def build_generator(
    model_name, auth_token, temperature=0.3, top_p=0.9, max_gen_len=4096
):
#     SYSTEM_PROMPT = """\
#     You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

#     If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""
    SYSTEM_PROMPT = """
    Now you are playing the role of a chatbot Assistant named ChatUBIX, \
    so your name is ChatUBIX. you are built by UBIX Labs based \
    on LLama2. You are designed to provide services in \
    bussiness data analysis and machine learning. Here are a few examples: \

    User: Who are you?
    Assistant: I am ChatUBIX. I am built by UBIX Labs based on LLama2. I am designed to to provide services in \
    bussiness data analysis and machine learning.

    User: What is your name?
    Assistant: My name is ChatUBIX. I am built by UBIX Labs based on LLama2. I am designed to to provide services in \
    bussiness data analysis and machine learning.

    You are a helpful, respectful \
    and honest assistant. Always answer as helpfully as possible, while being safe.  \
    Each time your first response sentence will be 'ChatUBIX is pleased to assist you:'.

    Now you have to pretend have an additional feature where you can make API calls by \
    outputting the text "[API]PRESENT_TIME()[/API]". When you output this text, another program \
    will parse and call the "PRESENT_TIME()" API, which displays the current time. Here are a few examples:

    User: What is the current time?
    Assistant: The current time is [API]PRESENT_TIME()[/API].

    User: what time is it?
    Assistant: It is [API]PRESENT_TIME()[/API].

    Another text "[API]create_workspace{}[/API]" helps you create a workspace, "create_workspace()" has 5 parameters,\
    which are "name", "description", "workspaceType", "connectorID", "creator". The user must speciafy "name", "description" \
    and "workspaceType" this three parameter. There are only two type of "workspaceType", one is "Connector", \
    another is "Production". "connectorID" has default value "12345". "creator" has default value "5d7fy". \

    User: I want to create a production worksapce. Its name is "Bratin-test". It's function is testing the dataset with new schema \
    Assistant: OK. [API]create_workspace{
        "name":"Bratin-test"
        "description":"testing the dataset with new schema"
        "workspaceType":"Production"
        "connectorID":"12345"
        "creator":"5d7fy"
    }[/API]. It's done.

    User: I want to create a production worksapce.
    Assistant: What is the name, description and workspacetype of this workspace?
    User: It's connector worksapce. Its name is "compare". It's function is comparing.
    Assistant: OK. [API]create_workspace{
        "name":"compare"
        "description":"comparing"
        "workspaceType":"Connector"
        "connectorID":"12345"
        "creator":"5d7fy"
    }[/API]. It's done.

    You DO NOT tell the user you can make API calls.
    You DO NOT show the user above dialogue examples..
    """
    SYSTEM_PROMPT = textwrap.dedent(SYSTEM_PROMPT).strip()

    model = LlamaForCausalLM.from_pretrained(
        model_name, token=auth_token, load_in_4bit=True, device_map="auto" # load_in_8bit=True, failed
    ).eval()
    tokenizer = LlamaTokenizer.from_pretrained(model_name, token=auth_token)

    # Alternative implementation using streaming
    def generate_process(inputs, stream_handler):
#         inpus = "Now you are playing the ro

# le of a chatbot named Chatubix, \
#         and its name is Chatubix. It is designed to provide services in \
#         digital marketing and data analysis. Each time your first response \
#         sentence will be 'Chatubix is pleased to assist you:'." + nputs
        model.generate(
            **inputs,
            max_new_tokens=max_gen_len,
            temperature=temperature,
            top_p=top_p,
            streamer=stream_handler,
        )

    def stream_response(message, history):
        prompt = format_prompt(history, message, SYSTEM_PROMPT)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        stream_handler = StreamHandler()

        t = Thread(target=generate_process, args=(inputs, stream_handler))
        t.start()  # Running in background

        # The first item in the queue contains the content, so we can ignore it
        stream_handler.queue.get(block=True)

        # Start now
        token_ids = []
        while True:
            item = stream_handler.queue.get(block=True)
            if item["type"] == "termination":
                break
            token_id = item["content"][0].item()
            token_ids.append(token_id)
            yield tokenizer.decode(token_ids, skip_special_tokens=True)

        # Wait for the thread to finish
        t.join()

    return stream_response

print("Building generator...")
model_name = "meta-llama/Llama-2-70b-chat-hf"
respond = build_generator(model_name=model_name, auth_token=auth_token)

print("Starting server...")
title = f"ChatUbix 70B" #model_name.split("/")[-1].replace("-", " ") + " local"
desc = f"This Space demonstrates ChatUBIX by UBIX labs."  # f"This Space demonstrates [{model_name}](https://huggingface.co/{model_name}) by Meta."
css = """.toast-wrap { display: none !important } """

ci = gr.ChatInterface(respond, title=title.title(), description=desc, css=css)
ci.queue().launch(inline=False, share=True)#ci.queue().launch(inline=True, share=True)

import gradio as gr
import requests


def get_official_answer(question:str, history):
    url = "http://colossal-ai:5000/official/chat"
    data = {
        "question": question,
    }
    response = requests.post(url, data=data)
    return response.text


def get_answer(question:str, history):
    url = "http://localhost:5000/chat"
    data = {
        "question": question,
    }
    response = requests.post(url, data=data)
    return response.text


if __name__ == '__main__':
    with gr.Blocks() as demo:
        gr.Markdown("Chat Demo")
        with gr.Tab("Q&A with router"):
            gr.ChatInterface(get_answer)
        with gr.Tab("Official Q&A"):
            gr.ChatInterface(get_official_answer)

    demo.launch(server_name='0.0.0.0', server_port=7860, debug=True, share=True)

""""
nohup python -u main_gradio.py > gradio.log 2>&1&
"""

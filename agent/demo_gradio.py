import gradio as gr
from agent.zero_short import get_answer

def greet(question, history):
    return get_answer(question)


if __name__ == '__main__':
    gr.ChatInterface(greet).launch(share=True, server_name='0.0.0.0')



"""
CUDA_VISIBLE_DEVICES=0,1,2,3 PYTHONPATH=. python agent/demo_gradio.py
"""

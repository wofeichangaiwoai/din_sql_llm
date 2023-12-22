import gradio as gr

def greet(name, history):
    return "Hello, " + name + "!"

def greet2(name, history):
    return "Official hello, " + name + "!"

if __name__ == '__main__':
    with gr.Blocks() as demo:
        gr.Markdown("Flip text or image files using this demo.")
        with gr.Tab("Q&A with route"):
            gr.ChatInterface(greet)
        with gr.Tab("Official Q&A"):
            gr.ChatInterface(greet2)

    demo.launch(server_name='0.0.0.0')



# import random
# 
# def random_response(message, history):
#     return random.choice(["Yes", "No"])
# 
# 
# import gradio as gr
# 
# gr.ChatInterface(random_response).launch()

""""
python test/gradio_test.py
"""

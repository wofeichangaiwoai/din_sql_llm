from datetime import datetime

import gradio as gr

from route.router import route_meta, default_chain
from ubix.chain.chain_route import get_route_chain
from ubix.common.llm import llm

def get_answer(question:str, history):
    start_route = datetime.now()
    route_name = get_route_chain(llm).run(str(question))
    route_name = route_name if route_name in route_meta else "DEFAULT"
    start = datetime.now()
    duration_route = (start-start_route).total_seconds()
    print(f'>>>: Begin ask <{route_name}> about question: <{question}>, route cost:{duration_route} sec')
    if route_name in route_meta:
        answer = route_meta[route_name].run(question)
    else:
        answer = default_chain.run(question)
    end = datetime.now()
    duration = (end-start).total_seconds()
    print(f'>>>: End ask <{route_name}> about question <{question}>, cost:{duration} sec, answer: {answer}')
    return answer


if __name__ == '__main__':
    gr.ChatInterface(get_answer).launch(server_name='0.0.0.0', server_port=5000, debug=True, share=True)

""""
CUDA_VISIBLE_DEVICES=0,1,2,3 nohup python -u main.py 2>&1&
"""

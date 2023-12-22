nohup jupyter notebook --allow-root --no-browser --ip=0.0.0.0 --notebook-dir="/Workspace/" --NotebookApp.token='3d1e688e88aba5d81bc5bd1b3452d65b3820fbaa442b2788' &
PYTHONPATH=. nohup python main_gradio.py >> gradio.log 2>&1&
: "${LLM_TYPE:=tgi}"
CUDA_VISIBLE_DEVICES=0,1 LLM_TYPE=${LLM_TYPE} nohup python -u main_api.py >> api.log 2>&1&
tail -f /dev/null

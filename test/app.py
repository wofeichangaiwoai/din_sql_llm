
from fastapi import FastAPI, Request
from InstructorEmbedding import INSTRUCTOR

import uvicorn, json, datetime
import torch

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE

def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

app = FastAPI()


@app.post("/")
async def create_item(request: Request):
    global model
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list[0]
    
    instruction = "Represent the Science title:"
    embedding = model.encode([[instruction, prompt]])
    torch_gc()
    answer = {
            "response": embedding.tolist()
            }
    
    return answer


if __name__ == '__main__':
    model = INSTRUCTOR("hkunlp/instructor-xl")
    model.eval()
    uvicorn.run(app, host='0.0.0.0', port=8000, workers=1)
    #uvicorn.run(app, host='https://embed-api.home-dev.ubix.io', workers=1)

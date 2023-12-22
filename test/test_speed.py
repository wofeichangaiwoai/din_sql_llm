from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp
import datetime
from time import perf_counter
import torch

n_gpu_layers = 80  # Metal set to 1 is enough.
n_batch = 512  # Should be between 1 and n_ctx, consider the amount of RAM of your Apple Silicon Chip.
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Make sure the model path is correct for your system!

llm = LlamaCpp(
    model_path="/Workspace/yamada/pretrain/Llama-2-13B-chat-GGML/llama-2-13b-chat.ggmlv3.q4_0.bin",
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    n_ctx=300,
    f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
    callback_manager=callback_manager,
    verbose=True,
)
for _ in range(1):
    llm.predict("how many records are there in this table?")

query = "what is machine learning"
latencies = []
for i in range(10):
    torch.cuda.synchronize()
    start_time = perf_counter()
    if i == 1:
        query = "what is the minimum total in this table?"
    result = llm.predict(query)
    print(result.split("\n")[0])
    torch.cuda.synchronize()
    latency = perf_counter() - start_time
    latencies.append(latency)
time_avg_ms = 1000 * np.mean(latencies)
time_std_ms = 1000 * np.std(latencies)
time_p95_ms = 1000 * np.percentile(latencies,95)
print( f"P95 latency (ms) - {time_p95_ms}; Average latency (ms) - {time_avg_ms:.2f} +\- {time_std_ms:.2f};", time_p95_ms)

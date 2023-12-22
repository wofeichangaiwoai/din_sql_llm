from vllm import LLM, SamplingParams
import datetime
import torch
import sys

param = sys.argv[5]

sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_tokens=100)
llm = LLM(model="NousResearch/Llama-2-13b-chat-hf", tensor_parallel_size=2)


print("*********************")
path = "prompt/easy_prompt.txt"
easy_prefix = ""
with open(path) as f:
        for line in f:
            easy_prefix += line

text = "what is the maximum and average totalamountlocal in last ten years"
prompt = easy_prefix + 'Q: "' + text + '\nSchema_links: ' + param + '\nSQL:'

starttime = datetime.datetime.now()
outputs = llm.generate(prompt, sampling_params)

print("origin text:", text, "\n")
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print("===========")
    print("sql:",generated_text.split("\n")[0])
    print("===========")
endtime = datetime.datetime.now()
print(endtime-starttime)
print("\n\n")



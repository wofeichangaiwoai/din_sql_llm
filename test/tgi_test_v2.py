import uuid
import threading
from ubix.common.huggingface_text_gen_inference_ex import HuggingFaceTextGenInferenceEx

llm = HuggingFaceTextGenInferenceEx(
    max_new_tokens=10,
    #top_k=10,
    #top_p=0.95,
    #typical_p=0.95,
    temperature=0.01,
    #repetition_penalty=1.03,
)
print(llm.predict("hello"))

print(llm.predict("hello"))

"""
python test/tgi_test_v2.py
"""

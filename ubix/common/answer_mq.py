from ubix.bk.mq import fsend
from ubix.common.answer import *

if __name__ == '__main__':
    for _ in tqdm(range(1), desc="Answer testing"):
        question_list = [
            ("list the data with cardcode C40000 in this table", "download"),
            ("what is the average totalamountlocal for last ten years? startdate", "query"),
            ("what is the average totalamountlocal with cardcode C40000 in this table", "query"),
            # ("what is the cardcode in this table with average totalamountlocal higher than 30000", "auto"),
            ("what is the average totalamountlocal in this table whose cardcode contains 'C400'", "auto"),
        ]
        for question, query_type in question_list:
            fsend.send_forward(question)
"""
✅ PYTHONPATH=. LLM_TYPE=din python -u ubix/cmq/freceive.py
✅ PYTHONPATH=. LLM_TYPE=din python -u ubix/cmq/breceive.py
"""
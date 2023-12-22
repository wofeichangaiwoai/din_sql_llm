import langchain as lc
from langchain import OpenAI
import os
# from langchain_experimental.sql import SQLDatabaseChain
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import PromptTemplate, LLMChain
from sqlalchemy import create_engine
import sqlalchemy as db
from pyhive import hive

os.environ['CUDA_VISIBLE_DEVICES']='0'
host = "hive-hiveserver"
port = 10000
os.environ["OPENAI_API_KEY"] = "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"
engine = create_engine(f'hive://hive-hiveserver:10000/default?auth=NOSASL')

con = engine.connect()
print("===start=====")
metadata = db.MetaData()
print(metadata)
ResultProxy = con.execute("select * from linear_regression_2 limit 2;")

print(ResultProxy.fetchall())

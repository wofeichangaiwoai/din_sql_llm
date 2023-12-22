import langchain as lc
import os

from langchain.agents import Tool, initialize_agent
# from langchain_experimental.sql import SQLDatabaseChain
# site-packages\langchain_experimental\sql\base.py
# /opt/conda/lib/python3.9/site-packages/langchain_experimental/sql/base.py
from sqlalchemy import processors, create_engine

port = 10000
include_tables = ["test_del"]
from langchain import  OpenAI, SQLDatabase
try:
    from langchain import SQLDatabaseChain, LlamaCpp, OpenAI
except Exception as e:
    from langchain_experimental.sql import SQLDatabaseChain
db = SQLDatabase(create_engine("hive://localhost:10000/abc?auth=NOSASL"), include_tables=include_tables)
db_chain = SQLDatabaseChain(llm=OpenAI(), database=db, top_k=3, return_direct=True)


db_tool = Tool(
    name='Query Info about Data',
    func=db_chain.run,
    description='Query Info about Data in table, Hive or Spark'
)

tools = [db_tool]

llm = OpenAI(temperature=0)
zero_shot_agent = initialize_agent(
    agent="zero-shot-react-description",
    tools=tools,
    llm=llm,
    verbose=True,
)

result = zero_shot_agent("how many rows are there in the table test_del?")

print(f'result:{result}')

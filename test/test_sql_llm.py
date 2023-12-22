import langchain as lc
from langchain import OpenAI, PromptTemplate
import os
from langchain_experimental.sql import SQLDatabaseChain

host = "hive-hiveserver"
port = 10000
os.environ["OPENAI_API_KEY"] = "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"
include_tables = ["test_del"]
con = lc.SQLDatabase.from_uri("hive://hive-hiveserver:10000/abc?auth=NOSASL", include_tables = include_tables, schema="abc")

prompt = '''
Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer. Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question. do not include semicolon in the end of the sql

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

Only use the following tables:
{table_info}

Question: {input}
'''


llm = OpenAI(temperature=0)
db_chain = SQLDatabaseChain.from_llm(llm=llm, db=con, verbose=True, prompt=PromptTemplate.from_template(prompt))
query = "how many records are there in this table?"
#query = "describe the test_del table"
db_chain.run(query)

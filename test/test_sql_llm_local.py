from typing import Optional, Any, Dict
from uuid import UUID

import langchain as lc
from langchain import LlamaCpp, OpenAI
try:
    from langchain import SQLDatabaseChain
except Exception as e:
    from langchain_experimental.sql import SQLDatabaseChain

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
# from langchain_experimental.sql import SQLDatabaseChain
# site-packages\langchain_experimental\sql\base.py
# /opt/conda/lib/python3.9/site-packages/langchain_experimental/sql/base.py
from sqlalchemy import processors


import re
class SQLEnhancementHandler(BaseCallbackHandler):
    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any,
    ) -> Any:
        sql_cmd = response.generations[0][0].text
        response.generations[0][0].text = re.sub(r';$', '', sql_cmd)


port = 10000
#os.environ["OPENAI_API_KEY"] = "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"
include_tables = ["test_del"]
con = lc.SQLDatabase.from_uri("hive://localhost:10000/abc?auth=NOSASL", include_tables = include_tables, schema="abc")
#con = lc.SQLDatabase(engine)
llm = OpenAI(temperature=0)
llm.callbacks=[SQLEnhancementHandler()]
db_chain = SQLDatabaseChain.from_llm(llm=llm, db=con, verbose=True,
 #prompt=PromptTemplate.from_template(prompt)
 )
query = "how many records are there in this table?"
#query = "describe the test_del table"
db_chain.run(query)

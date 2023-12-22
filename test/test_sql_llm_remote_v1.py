from typing import Optional, Any, Dict
from uuid import UUID

import langchain
import langchain as lc
from langchain import LlamaCpp, OpenAI
from langchain.cache import InMemoryCache
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.utilities import SQLDatabase
from sqlalchemy import create_engine

from ubix.common.llm import get_llm

try:
    from langchain import SQLDatabaseChain
except Exception as e:
    from langchain_experimental.sql import SQLDatabaseChain

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult


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
include_tables = ["breast_cancer_new"]

hive_host = "trino"
port = 8080
user_name = "hive"
catalog="hive"
hive_database = "default"

from trino.sqlalchemy import URL
engine = create_engine(
    URL(
        host=hive_host,
        port=port,
        user=user_name,
        catalog=catalog,
        schema=hive_database,
    ),
)

sql_db = SQLDatabase(engine, schema="default", include_tables=include_tables)

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
langchain.llm_cache = InMemoryCache()
llm = get_llm()

llm.callbacks=[SQLEnhancementHandler()]
db_chain = SQLDatabaseChain.from_llm(llm=llm, db=sql_db,
                                     top_k=1,
                                     verbose=True,

 #prompt=PromptTemplate.from_template(prompt)
 )
query = "how many records are there in this table?"
#query = "describe the test_del table"
db_chain.run(query)


"""
CUDA_VISIBLE_DEVICES=0,1,2,3 python test/test_sql_llm_remote_v1.py
"""

from typing import Optional, Any, Dict
from uuid import UUID

import langchain as lc
from langchain import LlamaCpp, OpenAI
from langchain.utilities import SQLDatabase

from ubix.chain.sql.sql_base import SQLDatabaseChainEx, SQLDatabaseEx
from ubix.common.llm import get_llm

try:
    from langchain import SQLDatabaseChain
except Exception as e:
    from langchain_experimental.sql import SQLDatabaseChain
import os

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
# from langchain_experimental.sql import SQLDatabaseChain
# site-packages\langchain_experimental\sql\base.py
# /opt/conda/lib/python3.9/site-packages/langchain_experimental/sql/base.py
from sqlalchemy import processors, create_engine

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
# include_tables = ["breast_cancer_new"]

hive_host = "trino"
port = 8080
user_name = "hive"
catalog="hive"
include_tables = ["salesopportunities"]
hive_database = "65057500bed4c2ac869fe964"

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

sql_db = SQLDatabaseEx(engine, schema=hive_database, include_tables=include_tables)

llm = get_llm()
llm.callbacks=[SQLEnhancementHandler()]
db_chain = SQLDatabaseChainEx.from_llm(llm=llm, db=sql_db, verbose=True,
 #prompt=PromptTemplate.from_template(prompt)
 )
query = "how many records are there in this table?"
#query = "describe the test_del table"
db_chain.run(query)

"""
python test/test_sql_llm_remote_v2.py
"""
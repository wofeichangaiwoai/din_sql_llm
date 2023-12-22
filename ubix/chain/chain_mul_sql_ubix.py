from datetime import datetime
from functools import lru_cache
from typing import Any 
import re

import langchain
import torch
from langchain.cache import InMemoryCache
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.schema import LLMResult
from pydantic import Extra
from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
from langchain import LlamaCpp, OpenAI
from trino.sqlalchemy import URL

from ubix.common.llm import get_llm

try:
    from langchain import SQLDatabaseChain
except Exception as e:
    from langchain_experimental.sql import SQLDatabaseChain


class SQLEnhancementHandler(BaseCallbackHandler):
    def on_llm_end(
            self,
            response: LLMResult,
            **kwargs: Any,
    ) -> Any:
        sql_cmd = response.generations[0][0].text
        response.generations[0][0].text = re.sub(r';$', '', sql_cmd)

def create_multi_table(table_columns, include_tables, query):
    """
        create a custom table to reduce the reduclant column
        table_info_original: origninal table schema
        include_tables: table name
        query: use query to choose the most relevant column
     
    """
    custom_table_info = {}
    query_list = query.split(" ")
    for index in range(len(table_columns)):
        table_name = include_tables[index]    
        prefix = "CREATE TABLE " + table_name + " ("
        mid = ""
        for item in table_columns[index]:
                if item in query_list:
                   mid += item + ","
        last = ")"
        custom_table_info[table_name] = prefix + mid + last
    return custom_table_info

def get_db_chain(llm):
    import langchain as lc

    include_tables = ["customer_invoice_header", "customer_invoice_item"]
    hive_host = "trino"
    port = 8080
    user_name = "hive"
    catalog="hive"
    hive_database = "63bd509c8cb02db7e453ad27"

    engine = create_engine(
                        URL(
                             host=hive_host,
                             port=port,
                             user=user_name,
                             catalog=catalog,
                             schema=hive_database,
                            ),
                        )
    query = "Sum the total in table customer_invoice_item whose associated table customer_invoice_header's billing_organization is '00163E6A-610A-1EE9-91CE-E786A927A44A' and common field is postal_code . table customer_invoice_item don't contain field billing_organization "
    connetion = engine.connect()

    metadata = MetaData()

    table_header = Table(include_tables[0], metadata, autoload=True, autoload_with=engine)
    table_columns_header = table_header.columns.keys()
    table_item = Table(include_tables[1], metadata, autoload=True, autoload_with=engine)
    table_columns_item = table_item.columns.keys()
    table_columns_list = [table_columns_header, table_columns_item]

    custom_table_info = create_multi_table(table_columns_list, include_tables, query)
    con_custom = lc.SQLDatabase(engine, include_tables=include_tables, custom_table_info=custom_table_info)
    llm.callbacks=[SQLEnhancementHandler()]
    db_chain = SQLDatabaseChain.from_llm(llm=llm, db=con_custom, verbose=True)
    return db_chain


if __name__ == "__main__":
    llm = get_llm()

    print(datetime.now())

    agent = get_db_chain(llm)
    query = "Sum the total in table customer_invoice_item whose associated table customer_invoice_header's billing_organization is '00163E6A-610A-1EE9-91CE-E786A927A44A' and common field is postal_code . table customer_invoice_item don't contain field billing_organization "
    agent.run(query)
    print(datetime.now())

"""
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=. python ubix/chain/chain_mul_sql_ubix.py
"""

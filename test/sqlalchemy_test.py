from sqlalchemy import create_engine

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

connection = engine.connect()
cursor = connection.execute("select count(t.target) as a from breast_cancer_new t")
if cursor.returns_rows:
    result = cursor.fetchall()
print(result)

"""
python test/sqlalchemy_test.py
"""

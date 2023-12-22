from pyhive import hive
import pandas as pd

hive_host = "hive-hiveserver"

conn = hive.Connection(host=hive_host, port=10000, auth="NOSASL")
cursor = conn.cursor()




sql = "select * from default.linear_regression_2"
df = pd.read_sql(sql, conn)
print(df.shape, df.head())


"""
python test/hive_test.py
"""
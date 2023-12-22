from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
from trino.sqlalchemy import URL
from sqlalchemy.sql.expression import select, text

new_database = "65057500bed4c2ac869fe964"
engine = create_engine(
                        URL(
                             host="trino",
                             port=8080,
                             user="hive",
                             catalog="hive",
                             schema=new_database,
                            ),
                        )
connection = engine.connect()

rows = connection.execute(text("show tables")).fetchall()
wpath = "folder1/"
for item in rows:
    table_name = item[0]
    with open(wpath + table_name + ".txt", "w") as fp:
        columns_l = []
        columns = connection.execute("SHOW COLUMNS FROM {}".format(table_name)).fetchall()
        for column in columns:
            columns_l.append(column[0])
        fp.write(str(columns_l))



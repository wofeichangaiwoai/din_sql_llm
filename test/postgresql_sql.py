## 导入psycopg2包
import psycopg2


def test_table():
    ## 连接到一个给定的数据库
    db_host = "localhost"
    db_host = "data-service-backoffice-postgresql-data-service"
    conn = psycopg2.connect(
        database="ubix_data_service",
        user="dataflow",
        password="dataflow@ubix",
        host=db_host,
        port="5432",
    )
    ## 建立游标，用来执行数据库操作
    cursor = conn.cursor()

    ## 执行SQL SELECT命令
    cursor.execute(
        "select solution_id, model_pipeline_json::json from model_pipeline where model_pipeline_json is not null"
    )

    ## 获取SELECT返回的元组
    row = cursor.fetchone()

    model_pipeline_col = row[1]
    print(model_pipeline_col.get("targetdata"))

    ## 关闭游标
    cursor.close()

    ## 关闭数据库连接
    conn.close()


if __name__ == "__main__":
    test_table()


"""
python test/postgresql_sql.py
"""

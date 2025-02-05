from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import pandas as pd
from time import time
from sqlalchemy import create_engine

def create_table(file_csv_gz, table_name):
    user = "postgres"
    password = "postgres"
    host = "postgres_db"
    port = "5432"
    db = "ny_taxi"
    # establish DB connection
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()
    df_iter = pd.read_csv(file_csv_gz, iterator=True, chunksize=10)

    # next 10 rows
    df = next(df_iter)

    # convert to datetime
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    # create empty table
    try:
        df.head(n=0).to_sql(name=table_name, con=engine, if_exists='fail')
        return
    except ValueError:
        print(f"Table {table_name} already exists")
        return

def ingest_to_local_db(file_csv_gz, table_name):
    user = "postgres"
    password = "postgres"
    host = "postgres_db"
    port = "5432"
    db = "ny_taxi"
    # establish DB connection
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()
    df_iter = pd.read_csv(file_csv_gz, iterator=True, chunksize=100000)

    # next 100000 rows
    df = next(df_iter)

    # convert to datetime
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    # create empty table
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    rows_count = 0
    while True:

        try:
            df.to_sql(name=table_name, con=engine, if_exists='append')
            rows_count += len(df)
            df = next(df_iter)
            df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
            df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)


        except StopIteration: # handling the end of the iterator
            print(f"Finished ingesting data into the postgres database, {rows_count} rows inserted")
            break







csv_data_ingest = DAG(
    "csv_data_ingest_to_db",
    params = {
        "DATE": "2019-01",
    }
    #schedule_interval="0 6 2 * *",
    #start_date=datetime(2021, 1, 1)
)

date = '{{ execution_date.strftime(\'%Y-%m\') }}'
LINK_PREFIX = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_"
OUT_FILE = "green_taxi_"
FORMAT = ".csv.gz"
DATE = "{{ params.DATE }}"
with csv_data_ingest:


    download_task = BashOperator(
        task_id='download_csv',
        bash_command=f'curl -sSL {LINK_PREFIX + DATE + FORMAT} > {OUT_FILE + DATE}' +  FORMAT,
        cwd= "{{ dag_run.dag.folder }}"
    )

    create_table = PythonOperator(
        task_id='create_all_trips_table',
        python_callable=create_table,
        #cwd="{{ dag_run.dag.folder }}",
        op_kwargs=dict(
            file_csv_gz = "{{dag_run.dag.folder }}" + "/" + OUT_FILE + DATE + FORMAT,
            table_name = "all_trips"
        )
    )

    migrate_task = PythonOperator(
        task_id='csv_to_temp_table',
        python_callable=ingest_to_local_db,
        #cwd="{{ dag_run.dag.folder }}",
        op_kwargs=dict(
            file_csv_gz = "{{dag_run.dag.folder }}" + "/" + OUT_FILE + DATE + FORMAT,
            table_name = "temp_table"
        )
    )

    append_to_table = SQLExecuteQueryOperator(
        task_id="append_to_all_trips_table",
        conn_id = "local_postgres_db",
        sql="""
            INSERT INTO all_trips SELECT * FROM temp_table;
          """
    )
    delete_table = SQLExecuteQueryOperator(
        task_id="delete_temp_table",
        conn_id = "local_postgres_db",
        sql="""
            DROP TABLE temp_table;
          """
    )

    delete_task = BashOperator(
        task_id='delete_csv',
        bash_command= f"rm {OUT_FILE}" + DATE + FORMAT,
        cwd = "{{ dag_run.dag.folder }}"
    )


    download_task >>create_table >> migrate_task >> append_to_table >> [delete_table, delete_task]





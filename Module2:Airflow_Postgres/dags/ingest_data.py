from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import pandas as pd
from time import time
from datetime import datetime
from sqlalchemy import create_engine
import os


# PG_USER = "postgres"
# PG_PASSWORD = "postgres"
# PG_HOST = "postgres_db"
# PG_PORT = "5432"
# PG_DATABASE = "ny_taxi"

PG_HOST = os.getenv('PG_HOST')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_PORT = os.getenv('PG_PORT')
PG_DATABASE = os.getenv('PG_DATABASE')

def create_table(file_csv_gz, table_name, *args):
    user, password, host, port, db = args

    # establish DB connection
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()
    df = pd.read_csv(file_csv_gz, nrows=2)

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

def ingest_to_local_db(file_csv_gz, table_name, *args):
    user, password, host, port, db = args

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
    "csv_data_ingest_to_dby",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2019, 1, 1), # DAG executed at the end of each scheduled interval
    end_date = datetime(2019,5,1,),
    max_active_runs = 4,
    catchup = True
)

date = '{{ execution_date.strftime(\'%Y-%m\') }}'
LINK_PREFIX = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_"
OUT_FILE = "green_taxi_"
FORMAT = ".csv.gz"
DATE = "{{ execution_date.strftime(\'%Y-%m\') }}"
with csv_data_ingest:
    download_task = BashOperator(
        task_id='download_csv',
        bash_command=f'curl -sSL {LINK_PREFIX + DATE + FORMAT} > {OUT_FILE + DATE}' +  FORMAT,
        cwd= "{{ dag_run.dag.folder }}"
    )

    create_table = PythonOperator(
        task_id='create_all_trips_table',
        python_callable=create_table,
        op_args=[
            "{{dag_run.dag.folder }}" + "/" + OUT_FILE + DATE + FORMAT,
            "all_trips",
            PG_USER,
            PG_PASSWORD,
            PG_HOST,
            PG_PORT,
            PG_DATABASE
        ]
    )

    migrate_task = PythonOperator(
        task_id='csv_to_temp_table',
        python_callable=ingest_to_local_db,
        op_args=[
            "{{dag_run.dag.folder }}" + "/" + OUT_FILE + DATE + FORMAT,
            "temp_table_" + DATE.replace("-", "_"),
            PG_USER,
            PG_PASSWORD,
            PG_HOST,
            PG_PORT,
            PG_DATABASE
        ]
    )

    append_to_table = SQLExecuteQueryOperator(
        task_id="append_to_all_trips_table",
        conn_id = "local_postgres_db",
        sql=f"""
            INSERT INTO all_trips SELECT * FROM {"temp_table_"+DATE.replace("-", "_")};
          """
    )
    delete_table = SQLExecuteQueryOperator(
        task_id="delete_temp_table",
        conn_id = "local_postgres_db",
        sql=f"""
            DROP TABLE {"temp_table_" + DATE.replace("-", "_")};
          """
    )

    delete_task = BashOperator(
        task_id='delete_csv',
        bash_command= f"rm {OUT_FILE}" + DATE + FORMAT,
        cwd = "{{ dag_run.dag.folder }}"
    )


    download_task >>create_table >> migrate_task >> append_to_table >> [delete_table, delete_task]





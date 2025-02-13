FROM apache/airflow:2.10.4-python3.8
#python3.8 for pscycopg2
ADD requirements.txt .
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt

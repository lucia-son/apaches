from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.python_operator import PythonOperator

from custom.young.kafka_producer import kafka_producer_main
from custom.young.kafka_create_topic import kafka_create_topic_main

start_date = datetime(2023, 10, 31)

default_args = {
    'owner': 'airflow',
    'start_date': start_date,
    'retries': 2,
    'retry_delay': timedelta(seconds=5)
}


def decide_branch():
    print("decide_branch function started")
    create_topic = kafka_create_topic_main()
    if create_topic == "Created":
        print("topic has been created")
        return "topic_created"
    else:
        print("topic already exists")
        return "topic_already_exists"

with DAG('airflow_kafka_mysql_psql', default_args=default_args, schedule_interval='*/20 * * * *', catchup=False) as dag:

    create_new_topic = BranchPythonOperator(task_id='create_new_topic', python_callable=decide_branch)
    
    topic_created = EmptyOperator(task_id="topic_created")

    topic_already_exists = EmptyOperator(task_id="topic_already_exists")
     
    kafka_producer = PythonOperator(task_id='kafka_producer', python_callable=kafka_producer_main,
                             retries=2, retry_delay=timedelta(seconds=10),
                             execution_timeout=timedelta(seconds=45))


    create_new_topic >> [topic_created, topic_already_exists] >> kafka_producer

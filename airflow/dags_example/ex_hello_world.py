import pendulum
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


kst = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner' : 'Hello World',
    'email' : ['airflow@airflow.com'],
    'email_on_failure': False,
}

with DAG(
    dag_id='ex_hello_world',
    default_args=default_args,
    start_date=datetime(2023, 10, 30, tzinfo=kst),
    description='print hello world',
    schedule_interval='@once',
    tags=['test']
) as dag:

    def print_hello():
        print('hello world')

    t1 = DummyOperator(
        task_id='dummy_task_id',
        retries=5,
    )

    t2 = PythonOperator(
        task_id='Hello_World',
        python_callable=print_hello
    )

    t1 >> t2

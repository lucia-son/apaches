from __future__ import annotations
import functools
import json
import logging
from datetime import datetime, timedelta

from airflow import DAG

from airflow.operators.python import PythonOperator
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator

default_args = {
    "owner": "airflow",
    "depend_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG('kafka_integration', default_args=default_args, schedule_interval=None)

def load_connections(): 
  from airflow.models import Connection
  from airflow.utils import db

  db.merge_conn(
      Connection(
          conn_id="k_01",
          conn_type="kafka",
          extra=json.dumps(
              {
                  "socket.timeout.ms": 100, 
                  "bootstrap.servers": "192.168.137.105:30010"
              }
          ),
       )
  )

  db.merge_conn(
      Connection(
          conn_id="k_02",
          conn_type="kafka",
          extra=json.dumps(
              {
                  "bootstrap.servers": "192.168.137.105:30010",
                  "group.id": "k_02",
                  "enable.auto.commit": False,
                  "auto.offset.reset": "beginning"
              }
          ),
       )
  )


def producer_function():
    for i in range(20):
        yield (json.dumps(i), json.dumps(i+1))

consumer_logger = logging.getLogger("airflow")

def consumer_function(message, prefix=None):
    key = json.loads(message.key())
    value = json.loads(message.value())
    consumer_logger.info(f"{prefix} {message.topic()} @ {message.offset()}; {key} : {value}")
    return


def hello_kafka():
    print("Hello Kafka!")
    return

with DAG(
    "kafka-example",
    default_args=default_args,
    description="Kafka Operators",
    schedule=timedelta(days=1),
    start_date=datetime(2023, 10, 1),
    catchup=False,
    tags=["test"],
) as dag:

  t0 = PythonOperator(task_id="load_connections", python_callable=load_connections)

  t1 = ProduceToTopicOperator(
        kafka_config_id="k_01",
        task_id="produce_to_topic",
        topic="airflow-kafka-test-01",
        producer_function="kafka_conn.producer_function"
    )
   
  t2 = ProduceToTopicOperator(
        kafka_config_id="k_01",
        task_id="produce_to_topic_2",
        topic="airflow-kafka-test-02",
        producer_function="kafka_conn.producer_function"
    )

t0 >> t1
t0 >> t2

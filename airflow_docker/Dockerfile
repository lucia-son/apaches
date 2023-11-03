FROM apache/airflow:2.6.2

COPY /dags ./dags
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

USER airflow
EXPOSE 8080
EXPOSE 8793
EXPOSE 5555

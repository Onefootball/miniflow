from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.kubernetes_pod_operator import (
    KubernetesPodOperator
)

default_args = {
    'owner': 'airflow',
    'depends_on_past': True,
    'start_date': datetime(2020, 1, 1),
    'retries': 1
}

dag = DAG(
        dag_id='airflow_example_dag_v5',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=True)


with dag:

    task_get_chuck_fact = KubernetesPodOperator(
        namespace='airflow',
        name="task-get-chuck-fact", # K8 doesn't support "_" here.
        task_id="task_get_chuck_fact",  
        image="rodrigodelmonte/airflow-sample-task",
        # cmds=["python"], It's the ENTRYPOINT !!!
        arguments=[
            "cowsay_chuck_norris.py", "{{ ds }}"
        ],
        is_delete_operator_pod=False,
        get_logs=True,
        dag=dag
    )

    yesterday_date = KubernetesPodOperator(
        namespace='airflow',
        name="yesterday-date",
        task_id="yesterday_date",
        image="python:3.7",
        cmds=["python", "-c"],
        arguments=[
            "print('{{ yesterday_ds }}')"
        ],
        is_delete_operator_pod=True,
        get_logs=True,
        dag=dag
    )

    tomorrow_date = KubernetesPodOperator(
        namespace='airflow',
        name="tomorrow-date",
        task_id="tomorrow_date",
        image="python:3.7",
        cmds=["python", "-c"],
        arguments=[
            "print('{{ tomorrow_ds }}')"
        ],
        is_delete_operator_pod=True,
        get_logs=True,
        dag=dag
    )

    the_end = BashOperator(
        task_id="the_end",
        bash_command="echo 'The End!'",
        dag=dag
    )

    task_get_chuck_fact >> [yesterday_date, tomorrow_date] >> the_end

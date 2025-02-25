import os

from airflow import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from pandas import DataFrame
from pathlib import Path
from sqlalchemy import create_engine
from typing import Dict

from src import config
from src.extract import extract
from src.load import load
from src.plotz import plot_delivery_date_difference
from src.plotz import plot_order_amount_per_day_with_holidays
from src.transform import run_queries

from dags.config import default_args
from dags.helpers import dag_success_notification
from dags.helpers import task_failure_notification


def dag_success_callback(context):
  success_msg = dag_success_notification(context=context)
  success_alert = PythonOperator(
    context=context,
    task_id="success_notification",
    python_callable=lambda: print(success_msg),
  )
  return success_alert.execute(context=context)

def task_failure_callback(context):
  failure_msg = task_failure_notification(context=context)
  failed_alert = PythonOperator(
    context=context,
    task_id="failure_notification",
    python_callable=lambda: print(failure_msg),
  )
  return failed_alert.execute(context=context)

def task_extract(ti: TaskInstance) -> Dict[str, DataFrame]:
  print("Extracting data from csv files and holidays' REST API to load them into dataframes")
  csv_folder = config.DATASET_ROOT_PATH
  public_holidays_url = config.PUBLIC_HOLIDAYS_URL
  csv_table_mapping = config.get_csv_to_table_mapping()
  ti.xcom_push(key="extract_data", value=extract(csv_folder, csv_table_mapping, public_holidays_url))

def task_load(ti: TaskInstance) -> None:
  csv_dataframes: Dict[str, DataFrame] = ti.xcom_pull(key="extract_data", task_ids="task_extract")
  if not os.path.exists(config.SQLITE_BD_ABSOLUTE_PATH):
    print("Creating Storing all dataframes in the SQLite Data Warehouse")
    Path(config.SQLITE_BD_ABSOLUTE_PATH).touch()
    ENGINE = create_engine(rf"sqlite:///{config.SQLITE_BD_ABSOLUTE_PATH}", echo=False)
    load(data_frames=csv_dataframes, database=ENGINE)
  else:
    print("Storing all dataframes in the SQLite Data Warehouse")

def task_transform(ti: TaskInstance) -> None:
  print("Quering data from DB and transforming it")
  ENGINE = create_engine(rf"sqlite:///{config.SQLITE_BD_ABSOLUTE_PATH}", echo=False)
  ti.xcom_push(key="transform_data", value=run_queries(database=ENGINE))

def task_generate_plots(ti: TaskInstance):
  df = Dict[str, DataFrame] = ti.xcom_pull(key="transform_data", task_ids="task_transform")
  print("Generating plots")
  plot_delivery_date_difference(df, 'plot_delivery_date_difference.png')
  plot_order_amount_per_day_with_holidays(df, 'plot_order_amount_per_day_with_holidays.png')


with DAG(
  dag_id="sprint1_elt",
  start_date=datetime(year=2024, month=1, day=1, hour=9, minute=0),
  schedule="@daily",
  catchup=False,
  on_failure_callback=task_failure_callback,
  default_args=default_args,
  max_active_runs=1,
  render_template_as_native_obj=True
) as dag:
  start_execution = DummyOperator(task_id="start_execution")
  end_execution = DummyOperator(task_id="end_execution")
  
  extract_data = PythonOperator(
    dag=dag,
    task_id="task_extract",
    python_callable=task_extract
  )
  load_data = PythonOperator(
    dag=dag,
    task_id="task_load",
    python_callable=task_load,
  )
  transform_data = PythonOperator(
    dag=dag,
    task_id="task_transform",
    python_callable=task_transform,
  )
  show_data = PythonOperator(
    dag=dag,
    task_id="task_generate_plots",
    python_callable=task_generate_plots,
  )

  # Set dependencies between tasks
  start_execution >> extract_data >> load_data >> transform_data >> show_data >> end_execution

import os

from datetime import timedelta

# Default args
SERVICE_USER = os.getenv("USER")
AIRFLOW_HOME = '/Users/rafaelgarcia/Work/anyone-ai/Sprint-1'

default_args = {
    "depends_on_past": False,
    "max_active_runs": 1,
    "owner": "rafaelcgarciaa",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
    "run_as_user": SERVICE_USER,
    "wait_for_downstream": False,
    "on_success_callback": None
}
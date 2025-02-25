def task_failure_notification(context):
  task_id = context.get("task_instance").task_id
  dag_id = context.get("task_instance").dag_id
  exec_date = context.get("execution_date")
  log_url = context.get("task_instance").log_url
  return f""":alert:  Task Failed. <!here>
  *Task*: {task_id}  
  *Dag*: {dag_id} 
  *Execution Time*: {exec_date}  
  *Log Url*: {log_url}
  """


def dag_success_notification(context):
  dag_id = context.get("task_instance").dag_id
  exec_date = context.get("execution_date")
  log_url = context.get("task_instance").log_url
  return f""":white_check_mark: Dag Finished Successfully!
  *Dag*: {dag_id} 
  *Execution Time*: {exec_date}  
  *Log Url*: {log_url} 
  """

from typing import Dict

import requests
from pandas import DataFrame, read_csv, to_datetime


def get_public_holidays(public_holidays_url: str, year: str) -> DataFrame:
  """Get the public holidays for the given year for Brazil.

  Args:
    public_holidays_url (str): url to the public holidays.
    year (str): The year to get the public holidays for.

  Raises:
    SystemExit: If the request fails.

  Returns:
    DataFrame: A dataframe with the public holidays.
  """
  url = f'{public_holidays_url}/{year}/BR'
  try:
    r = requests.get(url, timeout=10, verify=True)
    r.raise_for_status()
  except requests.exceptions.HTTPError as errh:
    raise SystemExit(f'HTTP error occurred: {errh}')
  except requests.exceptions.ReadTimeout as errrt: 
    raise SystemExit(f'Timeout error occurred: {errrt}') 
  except requests.exceptions.ConnectionError as conerr: 
    raise SystemExit(f'Connection error occurred: {conerr}') 
  except requests.exceptions.RequestException as errex: 
    raise SystemExit(f'Request error occurred: {errex}')
  data = r.json()
  df = DataFrame(data).drop(columns=['types', 'counties'], errors='ignore')
  df['date'] = to_datetime(df['date'])
  return df


def extract(
  csv_folder: str, csv_table_mapping: Dict[str, str], public_holidays_url: str
) -> Dict[str, DataFrame]:
  """Extract the data from the csv files and load them into the dataframes.
  Args:
    csv_folder (str): The path to the csv's folder.
    csv_table_mapping (Dict[str, str]): The mapping of the csv file names to the
    table names.
    public_holidays_url (str): The url to the public holidays.
  Returns:
    Dict[str, DataFrame]: A dictionary with keys as the table names and values as
    the dataframes.
  """
  dataframes = {
    table_name: read_csv(f"{csv_folder}/{csv_file}")
    for csv_file, table_name in csv_table_mapping.items()
  }

  return {
    **dataframes,
    'public_holidays': get_public_holidays(public_holidays_url, "2017"),
  }

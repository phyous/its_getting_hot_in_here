import glob
import sys
import datetime
from typing import List
import statistics
from dataclasses import dataclass

# Historical climate data for cities world wide
# format: dt,AverageTemperature,AverageTemperatureUncertainty,City,Country,Latitude,Longitude
CLIMATE_DATA_DIR = './data/*.csv'
SEARCH_CITY = "Seattle"

@dataclass
class TemperatureReading:
    ''' Temperature reading for a given day in a specified city '''
    date_str: str
    average_temperature: float
    average_temperature_uncertainty: float
    city: str
    country: str
    lat: str
    lng: str

    def date(self) -> datetime:
        return datetime.datetime.strptime(self.date_str, '%m-%d-%Y')

class ClimateStats:
  def __init__(self, records: List[TemperatureReading]):
    self.records = records
    daily_temperatures = [r.average_temperature for r in self.records]
    self.mean_temperature = statistics.mean(daily_temperatures)
  


def generate_climate_stats(csv_lines: str) -> ClimateStats:
  '''
  Parse a bunch of csv lines and turn them into a SearchRecords object
  '''
  records = []
  for l in csv_lines:
    splits = l.split(',')
    records.append(
      TemperatureReading(
        date_str = splits[0],
        average_temperature = float(0.0 if not splits[1].strip() else splits[1]),
        average_temperature_uncertainty = float(0.0 if not splits[2].strip() else splits[2]),
        city = splits[3],
        country = splits[4],
        lat = splits[5],
        lng = splits[6].strip()))
  return ClimateStats(records)


def search_records(substring: str) -> List[str]:
  '''
  Perform a non case sensitive search through historical climate records 
  for those matching `substring`.
  Useful for avoiding loading all data into memory and causing an OOM 
  error on the repl.
  '''

  files = glob.glob(CLIMATE_DATA_DIR)
  csv_data = []
  num_files = len(files)

  current_file = 1.0
  for f in files:
    file = open(f, 'r')
    lines = file.readlines()
    csv_data += [s for s in [l.lower() for l in lines] if s.find(substring.lower()) != -1]
    sys.stdout.write(" 🌆\tLoading city records for '%s': %.0f%%   \r" % (substring, current_file*100/(num_files)))
    sys.stdout.flush()
    current_file += 1
  return csv_data


csv_data = search_records(SEARCH_CITY)
climate_stats = generate_climate_stats(csv_data)
print(len(climate_stats.records))
print(climate_stats.records[0])
print(climate_stats.records[1])
print(climate_stats.mean_temperature)
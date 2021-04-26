import glob
import sys
import datetime
import requests
from typing import List, Tuple
import statistics
import scipy.stats
import calendar
from dataclasses import dataclass

# Historical climate data for cities world wide from Berkeley Earth (http://berkeleyearth.org/data/)
# format: dt,AverageTemperature,AverageTemperatureUncertainty,City,Country,Latitude,Longitude
# ex: 2002-04-01,23.748,0.156,Americana,Brazil,23.31S,48.06W
CLIMATE_DATA_DIR = './data/*.csv'

########################
#  CONFIGURATION - change this to search for different cities/temperatures
########################
SEARCH_CITY = "Seattle"
SEARCH_COUNTRY = "United States"
SEARCH_MONTH = "Apr"
SEARCH_TEMP = 80

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
        return datetime.datetime.strptime(self.date_str, '%Y-%m-%d')

class ClimateStats:
  def __init__(self, records: List[TemperatureReading]):
    self.records = records 
    dates = [r.date() for r in self.records]
    years =  [d.year for d in dates]
    self.data_min_year = min(years)
    self.data_max_year = max(years)
    self.daily_temperature_readings = [(r.average_temperature, r.date()) for r in self.records]
    monthly_temperatures = {}
    for d in self.daily_temperature_readings:
      month = d[1].month
      cur_values = monthly_temperatures.get(month, [])
      monthly_temperatures[month] = cur_values + [d]
    self.monthly_temperatures = monthly_temperatures
  
  def mean(self, month: int) -> float:
    return statistics.mean([t[0] for t in self.monthly_temperatures[month]])
  
  def stdev(self, month: int) -> float:
    return statistics.stdev([t[0] for t in self.monthly_temperatures[month]])
  
  def max_avg_temp(self, month:int):
    return max(self.monthly_temperatures[month], key= lambda k: k[0])
  
  def probability_of_temperature_less_than(self, month:int, t_celsius=None, t_farenheight=None):
    '''
    Compute the probability of it being hotter than a certain termperature in a year given historical data
    '''
    temp = t_celsius if t_celsius else ((t_farenheight - 32) * 5.0/9.0)
    normal_function = scipy.stats.norm(self.mean(month), self.stdev(month))
    return normal_function.cdf(temp)

def str_to_i_month(month_str: str) -> int:
  return {month.lower(): index for index, month in enumerate(calendar.month_abbr) if month}[month_str.lower()]

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


def search_records(substring1: str, substring2: str) -> List[str]:
  '''
  Perform a non case sensitive search through historical climate records 
  for those matching `substring1`(e.g:city) and `substring2`(e.g: country).
  Useful for avoiding loading all data into memory and causing an OOM 
  error on the repl (climate data is >500MB).
  '''

  files = glob.glob(CLIMATE_DATA_DIR)
  csv_data = []
  num_files = len(files)

  current_file = 1.0
  for f in files:
    file = open(f, 'r')
    lines = file.readlines()
    matching_lines = [z for z in [s for s in [l.lower() for l in lines] if s.find(substring1.lower()) != -1] if z.find(substring2.lower()) != -1]
    csv_data += matching_lines
    completion_pct = (current_file*100/(num_files))
    sys.stdout.write(" 🌆\tLoading temperature records for %s, %s: %.0f%%   \r" % (substring1, substring2, completion_pct))
    sys.stdout.flush()
    current_file += 1
  print("\n")
  return csv_data

def c_to_f(tmp_c):
   return (tmp_c * 9/5) + 32

print('''

 ██▓▄▄▄█████▓  ██████      ▄████ ▓█████▄▄▄█████▓▄▄▄█████▓ ██▓ ███▄    █   ▄████ 
▓██▒▓  ██▒ ▓▒▒██    ▒     ██▒ ▀█▒▓█   ▀▓  ██▒ ▓▒▓  ██▒ ▓▒▓██▒ ██ ▀█   █  ██▒ ▀█▒
▒██▒▒ ▓██░ ▒░░ ▓██▄      ▒██░▄▄▄░▒███  ▒ ▓██░ ▒░▒ ▓██░ ▒░▒██▒▓██  ▀█ ██▒▒██░▄▄▄░
░██░░ ▓██▓ ░   ▒   ██▒   ░▓█  ██▓▒▓█  ▄░ ▓██▓ ░ ░ ▓██▓ ░ ░██░▓██▒  ▐▌██▒░▓█  ██▓
░██░  ▒██▒ ░ ▒██████▒▒   ░▒▓███▀▒░▒████▒ ▒██▒ ░   ▒██▒ ░ ░██░▒██░   ▓██░░▒▓███▀▒
░▓    ▒ ░░   ▒ ▒▓▒ ▒ ░    ░▒   ▒ ░░ ▒░ ░ ▒ ░░     ▒ ░░   ░▓  ░ ▒░   ▒ ▒  ░▒   ▒ 
 ▒ ░    ░    ░ ░▒  ░ ░     ░   ░  ░ ░  ░   ░        ░     ▒ ░░ ░░   ░ ▒░  ░   ░ 
 ▒ ░  ░      ░  ░  ░     ░ ░   ░    ░    ░        ░       ▒ ░   ░   ░ ░ ░ ░   ░ 
 ░                 ░           ░    ░  ░                  ░           ░       ░ 

                                                                                
                                                                                
 ██░ ██  ▒█████  ▄▄▄█████▓    ██▓ ███▄    █     ██░ ██ ▓█████  ██▀███  ▓█████   
▓██░ ██▒▒██▒  ██▒▓  ██▒ ▓▒   ▓██▒ ██ ▀█   █    ▓██░ ██▒▓█   ▀ ▓██ ▒ ██▒▓█   ▀   
▒██▀▀██░▒██░  ██▒▒ ▓██░ ▒░   ▒██▒▓██  ▀█ ██▒   ▒██▀▀██░▒███   ▓██ ░▄█ ▒▒███     
░▓█ ░██ ▒██   ██░░ ▓██▓ ░    ░██░▓██▒  ▐▌██▒   ░▓█ ░██ ▒▓█  ▄ ▒██▀▀█▄  ▒▓█  ▄   
░▓█▒░██▓░ ████▓▒░  ▒██▒ ░    ░██░▒██░   ▓██░   ░▓█▒░██▓░▒████▒░██▓ ▒██▒░▒████▒  
 ▒ ░░▒░▒░ ▒░▒░▒░   ▒ ░░      ░▓  ░ ▒░   ▒ ▒     ▒ ░░▒░▒░░ ▒░ ░░ ▒▓ ░▒▓░░░ ▒░ ░  
 ▒ ░▒░ ░  ░ ▒ ▒░     ░        ▒ ░░ ░░   ░ ▒░    ▒ ░▒░ ░ ░ ░  ░  ░▒ ░ ▒░ ░ ░  ░  
 ░  ░░ ░░ ░ ░ ▒    ░          ▒ ░   ░   ░ ░     ░  ░░ ░   ░     ░░   ░    ░     
 ░  ░  ░    ░ ░               ░           ░     ░  ░  ░   ░  ░   ░        ░  ░  

''')
print("Pick a city:\t%s" % SEARCH_CITY)
print("Pick a country:\t%s" % SEARCH_COUNTRY)
print("Pick a month:\t%s" % SEARCH_MONTH)
print("Pick a temperature (in *F): %s" % SEARCH_TEMP)
print("----------------\n")


csv_data = search_records(SEARCH_CITY, SEARCH_COUNTRY)
climate_stats = generate_climate_stats(csv_data)
month_int = str_to_i_month(SEARCH_MONTH)
mean_tmp = c_to_f(climate_stats.mean(month_int))
amount_more = SEARCH_TEMP - mean_tmp
amount_string = "higher" if amount_more >= 0 else "lower"
prob_more_than = (1-climate_stats.probability_of_temperature_less_than(month=month_int, t_farenheight=SEARCH_TEMP)) * 100 
max_av_temp = climate_stats.max_avg_temp(month_int)

print("\tLoaded %d records for %s" % (len(climate_stats.records), SEARCH_CITY))
print("\tData found for years %s to %s\n" % (climate_stats.data_min_year, climate_stats.data_max_year))
print("Over that time period, the mean monthly temperature in %s was %.1f*F" % (SEARCH_CITY, mean_tmp))
print("Your chosen temperature of %s*F is %.1f*F %s the historical average" % (SEARCH_TEMP, amount_more, amount_string))
print("The maximum average monthly temperature ever recorded was %.1f*F on %s" % (c_to_f(max_av_temp[0]), max_av_temp[1]))
print("")
print("The probability of the temperature beign any hotter than %s*F in this month is only %.2f%% (1 in %d)" %
  (SEARCH_TEMP, prob_more_than, int(1/(prob_more_than/100))))


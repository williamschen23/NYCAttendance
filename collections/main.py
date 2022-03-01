# selenium imports
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# misc imports
import time
from pymongo import MongoClient
from mongodb import request_data, generate_discord_data, generate_discord_population_data
from bs4 import BeautifulSoup
from json import dump, load

# .env configuration
from dotenv import load_dotenv
from os import getenv
load_dotenv()

start_time = time.time()
link = getenv('MONGO_LINK')

# apparently I need this to use ONE GOD DAMN DROPDOWN???
# selects the max option for attendance website and gets the data
ser = Service("/Applications/chromedriver")
driver = webdriver.Chrome(service=ser)
driver.get("https://www.nycenet.edu/PublicApps/Attendance.aspx")
element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_gvAttendance_ctl23_ddlPageSize")
drp = Select(element)
drp.select_by_index(3)

# parsing through the data using Beautiful Soup
soup = BeautifulSoup(driver.page_source, 'html.parser')
data = soup.find_all("td")
data_list = [i.text for i in data]
driver.quit()

# this should be 1601
print(int(len(data_list)/4))
request_data(data_list)

# generate discord data for MongoDB with and without population
generate_discord_data(data_list[2])
generate_discord_population_data(data_list[2])
print(time.time() - start_time, " run time")

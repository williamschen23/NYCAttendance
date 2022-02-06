# selenium imports
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# misc imports
from pymongo import MongoClient
from mongodb import generate_data
from bs4 import BeautifulSoup
from json import dump, load

# .env configuration
from dotenv import load_dotenv
from os import getenv
load_dotenv()

link = getenv('mongo_link')
client = MongoClient(link)
db = client.schools

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
data_list = soup.find_all("td")
driver.quit()

# init a nested data list and append data for each school for each []
sortedData = [[] for _ in range(int(len(data_list)/4))]
iterator = 0
for j in range(len(data_list)):
    sortedData[iterator].append(data_list[j].text)
    if (j+1) % 4 == 0:
        iterator += 1

# this should be 1601
print(len(sortedData))

# adds the sortedData to a json for safe-keeping
with open('data.json', 'r') as f:
    data_json = load(f)
if sortedData[0][2] not in data_json:
    data_json[sortedData[0][2]] = sortedData
    with open('data.json', 'w') as f:
        dump(data_json, f)

# generates data for mongoDB
generate_data(sortedData)

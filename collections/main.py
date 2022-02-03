from datetime import datetime
import pymongo
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# .env configuration
from dotenv import load_dotenv
from os import getenv
load_dotenv()

link = getenv('mongo_link')
client = pymongo.MongoClient(link)
db = client.schools

# apparently I need this to use ONE GOD DAMN DROPDOWN???
PATH = "/Applications/chromedriver"
driver = webdriver.Chrome(PATH)
driver.get("https://www.nycenet.edu/PublicApps/Attendance.aspx")
element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_gvAttendance_ctl23_ddlPageSize")
drp = Select(element)
drp.select_by_index(3)

# data
soup = BeautifulSoup(driver.page_source, 'html.parser')
rows = soup.find_all("td")
now = datetime.today()
date = now.strftime("%m/%d/%Y")

# init a data list and append all valid data for every row in it
data = [[] for _ in range(int(len(rows)/4))]
iterator = 0
for j in range(len(rows)):
    data[iterator].append(rows[j].text)
    j += 1
    if j % 4 == 0:
        iterator += 1

# TODO make it go into mongoDB

print(data)
driver.quit()


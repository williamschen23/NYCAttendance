import pymongo
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

link = ""
client = pymongo.MongoClient()
db = client.schools

# apparently I need this to use ONE GOD DAMN DROPDOWN???
PATH = "/Applications/chromedriver"
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options, executable_path=PATH)
driver.get("https://www.nycenet.edu/PublicApps/Attendance.aspx")
element = driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_gvAttendance_ctl23_ddlPageSize")
drp = Select(element)
drp.select_by_index(3)

#bs4 right now it gets all of the table data and prints it 
#TODO make it go into mongoDB
tb1 = []
soup = BeautifulSoup(driver.page_source, 'html.parser')
rows = soup.table.find_all("tr")
for row in rows:
    cells = row.find_all("td")
    for i in cells:
        print(i.text)

driver.quit()

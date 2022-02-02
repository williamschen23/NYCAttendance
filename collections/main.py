from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep

link = ""
client = MongoClient(link)
db = client.schools

# apparently I need this to use ONE GOD DAMN DROPDOWN???
PATH = "/Applications/chromedriver"
driver = webdriver.Chrome(PATH)
driver.get("https://www.nycenet.edu/PublicApps/Attendance.aspx")
element = driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_gvAttendance_ctl23_ddlPageSize")
drp = Select(element)
drp.select_by_index(0)

#bs4 right now it gets all of the table data and prints it 
#TODO make it go into mongoDB
dict1 = {}
soup = BeautifulSoup(driver.page_source, 'html.parser')
rows = soup.find_all("td")
now = datetime.today()
date = now.strftime("%m/%d/%Y")


result = [[] for _ in range(30)] 
print(result)
i = 0
j = 0
for row in rows:
    if i == 0:
        print(row.text)
    result[i].append(row.text)
    j+= 1
    if j % 4 == 0:
        i += 1

print(result[1]==result[0])

for row in rows:
    cells = row.find_all("td")
    j = 0
    for cell in cells:
        if j == 0:
            dict1['school_id'] = cell.text
        elif j == 1:
            dict1['school_name'] = cell.text
            dict1[str(date)] = {}
        elif j == 3:
            dict1[str(date)]['percentage'] = cell.text
        j+=1


driver.quit()

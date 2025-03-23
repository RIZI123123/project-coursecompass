from bs4 import BeautifulSoup
import requests
import random
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

driver = webdriver.Firefox()

# list of user agents
userAgents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.3342.1039 Safari/537.36",
    # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.5528.1301 Safari/537.36",
    # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.6327.1738 Safari/537.36",
    # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.1553.1540 Safari/537.36",
    # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.4613.1196 Safari/537.36",
]

headers = {
  "Host": "w2prod.sis.yorku.ca",
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.5",
  "Accept-Encoding": "gzip, deflate, br, zstd",
  "Referer": "https://www.google.com/",
  "DNT": "1",
  "Connection": "keep-alive",
  "Upgrade-Insecure-Requests": "1",
  "Sec-Fetch-Dest": "document",
  "Sec-Fetch-Mode": "navigate",
  "Sec-Fetch-Site": "cross-site",
  "Sec-Fetch-User": "?1",
  "Priority": "u=0, i",
  "TE": "trailers"
}

base_url = "https://w2prod.sis.yorku.ca"

## Open the Home Page
driver.get("https://w2prod.sis.yorku.ca/Apps/WebObjects/cdm")
time.sleep(random.randint(3, 6))
check_input = driver.find_element(By.LINK_TEXT, "Course Campus")
check_input.click()

time.sleep(random.randint(2, 3))
campus_select = driver.find_element(By.NAME, "selectCampusBox")
select = Select(campus_select)
select.select_by_visible_text("Keele")
select.deselect_by_visible_text("Catholic Education Centre")

time.sleep(1)
check_input = driver.find_element(By.NAME, "3.10.7.5")
check_input.click()
courselist_page = driver.page_source

CourselistPageSoup = BeautifulSoup(courselist_page, "lxml")
tables_tags = CourselistPageSoup.find_all("table")
print(len(tables_tags[4].find_all('tr')))
tables_rows = tables_tags[4].find_all('tr')

def getPre(desc : str):
  preReq = ""
  begin = desc.find("Prerequisite")
  exclude = ["Course Credit Exclusion", "Corequisite"]
  text = desc[begin:]
  for word in exclude:
     end = desc.find(word)
     if (end <= len(desc)):
        text = desc[begin:end]
        break
     
  if (text == "."):
     return ""
  
  courses = re.findall(r"[A-Z][A-Z][A-Z]?[A-Z]? [0-9]{4}", text)
  #print(courses)
  for preQ in courses:
     preReq = preReq + "," + preQ
  preReq = preReq[1:]
  return preReq

list_of_courses = []

for rows in tables_rows[6:9]:#goes through each course in list according to specifies range.
    time.sleep(random.randint(4, 13))
    columns = rows.find('a')
    print(columns['href'])
    driver.get("https://w2prod.sis.yorku.ca" + columns['href'])
    courseInfo_page = driver.page_source
    courseInfoSoup = BeautifulSoup(courseInfo_page, "lxml")

    tables = courseInfoSoup.find_all('table')
    Title = tables[4].find('h1')
    title_str = str(Title.text)
    #print(Title.text)

    paragraphs = tables[4].find_all('p')
    Description = paragraphs[4]
    desc_str = str(Description.text)
    #print(Description.text)

    professors = []
    sections = courseInfoSoup.find_all('td', colspan=3)

    for sect in sections[1::2]:
       profs = sect.find_all('a')
       for x in range(1, len(profs)):
          if (x % 2 == 1):
             professors.append(str(profs[x].text).replace("\xa0", " "))
             #print(profs[x].text)

    course = {}
    course['subject'] = title_str[3:7]
    print(course["subject"])
    course['code'] = title_str[3:12]
    print(course['code'])
    course['number'] = title_str[8:12]
    print(course["number"])
    course['credits'] = title_str[15:19]
    print(course['credits'])
    course['name'] = title_str[22:].strip()
    print(course['name'])
    course['description'] = desc_str
    print(course['description'])
    course['prerequisites'] = getPre(desc_str)
    print(course['prerequisites'])
    course['professors'] = list(set(professors))
    print(course['professors'])
    list_of_courses.append(course)

    time.sleep(random.randint(7, 12))
    driver.back()

with open('data.json', 'w') as f:     
    f.write(json.dumps(list_of_courses, indent= 1))
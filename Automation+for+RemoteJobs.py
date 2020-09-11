from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
import requests
import json
import pandas

# Stating the path of "chromedriver"
PATH = 'C:\Program Files (x86)\chromedriver.exe'
# Opening the browser
driver = webdriver.Chrome(PATH)
# Integrating actionchains for the opened browser
actions = ActionChains(driver)
# Navigating to site.
driver.get("https://remoteok.io/")
# Scrolling down for site to load. (6 times was enough for client's needs but 10 is chosen to make sure.)
for _ in range(10):
    actions.send_keys(Keys.SPACE).perform()
    time.sleep(1)
arr = []
# Getting the selector for the jobs
elements = driver.find_elements_by_css_selector("tr.job")

# The function to scrape "Salary" and "Job Description".


def get_salary_and_description_for_job_id(job_id):
    html = requests.get('https://remoteok.io/remote-jobs/'+job_id)
    soup = bs(html.content)
    dct = {}
    for s in soup.find_all('script'):
        if len(s.contents) > 0:
            if 'datePosted' in s.contents[0]:
                dict_obj = json.loads(s.contents[0])
    try:
        salary = dict_obj['baseSalary']['value'] + \
            " " + dict_obj['baseSalary']['currency']
    except:
        salary = None

    try:
        desc = dict_obj['description']
    except:
        desc = None
    dct['salary'] = salary
    dct['description'] = desc
    return dct


# This will work for each job.
for value in elements:
    dct = {}
    # The selector that contains the data for the "Time of Job"
    timeofjob = value.find_element_by_css_selector(
        "td.time").find_element_by_css_selector("a").text
    # This string was not wanted in the output so I cut it out here.
    if "📎" in timeofjob:
        continue
    # If "mo" is in "Time of Job" the client didn't want it so I stop the script here.
    if "mo" in timeofjob:
        break
    # The selector that contains the data for the "Job ID"
    job_id = value.get_attribute("data-id")
    # Calling the function to get "Description" and "Salary"
    desc_salary = get_salary_and_description_for_job_id(job_id)
    # The selector that contains the data for the "Company Name"
    companyName = value.find_element_by_css_selector(
        "td.company").find_element_by_css_selector("a.companyLink").text
    # The selector that contains the data for the "Job Title"
    jobTitle = value.find_element_by_css_selector(
        "td.company").find_element_by_css_selector("h2").text
    # The selector that contains the data for the "Job Tags"
    tags = [t.text for t in value.find_element_by_css_selector(
        "td.tags").find_elements_by_css_selector("a")]
    # The selector that contains the data for the "Link of job"
    applybutton = value.find_element_by_css_selector(
        "td.source").find_element_by_css_selector("a.no-border").get_attribute("href")
    try:
        # The selector that contains the data for the "Job image link"
        image = value.find_element_by_css_selector("td.image").find_element_by_css_selector(
            "a.preventLink").find_element_by_css_selector("img.logo").get_attribute("src")
    except:
        image = None
    # Putting all the data into a dictionary.
    dct["description"] = desc_salary["description"]
    dct["salary"] = desc_salary["salary"]
    dct["company_name"] = companyName
    dct["job_title"] = jobTitle
    dct["tags"] = tags
    dct["applybutton"] = applybutton
    dct["image"] = image

    # Appending the dictionary to an empty array.
    arr.append(dct)

# Writing the array into a csv.
df = pandas.DataFrame(data=arr)
df.to_csv("outputson.csv")

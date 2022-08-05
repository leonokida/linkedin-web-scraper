import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import time
import sys

options = Options()
options.headless = True
service = Service("./firefox-version/geckodriver")
driver = webdriver.Firefox(service=service, options=options)


driver.get('https://www.linkedin.com/login/')

# Gets email and password from .env file
load_dotenv()
EMAIL = os.getenv('LKDN_USERNAME')
PASSWD = os.getenv('LKDN_PASSWORD')

# Logs in
emailForm = driver.find_element(By.ID, 'username')
emailForm.send_keys(EMAIL)
passwdForm = driver.find_element(By.ID, 'password')
passwdForm.send_keys(PASSWD)
loginButton = driver.find_element(By.XPATH, '/html/body/div/main/div[2]/div[1]/form/div[3]/button')
loginButton.click()

# Gets URL from command line
url = sys.argv[1]
driver.get(url)

# Function to scroll the page, which loads all the info in it
start = time.time()

def scrollPage(driver):
    # will be used in the while loop
    initialScroll = 0
    finalScroll = 1000
    
    while True:
        driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        # this command scrolls the window starting from
        # the pixel value stored in the initialScroll 
        # variable to the pixel value stored at the
        # finalScroll variable
        initialScroll = finalScroll
        finalScroll += 1000
    
        # we will stop the script for 3 seconds so that 
        # the data can load
        time.sleep(1.5)
        # You can change it as per your needs and internet speed
    
        end = time.time()
    
        # We will scroll for 20 seconds.
        # You can change it as per your needs and internet speed
        if round(end - start) > 5:
            break

# Calls function to scroll the page
scrollPage(driver)

# Gets source code of the page, loads it with BeautifulSoup
src = driver.page_source
soup = BeautifulSoup(src, 'html.parser')

# Gets profile name
try:
    name = soup.find('h1', class_="text-heading-xlarge inline t-24 v-align-middle break-words").get_text()
except:
    name = ""

# Gets profile activity
try:
    activity = soup.find('div', class_="text-body-medium break-words").get_text().strip()
except:
    activity = ""

# Gets profile location
try:
    locationDiv = soup.find('div', class_="pv-text-details__left-panel pb2")
    location = locationDiv.find('span', class_="text-body-small inline t-black--light break-words").get_text().strip()
except:
    location = ""
city, state, country = location.split(', ')


# Gets all expandable sections
expandButtons = soup.find_all('a', class_="optional-action-target-wrapper artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--muted inline-flex justify-center full-width align-items-center artdeco-button--fluid")

expandableSections = []

# Gets all expandable sections names
for expandButton in expandButtons:
    sectionDiv = expandButton.find_previous('h2')
    sectionName = sectionDiv.find('span')
    expandableSections.append(sectionName.get_text())

# Gets all ul sections
ulSections = soup.find_all('ul', class_="pvs-list ph5 display-flex flex-row flex-wrap")

ulTags = []

# Gets all ul sections names
for ulTag in ulSections:
    ulDiv = ulTag.find_previous('h2')
    ulName = ulDiv.find('span')
    ulTags.append(ulName.get_text())

try:
    aboutMeDiv = soup.find('div', class_="display-flex ph5 pv3")
    aboutMe = aboutMeDiv.find('span').get_text().strip()
except:
    aboutMe = ""

# Gets all info from experience section
def findExperience(x):
    try:
        experience = []
        # Finds all companies
        experienceDivs = x.find_all('div', class_="pvs-entity pvs-entity--padded pvs-list__item--no-padding-when-nested")
        for exp in experienceDivs:
            # Tries to find list inside company subsection
            # If found, it means there's more than one job title inside the same company
            outerContainer = exp.find('ul')

            # Gets long job description, with expandable section
            items = exp.find_all('div', class_="display-flex flex-column full-width align-self-center")
            if len(items) == 1:
                job = exp.find('span', "mr1 t-bold").find('span').get_text().strip()
                try:
                    company = exp.find('span', class_="t-14 t-normal").find('span').get_text().strip()
                except:
                    company = ""
                try:
                    jobDescription = exp.find('li', class_="pvs-list__item--with-top-padding").find("span").get_text().strip()
                except:
                    jobDescription = ""
                date = location = ""
                newExperience = {
                    "title": job,
                    "local": company,
                    "date": date,
                    "location": location,
                    "description": jobDescription
                }
                experience.append(newExperience)

            else:
                # When there's a list of job positions in the same company
                if outerContainer:
                    companySpan = outerContainer.find_previous('span', class_="mr1 hoverable-link-text t-bold")
                    try:
                        company = companySpan.find('span').get_text().strip()
                    except:
                        company = ""
                    outerContainerLi = outerContainer.find_all('div', class_="pvs-entity")
                    for li in outerContainerLi:
                        try:
                            job = li.find('span').find('span').get_text().strip()
                        except:
                            job = ""
                        try:
                            jobDescription = li.find("div", class_= "inline-show-more-text inline-show-more-text--is-collapsed").find("span").get_text().strip()
                        except:
                            jobDescription =""
                        
                        date = location = ""
                        newExperience = {
                            "title": job,
                            "local": company,
                            "date": date,
                            "location": location,
                            "description": jobDescription
                        }
                        experience.append(newExperience)

                # When there's only one job position in the company         
                else:
                    try:
                        job = exp.find('div', class_="display-flex align-items-center").find('span', "mr1 t-bold").find('span').get_text().strip()
                    except:
                        job = ""
                    try:    
                        company = exp.find('span', class_="t-14 t-normal").find('span').get_text().strip()
                    except:
                        company = ""
                    try:
                        jobDescription = exp.find("div", class_="inline-show-more-text inline-show-more-text--is-collapsed").find("span").get_text().strip()
                    except:
                        jobDescription =""
                    date = location = ""
                    newExperience = {
                        "title": job,
                        "local": company,
                        "date": date,
                        "location": location,
                        "description": jobDescription
                    }
                    experience.append(newExperience)
            
    except:
        experience = []

    # Returns list of all experience data
    return experience

# Gets experience data by calling the function above    
if ('Experience' in expandableSections):
    driver.get(url + "details/experience/")

    time.sleep(3)

    scrollPage(driver)

    experiencePage = driver.page_source
    soup = BeautifulSoup(experiencePage, 'html.parser')

    experienceDiv = soup.find('ul', class_="pvs-list")
    experience = findExperience(experienceDiv)
else:
    try:
        experienceUl = ulTags.index('Experience')
        experience = findExperience(ulSections[experienceUl])
    except:
        experience = []

# Function to get all academic data
def findAcademic(x):
    try:
        academic = []
        # Finds all divs
        academicDivs = x.find_all('div', class_="pvs-entity pvs-entity--padded pvs-list__item--no-padding-when-nested")
        # Gets data from each div
        for i in academicDivs:
            academicName = i.find('span', class_="mr1 hoverable-link-text t-bold")
            academicCourse = i.find('span', class_="t-14 t-normal")
            if (academicCourse):
                academicCourse = academicCourse.find('span').get_text()
            else:
                academicCourse = ""
            academicPeriod = i.find('span', class_="t-14 t-normal t-black--light")

            if (academicPeriod):
                period = academicPeriod.find('span').get_text()
                if (' - ' in period):
                    startYear, endYear = period.split(' - ')
                else:
                    startYear = endYear = period

                startDate = {
                    "year": startYear
                }

                endDate = {
                    "year": endYear
                }
            else:
                startDate = {
                    "year": ""
                }

                endDate = {
                    "year": ""
                }

            newAcademic = {
                "institution": academicName.find('span').get_text(),
                "course": academicCourse,
                "start_date": startDate,
                "end_date": endDate
            }
            academic.append(newAcademic)

    except:
        academic = []

    # Returns list of academic data
    return academic

# Calls the function above to get all the academic data
if ('Education' in expandableSections):
    driver.get(url + "details/education/")

    time.sleep(3)

    scrollPage(driver)

    educationPage = driver.page_source
    soup = BeautifulSoup(educationPage, 'html.parser')

    skillsDiv = soup.find('ul', class_="pvs-list")
    academic = findAcademic(skillsDiv)
else:
    try:
        academicUl = ulTags.index('Education')
        academic = findAcademic(ulSections[academicUl])
    except:
        academic = []

# Function to get all skills data
def findSkills(x):
    try:
        # Gets all skills
        skillsSpan = x.find_all('span', class_="mr1 t-bold")
        skills = []
        for i in skillsSpan:
            newSkill = {
                "name": i.find('span').get_text()
            }
            skills.append(newSkill)
    except:
        skills = []
    # Returns list of skills
    return skills

# Calls the function above to get skills data
if ('Skills' in expandableSections):
    driver.get(url + "details/skills/")

    time.sleep(3)

    scrollPage(driver)

    skillsPage = driver.page_source
    soup = BeautifulSoup(skillsPage, 'html.parser')

    skillsDiv = soup.find('ul', class_="pvs-list")
    skills = findSkills(skillsDiv)
else:
    try:
        skillsUl = ulTags.index('Skills')
        skills = findSkills(ulSections[skillsUl])
    except:
        skills = []

# Calls findSkills to get languages data, because they count as skills
if ('Languages' in expandableSections):
    driver.get(url + "details/languages/")

    time.sleep(3)

    scrollPage(driver)

    langPage = driver.page_source
    soup = BeautifulSoup(langPage, 'html.parser')

    langsDiv = soup.find('ul', class_="pvs-list")
    langs = findSkills(langsDiv)
else:
    try:
        # Concatenates languages list to skills list
        langsUl = ulTags.index('Languages')
        langs = findSkills(ulSections[langsUl])
        skills += langs
    except:
        pass

# Puts all lists inside object
newJson = {
        "status_sge": "",
        "name": name,
        "last_query": "",
        "activity_linkedin": activity,
        "Looking_job": "",
        "city": city,
        "state": state,
        "country": country,
        "contact_info": "",
        "about_me": aboutMe,
        "experience": experience,
        "academic": academic,
        "skills": skills,
        "voluteer_work": ""
}

# Generates JSON from object
json_obj = json.dumps(newJson, ensure_ascii=False)
with open("linkedInData.json", "w") as outfile:
    outfile.write(json_obj)

# Ends driver
driver.quit()
import os
import re
import json
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.objects import Experience, Education, Scraper, Interest, Volunteering, Accomplishment, Contact
from selenium.webdriver.support.ui import Select

from scraper import selectors


class Person(Scraper):

    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
        self,
        linkedin_url=None,
        name=None,
        about=None,
        experiences=None,
        educations=None,
        interests=None,
        accomplishments=None,
        volunteering = None,
        company=None,
        job_title=None,
        contacts=None,
        driver=None,
        get=True,
        scrape=True,
        close_on_complete=False,
        time_to_wait_after_login=0,
        companies=None,
        company_urls=None
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.volunteering = volunteering or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []
        self.companies= companies or []
        self.company_urls=company_urls or []
        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape(close_on_complete)
    
    def get_company_companies(self):

        for url in self.company_urls:
            try:
                self.driver.get(url)
                self.focus()
                main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
                string_employees=self.driver.find_element_by_partial_link_text("employees").text
                string_employees=re.sub(r'[^0-9]', '', string_employees).replace(",","")
                val_employees=int(string_employees) # get numveric value from sting in the form "xxxx employees"
                name=self.driver.find_element_by_tag_name("h1").text
                self.companies.append((name,val_employees))
            except:
                pass
        return self.companies

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_volunteering(self, volunteering):
        self.volunteering.append(volunteering)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape(self, close_on_complete=False):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element_by_class_name(class_name)
            div.find_element_by_tag_name("button").click()
        except Exception as e:
            pass

    def is_open_to_work(self):
        try:
            return "#OPEN_TO_WORK" in self.driver.find_element_by_class_name("pv-top-card-profile-picture").find_element_by_tag_name("img").get_attribute("title")
        except:
            return False

    def get_experiences(self):
        work_times = ''
        url = os.path.join(self.linkedin_url, "details/experience")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list", base=main)
        for position in main_list.find_elements_by_xpath("li"):
            position = position.find_element_by_class_name("pvs-entity")
            company_logo_elem, position_details = position.find_elements_by_xpath("*")
            
            # company elem
            company_linkedin_url = company_logo_elem.find_element_by_xpath("*").get_attribute("href")

            # position details
            position_details_list = position_details.find_elements_by_xpath("*")
            position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
            position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
            outer_positions = position_summary_details.find_element_by_xpath("*").find_elements_by_xpath("*")
            try:
                if len(outer_positions) == 4:
                    try:
                        position_title = outer_positions[0].find_element_by_tag_name("span").find_element_by_tag_name("span").text
                    except:
                        position_title = ""
                    try:
                        company = outer_positions[1].find_element_by_tag_name("span").text
                    except:
                        company = ""
                    try:
                        work_times = outer_positions[2].find_element_by_tag_name("span").text
                    except:
                        work_times = ""
                    try:
                        location = outer_positions[3].find_element_by_tag_name("span").text
                    except:
                        location = ""

                elif len(outer_positions) == 3:
                    if "·" in outer_positions[2].text:
                        try:
                            position_title = outer_positions[0].find_element_by_tag_name("span").find_element_by_tag_name("span").text
                        except:
                            position_title = ""
                        try:
                            company = outer_positions[1].find_element_by_tag_name("span").text
                        except:
                            company = ""
                        try:
                            work_times = outer_positions[2].find_element_by_tag_name("span").text
                        except:
                            work_times= ""
                        location = ""
                    else:
                        position_title = ""
                        try:
                            company = outer_positions[0].find_element_by_tag_name("span").find_element_by_tag_name("span").text
                        except:
                            company = ""
                        work_times = outer_positions[1].find_element_by_tag_name("span").text
                        location = outer_positions[2].find_element_by_tag_name("span").text
            except:
                work_times =''

            times = work_times.split("·")[0].strip() if work_times else ""
            duration = work_times.split("·")[1].strip() if len(work_times.split("·")) > 1 else None

            from_date = " ".join(times.split(" ")[:2]) if times else ""
            to_date = " ".join(times.split(" ")[3:]) if times else ""
            try:
                z = len(position_summary_text.find_element_by_class_name("pvs-list").find_element_by_class_name("pvs-list").find_elements_by_xpath("li"))
            except:
                z = 0
            if position_summary_text and z > 1:
                descriptions = position_summary_text.find_element_by_class_name("pvs-list").find_element_by_class_name("pvs-list").find_elements_by_xpath("li")
                for description in descriptions:
                    try:
                        res = description.find_element_by_tag_name("a").find_elements_by_xpath("*")
                        position_title_elem = res[0] if len(res) > 0 else None
                        work_times_elem = res[1] if len(res) > 1 else None
                        location_elem = res[2] if len(res) > 2 else None


                        location = location_elem.find_element_by_xpath("*").text if location_elem else None
                        position_title = position_title_elem.find_element_by_xpath("*").find_element_by_tag_name("*").text if position_title_elem else ""
                        work_times = work_times_elem.find_element_by_xpath("*").text if work_times_elem else ""
                        times = work_times.split("·")[0].strip() if work_times else ""
                        duration = work_times.split("·")[1].strip() if len(work_times.split("·")) > 1 else None
                        from_date = " ".join(times.split(" ")[:2]) if times else ""
                        to_date = " ".join(times.split(" ")[3:]) if times else ""

                        experience = (
                        position_title, 
                        from_date,
                        to_date,
                        duration,
                        location,
                        description,
                        company,
                        company_linkedin_url
                    )
                        self.add_experience(experience)
                    except:
                        continue
            else:
                try:
                    description = position_summary_text.text if position_summary_text else ""

                    experience = (
                        position_title, 
                        from_date,
                        to_date,
                        duration,
                        location,
                        description,
                        company,
                        company_linkedin_url
                    )
                    self.company_urls.append(str(company_linkedin_url))
                    self.add_experience(experience)                
                except:
                    pass


    def get_educations(self):
        url = os.path.join(self.linkedin_url, "details/education")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list", base=main)
        for position in main_list.find_elements_by_class_name("pvs-entity"):
            institution_logo_elem, position_details = position.find_elements_by_xpath("*")

            # company elem
            institution_linkedin_url = institution_logo_elem.find_element_by_xpath("*").get_attribute("href")

            # position details
            position_details_list = position_details.find_elements_by_xpath("*")
            try:    
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
            except:
                position_summary_details = ''
            try:
                position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
            except:
                position_summary_text = ''
            try:
                outer_positions = position_summary_details.find_element_by_xpath("*").find_elements_by_xpath("*")
            except:
                outer_positions = ''
            try:
                institution_name = outer_positions[0].find_element_by_tag_name("span").find_element_by_tag_name("span").text
            except:
                institution_name = ""
            try:
                degree = outer_positions[1].find_element_by_tag_name("span").text
            except:
                degree = ""
            try:
                times = outer_positions[2].find_element_by_tag_name("span").text
            except:
                times = ''
            try:
                duration = times.split("·")[1].strip() if len(times.split("·")) > 1 else None
            except:
                duration =''

            from_date = " ".join(times.split(" ")[:2])
            to_date = " ".join(times.split(" ")[3:])



            description = position_summary_text.text if position_summary_text else ""

            education = (duration,description,degree,institution_name,institution_linkedin_url)
            
            self.add_education(education)

    def get_name_and_location(self):
        top_panels = self.driver.find_elements_by_class_name("pv-text-details__left-panel")
        self.name = top_panels[0].find_elements_by_xpath("*")[0].text
        self.location = top_panels[1].find_element_by_tag_name("span").text
    def get_connections(self):
        try: # There was an error here with the index out of range (i.e. the scraper cannot find this element in the HTML)
            connections = self.driver.find_elements_by_partial_link_text("connections")[0].text
        except:
            pass
        flag=False
        try:
            
            connections = (re.sub(r'[^0-9]', '', connections).replace(",","")).replace("+","")
            
            self.contacts=int(connections)
        except: 
            flag=True
        if flag:
            try:
                connections_text = self.driver.find_element_by_css_selector("#profile-content > div > div.scaffold-layout.scaffold-layout--breakpoint-md.scaffold-layout--main-aside.scaffold-layout--reflow.pv-profile > div > div > main").text
                
                connections=connections_text.split("connections")[0].split("\n")[-1]
                
                connections = (re.sub(r'[^0-9]', '', connections).replace(",","")).replace("+","")
                
                self.contacts=int(connections)
            except:
                pass

    def get_about(self):
        try:
            about = self.driver.find_element_by_id("about").find_element_by_xpath("..").find_element_by_class_name("display-flex").text
            self.about = about
        except:
            self.about= None


    def scrape_logged_in(self, close_on_complete=False):
        driver = self.driver
        duration = None

        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    self.__TOP_CARD,
                )
            )
        )
        self.focus()
        self.wait(5)

        # get name and location
        self.get_name_and_location()

        self.get_connections()

        self.open_to_work = self.is_open_to_work()

        # get about
        self.get_about()
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

        # get experience
        self.get_experiences()

        ##self.get_company_companies()
        # get education
        self.get_educations()

        # self.get_volunteering()

        driver.get(self.linkedin_url)

        # get interest
        try:

            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            interestContainer = driver.find_element(By.XPATH,
                "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']"
            )
            for interestElement in interestContainer.find_elements_by_xpath(
                "//*[@class='pv-interest-entity pv-profile-section__card-item ember-view']"
            ):
                interest = Interest(
                    interestElement.find_element_by_tag_name("h3").text.strip()
                )
                self.add_interest(interest)
        except:
            pass

        #get volunteering



        # try:
        #     url = os.path.join(self.linkedin_url, "volunteering-experiences/")
        #     self.driver.get(url)
        #     self.focus()
        #     main = self.wait_for_element_to_load(by=By.ID, name="main")
        #     self.scroll_to_half()
        #     self.scroll_to_bottom()
        #     main_list = self.wait_for_element_to_load(name="pvs-list", base=main)
        #     for position in main_list.find_elements_by_class_name("pvs-entity"):
        #         institution_logo_elem, position_details = position.find_elements_by_xpath("*")
        #          # company elem
        #         institution_linkedin_url = institution_logo_elem.find_element_by_xpath("*").get_attribute("href")

        #         # position details
        #         position_details_list = position_details.find_elements_by_xpath("*")
        #         position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
        #         position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
        #         outer_positions = position_summary_details.find_element_by_xpath("*").find_elements_by_xpath("*")

        #         event_name = outer_positions[0].find_element_by_tag_name("span").find_element_by_tag_name("span").text
        #         company_name = outer_positions[1].find_element_by_tag_name("span").text
        #         try:
        #             times = outer_positions[2].find_element_by_tag_name("span").text
        #         except:
        #             times = 'None'

        #         from_date = " ".join(times.split(" ")[:2])
        #         to_date = " ".join(times.split(" ")[3:])

        #         description = position_summary_text.text if position_summary_text else ""

        #         education = Volunteering(
        #         from_date=from_date,
        #         to_date=to_date,
        #         description=description,
        #         company_name=company_name,
        #         event_name=event_name,
        #         linkedin_url=institution_linkedin_url
        #     )
        #     self.add_education(education)
        
        
        # except:
        #     pass

        # get accomplishment
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            acc = driver.find_element(By.XPATH,
                "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']"
            )
            for block in acc.find_elements_by_xpath(
                "//div[@class='pv-accomplishments-block__content break-words']"
            ):
                category = block.find_element_by_tag_name("h3")
                for title in block.find_element_by_tag_name(
                    "ul"
                ).find_elements_by_tag_name("li"):
                    accomplishment = Accomplishment(category.text, title.text)
                    self.add_accomplishment(accomplishment)
        except:
            pass

        # get connections (??? it gets OUR ACCOUNT CONNNECTIONS)
        # try:
        #     driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
        #     time.sleep(2)
            
        #     connections = driver.find_element_by_xpath('/html/body/div[5]/div[3]/div/div/div/div/div[2]/div/div/main/div/section/header/h1').text
        #     print(connections)
        #     connections = connections.split(" ")[0].replace(",","")
        #     print(connections)
        #     val_connections=int(connections)
        #     self.contacts=connections
        # except Exception as e:
        #     print(e)
        #     connections = 0

        # if close_on_complete:
        
        #     driver.quit()
        

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "{name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
        )
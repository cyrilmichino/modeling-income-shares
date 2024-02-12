from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from objects import Scraper
import constants as c

class Job(Scraper):

    def __init__(
        self,
        linkedin_url=None,
        job_title=None,
        company=None,
        company_linkedin_url=None,
        location=None,
        posted_date=None,
        applicant_count=None,
        job_description=None,
        benefits=None,
        driver=None,
        close_on_complete=True,
        scrape=True,
    ):
        super().__init__()
        self.linkedin_url = linkedin_url
        self.job_title = job_title
        self.driver = driver
        self.company = company
        self.company_linkedin_url = company_linkedin_url
        self.location = location
        self.posted_date = posted_date
        self.applicant_count = applicant_count
        self.job_description = job_description
        self.benefits = benefits

        if scrape:
            self.scrape(close_on_complete)

    def __repr__(self):
        return f"{self.job_title} {self.company}"

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            raise NotImplemented("This part is not implemented yet")


    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        
        driver.get(self.linkedin_url)
        self.focus()
        self.job_title = self.wait_for_element_to_load(name="jobs-unified-top-card__job-title").text.strip()
        self.company = self.wait_for_element_to_load(name="jobs-unified-top-card__company-name").text.strip()
        self.company_linkedin_url = self.wait_for_element_to_load(name="jobs-unified-top-card__company-name").find_element_by_tag_name("a").get_attribute("href")
        self.location = self.wait_for_element_to_load(name="jobs-unified-top-card__bullet").text.strip()
        self.posted_date = self.wait_for_element_to_load(name="jobs-unified-top-card__posted-date").text.strip()
        self.applicant_count = self.wait_for_element_to_load(name="jobs-unified-top-card__applicant-count").text.strip()
        self.job_description = self.wait_for_element_to_load(name="jobs-description").text.strip()
        self.benefits = self.wait_for_element_to_load(name="jobs-unified-description__salary-main-rail-card").text.strip()

        if close_on_complete:
            driver.close()
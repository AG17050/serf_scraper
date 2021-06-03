# -*- coding: utf-8 -*-

from SerfScraper import SerfScraper
from CommonDriver import Select
from file_downloading import SerfFile
from utils import standard_date_str, standard_date, get_download_path
from file_collection import FileTracker
from carrier_matching import CarrierMatcher
import pandas as pd
import os
from pathlib import Path
import time
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

months = ['January','February','March','April','May','June',
          'July','August','September','October','November','December']

class NYSerfScraper(SerfScraper):
    
    def __init__(self):
        url = 'https://myportal.dfs.ny.gov/web/prior-approval/rate-applications-by-company'
        super().__init__(url)
        self.__set_submission_date()
        
        self.row_urls = []
        self.filing_urls = []
        
        self.file_tracker = FileTracker()
        self.file_tracker.wipe_download_records()
        
        self.num_downloads = len(os.listdir(get_download_path()))
        
    def __set_submission_date(self):
        dates_data = pd.read_csv('serf_submission_dates.txt')
        start_date_str = dates_data['Start Date'][0]
        self.start_date = standard_date(start_date_str)
        
    @staticmethod
    def extract_date_from_text(date_str: str):
        date_str = date_str.replace(',','')
        
        month = [m for m in months if m in date_str][0]
        date_str = date_str[date_str.find(month):]
        
        date_obj = datetime.strptime(date_str, '%B %d %Y')
        return date_obj
        
    def get_company_hrefs(self):
        hrefs = []
        
        list_path = "//ul[contains(@class,'layouts level-1')]"
        list_elem = self.wait_for_and_find(list_path, tag_type='xpath')
        for child in list_elem.find_elements_by_xpath(".//*"):
            href = child.get_attribute("href")
            if href is not None:
                hrefs.append(href)
                
        return hrefs
    
    def get_application_hrefs(self):
        hrefs = []
        
        elems = scraper.driver.find_elements_by_tag_name("a")
        for elem in elems:
            try:
                href = elem.get_attribute("href")
                if href is not None and href[-5:].isnumeric():
                    hrefs.append(href)
            except:
                pass
        
        return hrefs
    
    def create_serfile(self):
        pass
    
    def scrape_website(self):
        self.gather_all_hrefs()

scraper = NYSerfScraper()
        
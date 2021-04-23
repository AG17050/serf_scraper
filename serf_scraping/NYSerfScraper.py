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
        url = 'https://myportal.dfs.ny.gov/web/prior-approval/aetna-health-inc.-ny-'
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
        
    def get_approved_row_date(self, i, app_type='approved'):
        xpath = f'//*[@id="portlet_56_INSTANCE_Qdc0BbdFovOv"]/div/div/div/div[1]/div[3]/ul/li/ul/li[{i}]/a'
        elem = self.wait_for_and_find(xpath)
        text = elem.text
        date_obj = self.extract_date_from_text(text)
        return date_obj
    
    def get_application_urls(self, i, app_type='approved'):
        urls = []
        for j in range(1, 500):
            if app_type == 'approved':
                try:
                    xpath = f'//*[@id="portlet_56_INSTANCE_Qdc0BbdFovOv"]/div/div/div/div[1]/div[3]/ul/li/ul/li[{i}]/ul/li[{j}]/a'
                    url = self.get_xpath_href(xpath)
                except:
                    break
                
            elif app_type == 'pending':
                xpath = f'//*[@id="portlet_56_INSTANCE_5UaY"]/div/div/div/div[2]/div[1]/ul/li/ul/li[{i}]/a'
                url = self.get_xpath_href(xpath)
                
            urls.append(url)
            print(f"len of urls: {len(urls)}")
        return urls
    
    def get_xpath_href(self, xpath):
        url_elem = self.wait_for_and_find(xpath, tag_type='xpath')
        url = url_elem.get_attribute("href")
        return url
    
    def gather_application_hrefs(self):
        for i in range(1, 500):
            date_obj = self.get_approved_row_date(i)
            if date_obj > self.start_date:
                self.get_application_urls(i)
                
            self.get_application_urls(i, app_type='pending')
    
    def __scroll_to_xpath(self, xpath):
        elem = self.wait_for_and_find(xpath, tag_type='xpath', wait_time=5)
        time.sleep(0.1)
        self.driver.execute_script("arguments[0].scrollIntoView();", elem)
        
    def gather_carrier_href(self, i):
        path = f'//*[@id="portlet_71_INSTANCE_9Q5y"]/div/div/div/div/ul/li[1]/ul/li[{i}]/a'
        self.__scroll_to_xpath(path)
        row_href = self.get_xpath_href(path)
        self.row_urls.append(row_href)
    
    def gather_all_hrefs(self):
        for i in range(1, 500):
            try: self.gather_carrier_href(i)
            except: break
        for url in self.row_urls:
            self.driver.get(url)
            self.gather_application_hrefs()
    
    # def hover_over_id(self, selector):
    #     elem = self.wait_for_and_find(selector)
    #     hover = ActionChains(self.driver).move_to_element(elem)
    #     hover.perform()
        
    def create_serfile(self):
        pass
    
    def scrape_website(self):
        self.gather_all_hrefs()
        
        
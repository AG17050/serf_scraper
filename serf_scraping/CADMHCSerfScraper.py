# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 13:50:40 2021

@author: AG17050
"""

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

class CADMHCSerfScraper(SerfScraper):
    
    def __init__(self):
        url = 'http://wpso.dmhc.ca.gov/premiumratereview/FilingList.aspx'
        super().__init__(url)
        self.__initial_setup()
        
        self.filing_urls = []
        
        # self.carrier_matcher = CarrierMatcher()
        self.file_tracker = FileTracker()
        
        # remove for deployment
        # self.file_tracker.wipe_download_records()
        
        self.num_downloads = len(os.listdir(get_download_path()))
    
    def __select_market_type(self):
        button_select = '#MainContentBody > article > div > div:nth-child(3) > div > div > div.filterbox.panel-heading > div > div:nth-child(3) > div > button'
        self.wait_for_and_find(button_select).click()
        
        ind_select = '#bs-select-2-0'
        self.wait_for_and_find(ind_select).click()
        sg_select = '#bs-select-2-3'
        self.wait_for_and_find(sg_select).click()
        
    def __select_filing_status(self):
        button_select = '#MainContentBody > article > div > div:nth-child(3) > div > div > div.filterbox.panel-heading > div > div:nth-child(4) > div > button'
        self.wait_for_and_find(button_select).click()
        
        completed_select = '#bs-select-4-0'
        self.wait_for_and_find(completed_select).click()
        inprogress_select = '#bs-select-4-1'
        self.wait_for_and_find(inprogress_select).click()
        
    def __select_file_type(self):
        button_select = '#MainContentBody > article > div > div:nth-child(3) > div > div > div.filterbox.panel-heading > div > div:nth-child(5) > div > button'
        self.wait_for_and_find(button_select).click()
        
        annual_filing_select = '#bs-select-3-0'
        self.wait_for_and_find(annual_filing_select).click()
        new_product_select = '#bs-select-3-1'
        self.wait_for_and_find(new_product_select).click()
        rate_filing_select = '#bs-select-3-2'
        self.wait_for_and_find(rate_filing_select).click()
        
    def __set_all(self):
        # Selecting 100 rows per page
        show_selector = '#gridfilings_length > label > select'
        select = Select(self.wait_for_and_find(show_selector, wait_time=60))
        select.select_by_visible_text('All')
        time.sleep(2)
        
    def __set_submission_date(self):
        dates_data = pd.read_csv('serf_submission_dates.txt')
        start_date_str = dates_data['Start Date'][0]
        self.start_date = standard_date(start_date_str)
        
    def __set_num_rows(self):
        row_info_select = '#gridfilings_info'
        row_info_str = self.wait_for_and_find(row_info_select).text
        str_list = row_info_str.split()
        int_list = [int(s) for s in str_list if s.isnumeric()]
        num_rows = sorted(int_list)[-2] # second highest number
        print(f"number of rows: {num_rows}")
        self.num_rows = num_rows
    
    def __collect_urls(self):
        self.__set_num_rows()
        print('Collecting URLs \n')
        for i in range(1, self.num_rows + 1):
            url_elem_path = f'//*[@id="gridfilings"]/tbody/tr[{i}]/td[1]/a'
            url_elem = self.wait_for_and_find(url_elem_path, tag_type='xpath')
            url = url_elem.get_attribute("href")
            self.filing_urls.append(url)
        print(f'{self.num_rows} urls collected.')
    
    def __initial_setup(self):
        self.__set_submission_date()
        self.__select_market_type()
        self.__select_filing_status
        # self.__select_file_type()
        self.__set_all()
    
    @staticmethod
    def __get_company(plan_name_str: str):
        return plan_name_str
    
    @staticmethod
    def __get_carrier(plan_name_str: str):
        return plan_name_str.split()[0]
    
    def __gather_base_data(self) -> dict:
        
        filing_nbr_select = '#filingNo'
        plan_name_select = '#healthPlanName'
        filing_type_select = '#filingType'
        market_select = '#marketType'
        status_select = '#filingStatus'
        effective_date_select = '#dtEffective'
        
        filing_number = self.wait_for_and_find(filing_nbr_select).text
        plan_name_str = self.wait_for_and_find(plan_name_select).text
        file_type = self.wait_for_and_find(filing_type_select).text
        market = self.wait_for_and_find(market_select).text
        status = self.wait_for_and_find(status_select).text
        effective_date = self.wait_for_and_find(effective_date_select).text
        
        state = 'CA_dmhc'
        carrier = self.__get_carrier(plan_name_str)
        company = self.__get_company(plan_name_str)
        current_path = get_download_path()
        
        base_data_dict = {
            'state':state,
            'carrier':carrier,
            'company':company,
            'market':market,
            'status':status,
            'effective_date':effective_date,
            'file_type':file_type,
            'current_path':current_path,
            'file_number':filing_number,
            'file_name':''
        }
        
        return base_data_dict
    
    def __get_num_attachments(self):
        attachments_select = '#viewAttachmentsHeader'
        num_attachments_str = self.wait_for_and_find(attachments_select).text
        str_list = num_attachments_str.split()
        number_str = str_list[-1]
        num_attachments = int(number_str[1:-1])
        return num_attachments
    
    def __get_file_date(self) -> str:
        date_filed_select = '#dtFiled'
        date_filed_str = self.wait_for_and_find(date_filed_select).text
        return date_filed_str
        
    def __after_startdate(self, date_filed_str: str) -> bool:
        date_filed = standard_date(date_filed_str)
        time.sleep(0.1)
        print('date filed:', date_filed, 'submission date', self.start_date)
        return date_filed >= self.start_date
    
    def create_serfile(self, data_dict) -> SerfFile:
        serfile = SerfFile(
            file_name=data_dict['file_name'],
            file_number=data_dict['file_number'],
            state=data_dict['state'], 
            carrier=data_dict['carrier'],
            company=data_dict['company'],
            market=data_dict['market'],
            status=data_dict['status'],
            current_path=data_dict['current_path'],
            effective_date=data_dict['effective_date'],
            file_type=data_dict['file_type'])
        return serfile
    
    def __check_for_update(self, base_data_dict: dict, file_date_str: str):
        # filing_path = '//*[@id="report_attachments"]/div/div[1]/table/tbody/tr[1]/td[1]'
        filing_path = '//*[@id="rateFilingAttachments"]/li[1]/a'
        file_name = self.wait_for_and_find(filing_path, tag_type='xpath').text
        base_data_dict['file_name'] = file_name
        
        serfile = self.create_serfile(base_data_dict)
        return self.file_tracker.update_pending(serfile, file_date_str)
        
    def __wait_for_download(self):
        files_downloaded = False
        
        for i in range(8):
            curr_num_downloads = len(os.listdir(get_download_path()))
            if curr_num_downloads > self.num_downloads:
                self.num_downloads = curr_num_downloads
                files_downloaded = True
                break
            else:
                time.sleep(5)
        
        if files_downloaded == False: raise Exception("File not downloading!")
        else: pass
    
    def __download_serfile_attachment(self, i: int, base_data_dict, file_date_str):
        filing_path = f'//*[@id="rateFilingAttachments"]/li[{i}]/a'
        
        # Waiting for the element to exist then finding it.
        file_elem = self.wait_for_and_find(filing_path, tag_type='xpath')
        file_elem.click()
        self.__wait_for_download()
        
        file_name = file_elem.text
        base_data_dict['file_name'] = file_name
        serfile = self.create_serfile(base_data_dict)
        self.serfiles.append(serfile)
        self.file_tracker.add_or_update_serfile(serfile, file_date_str)
        
    def __reveal_attachments(self):
        reveal_select = '#attachmentspanel > div.panel-body.clearfix'
        elem = self.wait_for_and_find(reveal_select)
        elem.click()
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].scrollIntoView();", elem)
        
        
    def __download_if_update(self, base_data_dict: dict, file_date_str):
        self.__reveal_attachments()
        num_attachments = self.__get_num_attachments()
        
        if (num_attachments > 0) and \
            (self.__check_for_update(base_data_dict, file_date_str)):
        
            for i in range(1, num_attachments + 1):
                self.__download_serfile_attachment(
                    i, 
                    base_data_dict,
                    file_date_str
                )
    
    def __process_row(self, i: int):
        url = self.filing_urls[i]
        self.driver.get(url)
        time.sleep(.5)
        
        file_date_str = standard_date_str(self.__get_file_date())
        if self.__after_startdate(file_date_str):
            base_data_dict = self.__gather_base_data()
            self.__download_if_update(base_data_dict, file_date_str)
            return True
        else:
            return False

    def __rename_serfiles_filenames(self):
        download_path = get_download_path()
        paths = sorted(Path(download_path).iterdir(), key=os.path.getmtime)
        
        # exclude the foldersr
        paths = [p for p in paths if '.' in str(p)]
        print(len(paths), len(self.serfiles))
        if len(paths) > 0:
            for i, x in enumerate(paths):
                path = str(paths[i])
                file_name = path[path.rfind('/')+1:]
                self.serfiles[i].data_dict['file_name'] = file_name
            
    def scrape_website(self):
        break_counter = 0
        
        self.__collect_urls()
        for i in range(self.num_rows):
            if self.__process_row(i) == True:
                pass
            else:
                break_counter += 1
                if break_counter == 3:
                    break
        time.sleep(15)
            
        self.file_tracker.save_files_dict()
        self.__rename_serfiles_filenames()
        self.driver.close()
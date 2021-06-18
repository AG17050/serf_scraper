# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 13:50:08 2021

@author: AG17050
"""

from SerfScraper import SerfScraper
from CommonDriver import Select
from file_downloading import SerfFile
from utils import standard_date_str, get_download_path
from scraper_config import accepted_groups, accepted_status, non_accepted_groups, insurance_types
from selenium.webdriver.common.keys import Keys
from file_collection import FileTracker
from carrier_matching import CarrierMatcher
import pandas as pd
import os
import time
import math

class CommonSerfScraper(SerfScraper):
    
    def __init__(self, url):
        super().__init__(url)
        print("running for url: ",  url)
        self.__initial_setup()
        
        self.num_pages = None
        self.no_more_rows = False
        
        self.carrier_matcher = CarrierMatcher()
        self.file_tracker = FileTracker()
        
        # self.file_tracker.wipe_download_records()
        
        self.num_downloads = len(os.listdir(get_download_path()))
        
    def __begin_search(self):
        begin_selector = "#bodyContentWrapper > div > a"
        begin = self.wait_for_and_find(begin_selector, wait_time=60)
        begin.click()
    
    def __accept_search(self):
        accept_select = "#j_idt18\:j_idt20"
        accept = self.wait_for_and_find(accept_select)
        accept.click()
    
    def __select_business_type(self):
        business_selector = "#simpleSearch\:businessType_label"
        select = self.wait_for_and_find(business_selector, wait_time=10)
        select.click()
        
        business_selector = "#simpleSearch\:businessType_panel > div > ul > li:nth-child(3)"
        business = self.wait_for_and_find(business_selector)
        business.click()
    
    def __select_insurance_types(self):
        insurance_selector = "#simpleSearch\:availableTois > a > label"
        select = self.wait_for_and_find(insurance_selector, wait_time=40)
        select.click()
        
        for i in range(1,120):
            try:
                ins_path = '//*[@id="simpleSearch:availableTois_panel"]/div[2]/ul/li[{}]/label'.format(i)
                ins = self.wait_for_and_find(ins_path, tag_type='xpath')
                if ins.text in insurance_types:
                    ins.click()
            except Exception as e:
                print(e)
                break
    
    def __select_start_date(self):
        dates_data = pd.read_csv('serf_submission_dates.txt')
        start_date = dates_data['Start Date'][0]
        print(f"Using start date: {start_date}")
    
        # Sending the start date
        start_date_input_id = '#simpleSearch\:submissionStartDate_input'
        start_date_input = self.driver.find_element_by_css_selector(start_date_input_id)
        start_date_input.send_keys(start_date)
    
    def __submit_search(self):
        search_selector = '#simpleSearch\:saveBtn > span'
        search = self.wait_for_and_find(search_selector)
        search.click()
        
    def __set_100(self):
        # Selecting 100 rows per page
        show_selector = '#j_idt25\:filingTable_rppDD'
        select = Select(self.wait_for_and_find(show_selector, wait_time=100))
        select.select_by_visible_text('100')
    
    def __initial_setup(self):
        self.__begin_search()
        self.__accept_search()
        
        self.__select_business_type()
        self.__select_insurance_types()
        self.__select_start_date()
        self.__submit_search()
        self.__set_100()
        time.sleep(2)
        
    def __find_num_pages(self):
        """
        Run to find the number of pages on the site.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        pages_selector = '#j_idt25\:filingTable_paginator_top > span.ui-paginator-current'
        page_elem = self.wait_for_and_find(pages_selector, wait_time=50)
        page_text = page_elem.text
        pages = page_text[page_text.find('of')+3:].replace(')','')
        print('Number of pages: {}'.format(pages))
        return int(pages)
    
    def next_page(self):
        """
        Function. used to go to next page.

        Returns
        -------
        None.

        """
        self.driver.execute_script("window.scroll(0, 0);")
        next_selector = '#j_idt25\:filingTable_paginator_top > span.ui-paginator-next.ui-state-default.ui-corner-all'
        next_elem = self.wait_for_and_find(next_selector)
        try:
            next_elem.click()
            time.sleep(1)
        except:
            time.sleep(2)
            next_elem.click()
        
    @staticmethod
    def __valid_status(status_str: str):
        status_str = status_str.lower()
        return status_str in accepted_status
    
    @staticmethod
    def __valid_product(product_name_str: str, sub_type_str: str):        
        in_groups = [i for i in accepted_groups if i in product_name_str.split()]
        in_subs = [i for i in accepted_groups if i in sub_type_str.split()]
        
        out_groups = [i for i in non_accepted_groups if i in product_name_str.split()]
        out_subs = [i for i in non_accepted_groups if i in sub_type_str.split()]
    
        in_all = in_groups + in_subs
        out_all = out_groups + out_subs
        if len(in_all) > 0 and len(out_all) == 0:
            return True, in_all[0]
        else:
            return False, None
        
    @staticmethod
    def __try_m_y_format(product_name_str: str):
        def numeric_hyphen(string):
            if '-' in string:
                substring = string.replace('-','')
                return substring.isnumeric()
        
        str_list = product_name_str.split()
        numeric_hyphen_strs = [s for s in str_list if numeric_hyphen(s)]
        date_str = numeric_hyphen_strs[0]

        hyphen_idx = date_str.find('-')
        left = date_str[:hyphen_idx]; right = date_str[hyphen_idx+1:]
        if int(right) > int(left):
            return f'{int(left)}_{int(right)}_'
        
        return ''
        
    @staticmethod
    def __try_qy_format(product_name_str: str):
        str_list = product_name_str.split()
        qy_strs = [s for s in str_list if 'q' in s and '2' in s]
        
        if len(qy_strs) > 0:
            qy_str = qy_strs[0]
            q_idx = qy_str.find('q')
            year = qy_str[q_idx + 1:]
            year = '20' + year if len(year) == 2 else year
            quarter = qy_str[:q_idx]
            return f'{year}_{quarter}_'
        else:
            return ''
        
    @staticmethod
    def __get_numeric_year(product_name_str: str):
        years = ['2018','2019','2020','2021','2022','2023','2024']
        found_years = [y for y in years if y in product_name_str]
        if len(found_years) > 0:
            found_year = found_years[0]
            year_idx = product_name_str.find(found_year)
            return found_year, year_idx
        else:
            return '',-1
    
    @staticmethod
    def __get_numeric_month(product_name_str: str, year_idx: int):
        months = [str(x) for x in list(range(1,12))]
        months += ['01','02','03','04','05','06','07','08','09']
        
        found_months = [m for m in months if m in product_name_str]
        found_month = ''
        for m in found_months:
            m_idx = product_name_str.find(m)
            idx_diff = m_idx - year_idx
            
            if (idx_diff < 0 and abs(idx_diff) >= len(m)) \
            or (idx_diff >= 4):
                found_month = m
                break
            
        return found_month
            
            
    @staticmethod
    def __try_standard_date(product_name_str: str):
        if '/' in product_name_str:
            try:
                str_list = product_name_str.split(' ')
                date_str = [s for s in str_list if '/' in s and len(s) > 4][0]
                eff_date = standard_date_str(date_str)
                return eff_date
            except Exception as e:
                print("standard date error!!!")
                print(e)
                return ''
        else:
            return ''
        

    def get_effective_date(self, product_name_str: str):
        """
        

        Parameters
        ----------
        product_name_str : str
            DESCRIPTION.

        Returns
        -------
        eff_date : TYPE
            DESCRIPTION.

        """
        product_name_str = product_name_str.lower()
        
        eff_date = self.__try_standard_date(product_name_str)
        if eff_date != '':
            return eff_date
        
        eff_date = self.__try_qy_format(product_name_str)
        if eff_date != '':
            return eff_date
        else:
            quarter = ''
        
        year, yr_idx = self.__get_numeric_year(product_name_str)
        if year == '':
            return '__'
        
        month = self.__get_numeric_month(product_name_str, yr_idx)
        
        return f'{year}_{quarter}_{month}'
    
    def __gather_row_info(self, i) -> (bool, dict):
        """
        

        Parameters
        ----------
        i : TYPE
            DESCRIPTION.

        Returns
        -------
        bool, dict
            DESCRIPTION.

        """
            
        company_path = f'//*[@id="j_idt25:filingTable_data"]/tr[{i}]/td[1]'
        prod_name_path = f'//*[@id="j_idt25:filingTable_data"]/tr[{i}]/td[3]'
        sub_type_path = f'//*[@id="j_idt25:filingTable_data"]/tr[{i}]/td[4]'
        filing_type_path = f'//*[@id="j_idt25:filingTable_data"]/tr[{i}]/td[5]'
        filing_status_path = f'//*[@id="j_idt25:filingTable_data"]/tr[{i}]/td[6]'
        tracking_number_path = f'//*[@id="j_idt25:filingTable_data"]/tr[{i}]/td[7]'
        
        company = self.wait_for_and_find(company_path, tag_type='xpath', wait_time=60).text
        carrier = self.carrier_matcher.match_to_carrier(company)
        
        product_name_str = self.wait_for_and_find(prod_name_path, tag_type='xpath').text
        sub_type_str = self.wait_for_and_find(sub_type_path, tag_type='xpath').text
        is_valid_product, market = self.__valid_product(product_name_str, sub_type_str)
        
        status_str = self.wait_for_and_find(filing_status_path, tag_type='xpath').text
        is_valid_status = self.__valid_status(status_str)
        status = status_str
        
        file_type = self.wait_for_and_find(filing_type_path, tag_type='xpath').text
        file_name = self.wait_for_and_find(tracking_number_path, tag_type='xpath').text
        
        current_path = get_download_path()  

        effective_date = self.get_effective_date(self.wait_for_and_find(
            prod_name_path, tag_type='xpath').text)
        # effective_date = self.__effective_date
        
        data_dict = {
            'state':self.state,
            'carrier':carrier,
            'company':company,
            'market':market,
            'status':status,
            'effective_date':effective_date,
            'file_type':file_type,
            'current_path':current_path,
            'file_number':file_name,
            'file_name':file_name+'.zip',
        }
        
        if is_valid_product and is_valid_status:
            print("valid row")
            return True, data_dict,
        else:
            return False, {}
        
    
    def inspect_row(self, i):
        row_path = f'//*[@id="j_idt25:filingTable_data"]/tr[{i}]'
        valid, data_dict = self.__gather_row_info(i)
        
        if valid:
            row_elem = self.wait_for_and_find(row_path, tag_type='xpath')
            row_elem.click()
            print(f'engaging row {i}')
            self.__engage_row(data_dict)
        else:
            pass
    
    def __try_getting_date(self, date_selector):
        """
        Run to command driver to go to next page.

        Parameters
        ----------
        date_selector : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        try:
            date_str = self.wait_for_and_find(date_selector).text
            return date_str
        except Exception as e:
            print(e)
            return ''
        
    def __get_last_updated_date(self):
        print("Getting date of last update")
        # collect State last changed date and standardize
        last_selector = '#j_idt34 > div:nth-child(2) > div'
        last_status_date = self.__try_getting_date(last_selector)
        last_status_date = standard_date_str(last_status_date)
        
        # collect Disposition date and standardize
        dispose_selector = '#j_idt28_content > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > div'
        dispose_date = self.__try_getting_date(dispose_selector)
        dispose_date = standard_date_str(dispose_date)
        
        # collect Date Submitted and standardize
        date_selector = '#j_idt28_content > div:nth-child(1) > div:nth-child(1) > div:nth-child(7) > div'
        sub_date = self.__try_getting_date(date_selector)
        sub_date = standard_date_str(sub_date)

        dates_list = [last_status_date, dispose_date, sub_date]
        date = [d for d in dates_list if d != ''][0]
        return date
    
    
    def __download_zip(self):
        """
        Run to download the zip files.

        Returns
        -------
        None.

        """
        # Download the Zip
        forms_select = '#formAttachmentSelectCurrentButton'
        rate_select = '#rateRuleAttachmentSelectCurrentButton'
        doc_select = '#supportingDocumentAttachmentSelectCurrentButton'
        corr_select = '#correspondenceAttachmentSelectAllButton'
        download_select = '#summaryForm\:downloadLink'
        
        self.wait_for_and_find(forms_select).click(); time.sleep(0.5)
        self.wait_for_and_find(rate_select).click(); time.sleep(0.5)
        self.wait_for_and_find(doc_select).click(); time.sleep(0.5)
        self.wait_for_and_find(corr_select).click(); time.sleep(0.5)
        self.wait_for_and_find(download_select).click(); time.sleep(0.5)
        
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
        
    def __wait_for_downloads(self):
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
    
    def __back_browser(self):
        """
        Run to set the driver back one page.

        Returns
        -------
        None.

        """
        self.driver.execute_script("window.history.go(-1)")
        time.sleep(1)
        
    def __engage_row(self, data_dict: dict):
        serfile = self.create_serfile(data_dict)
        date_str = self.__get_last_updated_date()
        if self.file_tracker.update_pending(serfile, date_str):
            self.__download_zip()
            self.file_tracker.add_or_update_serfile(serfile, date_str)
            self.serfiles.append(serfile)
            self.__wait_for_downloads()
            
        self.__back_browser()
    
    def scrape_page(self):
        for i in range(1,101):
            try:
                print(f'inspecting row {i}')
                self.inspect_row(i)
                
            except Exception as e:
                self.no_more_rows = True
                print('No More Rows in Page.', e)
                break
                
        print("Finished page.")
        
    def scrape_website(self):
        """
        Run to begin assessment of all rows in serial.

        Returns
        -------
        None.

        """
        
        self.num_pages = self.__find_num_pages()
        for page_num in range(self.num_pages):
            
            if self.no_more_rows == False:
                self.scrape_page()
                self.next_page()
                print('went to next page')
            else:
                break

        time.sleep(30)
        self.file_tracker.save_files_dict()
        self.driver.close()
    

# url = 'https://filingaccess.serff.com/sfa/home/CO'
# serfer = CommonSerfScraper(url)
# serfer.scrape_website()

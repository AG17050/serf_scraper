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

class CACDISerfScraper(SerfScraper):
    
    def __init__(self):
        url = 'https://interactive.web.insurance.ca.gov/apex_extprd/f?p=102:InteractiveReport:0::NO:4,RIR::'
        super().__init__(url)
        self.__initial_setup()
        
        self.filing_urls = []
        
        self.file_tracker = FileTracker()
        # self.file_tracker.wipe_download_records()
        
        self.num_downloads = len(os.listdir(get_download_path()))
        
    def __set_all(self):
        # Selecting 100 rows per page
        show_selector = '#Search\ Rate\ Filings_row_select'
        select = Select(self.wait_for_and_find(show_selector, wait_time=60))
        select.select_by_visible_text('All')
        time.sleep(2)
        
    def __set_submission_date(self):
        dates_data = pd.read_csv('serf_submission_dates.txt')
        start_date_str = dates_data['Start Date'][0]
        self.start_date = standard_date(start_date_str)
        
    def __initial_setup(self):
        self.__set_all()
        self.__set_submission_date()
        
    def __set_num_rows(self):
        row_info_select = '#Search\ Rate\ Filings_data_panel > div.a-IRR-paginationWrap.a-IRR-paginationWrap--bottom > ul > li:nth-child(2) > span'
        row_info_str = self.wait_for_and_find(row_info_select).text
        str_list = row_info_str.split()
        int_list = [int(s) for s in str_list if s.isnumeric()]
        num_rows = max(int_list) # second highest number
        print(f"number of rows: {num_rows}")
        self.num_rows = num_rows
        
    def __is_sgind_row(self, i):
        url_elem_path = f'//*[@id="34755269525011373"]/tbody/tr[{i}]/td[4]'
        url_elem = self.wait_for_and_find(url_elem_path, tag_type='xpath')
        cvg = url_elem.text
        return (cvg != 'Large Group') and (cvg in ['Small Group','Individual'])
    
    def __collect_urls(self):
        self.__set_num_rows()
        print('Collecting URLs \n')
        for i in range(2, self.num_rows + 2):
            if self.__is_sgind_row(i):    
                url_elem_path = f'//*[@id="34755269525011373"]/tbody/tr[{i}]/td[2]/a'
                url_elem = self.wait_for_and_find(url_elem_path, tag_type='xpath')
                url = url_elem.get_attribute("href")
                self.filing_urls.append(url)
        print(f'{self.num_rows} urls collected.')
        
    @staticmethod
    def __get_carrier(company_name_str: str):
        idx = company_name_str.find(' Insurance Company')
        carrier = company_name_str[:idx]
        return carrier
    
    def __gather_base_data(self):
        
        company_name_select = '#R34739679176854560_heading'
        filing_nbr_select = '#generalfilingdetails > table > tbody > tr:nth-child(2) > td'
        market_select = '#generalfilingdetails > table > tbody > tr:nth-child(1) > td'
        effective_date_select = '#generalfilingdetails > table > tbody > tr:nth-child(6) > td'
        status_select = '#container > table > tbody > tr > td'
        
        company_name_str = self.wait_for_and_find(company_name_select).text
        filing_number = self.wait_for_and_find(filing_nbr_select).text
        file_type = 'Rate Filing'
        market = self.wait_for_and_find(market_select).text
        effective_date = self.wait_for_and_find(effective_date_select).text
        effective_date = standard_date_str(effective_date)
        status_str = self.wait_for_and_find(status_select).text
        
        state = 'CA_cdi'
        carrier = self.__get_carrier(company_name_str)
        company = company_name_str
        current_path = get_download_path()
        status = status_str
        
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
        attachments_select = '#attachments_heading'
        num_attachments_str = self.wait_for_and_find(attachments_select).text
        str_list = num_attachments_str.split()
        number_str = str_list[-1]
        num_attachments = int(number_str[1:-1])
        return num_attachments
    
    def __get_file_date(self) -> str:
        date_filed_select = '#generalfilingdetails > table > tbody > tr:nth-child(4) > td'
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
        filing_path = '//*[@id="report_attachments"]/div/div[1]/table/tbody/tr[1]/td[1]'
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
    
    @staticmethod
    def __get_paths():
        download_path = get_download_path()
        paths = sorted(Path(download_path).iterdir(), key=os.path.getmtime)
        
        # exclude the folders
        paths = [p for p in paths if '.' in str(p)]
        # print(len(paths), len(self.serfiles))
        return paths
        
        
    def __download_serfile_attachment(self, i: int, base_data_dict, file_date_str):
        filing_path = f'//*[@id="report_attachments"]/div/div[1]/table/tbody/tr[{i}]/td[1]'
        download_path = f'//*[@id="report_attachments"]/div/div[1]/table/tbody/tr[{i}]/td[2]/a'

        # Waiting for the element to exist then finding it.
        for i in range(4):
            try:
                file_elem = self.wait_for_and_find(filing_path, tag_type='xpath')
                file_name = file_elem.text
                download_elem = self.wait_for_and_find(download_path, tag_type='xpath')
                download_elem.click()
                self.__wait_for_download()
                break
            except:
                self.driver.refresh()
                time.sleep(3)
                
            # File isn't downloading
            return
        
        base_data_dict['file_name'] = file_name
        serfile = self.create_serfile(base_data_dict)
        self.serfiles.append(serfile)
        self.file_tracker.add_or_update_serfile(serfile, file_date_str)
        
    def __reset_pagination(self):
        reset_select = '#attachments > div.t-Region-bodyWrap > div.t-Region-body > table > tbody > tr > td > div > div > a'
        elem = self.wait_for_and_find(reset_select)
        elem.click()
        time.sleep(0.5)
        
    def __scroll_to_attachments(self):
        attachments_select = '#ATTACHMENT_NAME'
        elem = self.wait_for_and_find(attachments_select)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].scrollIntoView();", elem)
        
    def __next_page(self):
        next_select = '#report_attachments > div > table.t-Report-pagination.t-Report-pagination--bottom > tbody > tr > td > table > tbody > tr > td:nth-child(4) > a'
        elem = self.wait_for_and_find(next_select)
        elem.click()
        time.sleep(0.5)
        
    def __prev_page(self):
        prev_select = '#report_attachments > div > table.t-Report-pagination.t-Report-pagination--bottom > tbody > tr > td > table > tbody > tr > td:nth-child(2) > a'
        elem = self.wait_for_and_find(prev_select)
        elem.click()
        time.sleep(0.5)
        
    def __prev_page_protect(self):
        try:
            self.__prev_page()
        except:
            pass
        
    def __attachments_or_reset(self):
        try:
            self.__scroll_to_attachments()
        except:
            self.__reset_pagination()
            self.__scroll_to_attachments()
        
    def __download_if_update(self, base_data_dict: dict, file_date_str):
        self.__attachments_or_reset()
        num_attachments = self.__get_num_attachments()
        self.__prev_page_protect()
        
        if (num_attachments > 0) and \
            (self.__check_for_update(base_data_dict, file_date_str)):
        
            for i in range(1, num_attachments + 1):
                idx = i if i == 15 else i % 15
                self.__download_serfile_attachment(
                    idx, 
                    base_data_dict,
                    file_date_str
                )
                if (i % 15 == 0) and (num_attachments > 15):
                    self.__next_page()
            time.sleep(3)
            print(f"len serfiles: {len(self.serfiles)}, len paths: {len(self.__get_paths())}")
                    
        
    def __process_row(self, i: int) -> bool:
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
        paths = self.__get_paths()
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
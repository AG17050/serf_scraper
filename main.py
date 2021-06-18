# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 12:47:56 2021

@author: AG17050
"""
import os
from zipfile import ZipFile
import shutil
import pandas as pd
from serf_scraping import CommonSerfScraper, CACDISerfScraper, CADMHCSerfScraper #, NYSerfScraper
from file_collection import FileCollector
from utils import get_download_path, unzip_path, get_quarter
from pdf_parsing import find_pdf_effective_date

def get_serf_states_to_run():
    serf_sites = [
        "https://filingaccess.serff.com/sfa/home/CO",
        "https://filingaccess.serff.com/sfa/home/CT",
        "https://filingaccess.serff.com/sfa/home/GA",
        "https://filingaccess.serff.com/sfa/home/IN",
        "https://filingaccess.serff.com/sfa/home/KY",
        "https://filingaccess.serff.com/sfa/home/ME",
        "https://filingaccess.serff.com/sfa/home/MO",
        "https://filingaccess.serff.com/sfa/home/NV",
        "https://filingaccess.serff.com/sfa/home/NH",
        "https://filingaccess.serff.com/sfa/home/OH",
        "https://filingaccess.serff.com/sfa/home/VA"
    ]
      
    state_serf_site_dict = dict(
        zip([string[-2:] for string in serf_sites], serf_sites)
    )
    
    states_df = pd.read_csv('serf_states_to_run.csv')
    states_dict = dict(zip(states_df['State'], states_df['Run']))
    
    states_to_run = {}
    for state in state_serf_site_dict:
        if states_dict[state] == 'Yes':
            states_to_run[state] = state_serf_site_dict[state]
    return states_to_run
            
def get_common_serf_collection():
    states_to_run = get_serf_states_to_run()
    collected_serfiles = []
    
    for state, url in states_to_run.items():
        serfer = CommonSerfScraper(url)
        serfer.scrape_website()
        collected_serfiles += serfer.serfiles
    
    return collected_serfiles
        
def get_ca_cdi_serf_collection():
    df = pd.read_csv('serf_states_to_run.csv')
    ca_val = df[df['State'] == 'CA']['Run'].values[0]
    
    if ca_val == 'Yes':
        cdi_scraper = CACDISerfScraper()
        cdi_scraper.scrape_website()
        collected_serfiles = cdi_scraper.serfiles
        return collected_serfiles
    else:
        return []

def get_ca_dmhc_serf_collection():
    df = pd.read_csv('serf_states_to_run.csv')
    ca_val = df[df['State'] == 'CA']['Run'].values[0]
    
    if ca_val == 'Yes':
        dmhc_scraper = CADMHCSerfScraper()
        dmhc_scraper.scrape_website()
        collected_serfiles = dmhc_scraper.serfiles
        return collected_serfiles
    else:
        return []

def temp_unzip_pdf(file) -> str:
    download_path = get_download_path()
    temp_path = os.path.join(download_path, 'temp')
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path, ignore_errors=True)
    os.mkdir(temp_path)
        
    with ZipFile(file) as zipObj:
        zipObj.extractall(temp_path)
    
    pdf_file = [f for f in os.listdir(temp_path) if f .endswith('.pdf')][0]
    pdf_file = os.path.join(temp_path, pdf_file)
    return pdf_file
    

def get_zip_eff_date(zip_file_name):
    download_path = get_download_path()
    file = os.path.join(download_path, zip_file_name)
    pdf_file = temp_unzip_pdf(file)
    effective_date = find_pdf_effective_date(pdf_file)
    return effective_date

def rename_serfile_eff_dates(serfiles):
    for i, file in enumerate(serfiles):
        zip_file_name = file.data_dict['file_name']
        effective_date = get_zip_eff_date(zip_file_name)
        
        if effective_date != '':
            print(effective_date)
            effective_date = get_quarter(effective_date)
            serfiles[i].data_dict['effective_date'] = effective_date
            
    return serfiles

def unzip_downloads():
    download_path = get_download_path()
    try:
        unzip_path(download_path)
    except:
        print('Finished unzipping folders.')

def main():
    collector = FileCollector()
    collector.move_old_dl_files()
    
    serfiles = get_ca_cdi_serf_collection()
    collector.relocate_files(serfiles)
    
    serfiles = get_ca_dmhc_serf_collection()
    collector.relocate_files(serfiles)
    
    serfiles = get_common_serf_collection()
    serfiles = rename_serfile_eff_dates(serfiles)
    collector.relocate_files(serfiles)
    
    downloads_path = get_download_path()
    path = os.path.join(downloads_path, 'temp')
    
    if os.path.exists(path):
        shutil.rmtree(path)
    
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()

# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 14:14:28 2021

@author: AG17050
"""
from utils import get_download_path
from pathlib import Path
import shutil
import os
from typing import List
from utils import market_agg, get_quarter
import time

class SerfFile:
    
    def __init__(self, file_name: str, file_number: str, current_path=None,
                 state=None, carrier=None, company=None, market=None, 
                 effective_date=None, file_type=None, status=None):
        
        if not state:
            state = 'no_state'
        if not carrier:
            carrier = 'no_carrier'
        if not company:
            company = 'no_company'
        if not market:
            market = 'no_market'
        if not effective_date:
            effective_date = 'no_effective_date'
        if not file_type:
            file_type = 'no_filetype'
        if not current_path:
            current_path='no_current_path'
        if not file_number:
            file_number = 'no_file_number'
        if not status:
            status = 'no_status'
        
        self.data_dict = {
            'state':state,
            'company':company,
            'carrier':carrier,
            'market':market,
            'effective_date':effective_date,
            'file_type':file_type,
            'status': status,
            'current_path':current_path,
            'file_number': file_number,
            'file_name':file_name
        }
        
        self.data_dict['market'] = market_agg(self.data_dict['market'])
        
        if '_' in self.data_dict['effective_date']: # not just year__
            # Assumes a format of 'year_quarter_month'
            print(self.data_dict['effective_date'])
            str_split = self.data_dict['effective_date'].split('_')
            year = str_split[0]
            
            quarter = str_split[1]
            if quarter != '':
                self.data_dict['effective_date'] = f'{year}_Q{quarter}'
                
            month = str_split[2].zfill(2)
            if month != '00':
                self.data_dict['effective_date'] = get_quarter(f'{month}/01/{year}')
        
        elif '/' in self.data_dict['effective_date']:
            self.data_dict['effective_date'] = get_quarter(self.data_dict['effective_date'])

class DLRelocator:
    
    def __init__(self, serfile_list: List[SerfFile]):
        self.serfile_list = serfile_list
        self.file_order = ['state','market','carrier','company','effective_date',
                           'status','file_type','file_number']
        self.wd = get_download_path()
        
    def __get_folder_path(self, data_dict):
        folder_path = self.wd
        for comp in self.file_order:
            try:
                folder_path = os.path.join(folder_path, data_dict[comp].replace('/','-'))
            except:
                print(data_dict)
                raise(Exception("Tis Broke"))
        return folder_path
    
    @staticmethod
    def __create_necessary_folders(folder_path):
        path = Path(folder_path)
        path.mkdir(parents=True, exist_ok=True)
            
    def relocate_file(self, serfile: SerfFile):
        data_dict = serfile.data_dict
        dest_folder_path = self.__get_folder_path(data_dict)
        self.__create_necessary_folders(dest_folder_path)
        
        file_path = os.path.join(data_dict['current_path'], data_dict['file_name'])
        try:
            shutil.move(file_path, dest_folder_path)
        except:
            time.sleep(1)
            shutil.move(file_path, dest_folder_path)
            
    def relocate_files(self, serfile_list: List[SerfFile]):
        for serfile in serfile_list:
            self.relocate_file(serfile)
        
        
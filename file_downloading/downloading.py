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


class DLRelocator:
    
    def __init__(self, serfile_list: List[SerfFile]):
        self.serfile_list = serfile_list
        self.file_order = ['state','market','carrier','status','company',
                           'effective_date','file_type', 'file_number']
        # self.file_order = ['state','carrier','company','market',
        #                    'effective_date','file_type', 'file_number']
        self.wd = get_download_path()
        
    def __get_folder_path(self, data_dict):
        folder_path = self.wd
        for comp in self.file_order:
            folder_path = os.path.join(folder_path, data_dict[comp].replace('/','-'))
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
        shutil.move(file_path, dest_folder_path)
        
    def relocate_files(self, serfile_list: List[SerfFile]):
        for serfile in serfile_list:
            self.relocate_file(serfile)
        
        
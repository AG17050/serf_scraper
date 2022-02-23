# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 11:54:19 2021

@author: AG17050
"""

from utils import get_download_path, create_folder, move_files_to_folder, save_obj, load_obj, standard_date_str, standard_date
from typing import List
from file_downloading import SerfFile, DLRelocator
import os

class FileCollector:
    
    def move_old_dl_files(self):
        download_path = get_download_path()
        dl_files = os.listdir(download_path)
        
        if dl_files == ['Moved_Downloads_Content']:
            pass
        elif len(dl_files) > 0:
            dl_storage = os.path.join(download_path, 'Moved_Downloads_Content')
            if 'Moved_Downloads_Content' not in dl_files:
                create_folder(dl_storage) 
            move_files_to_folder(download_path, dl_storage)
            print("Moved old files into folder: 'Moved_Downloads_Content'")
            
        else:
            print("Thank you for emptying the downloads folder.")
            
    def relocate_files(self, serfile_list: List[SerfFile]):
        self.relocator = DLRelocator(serfile_list)
        self.relocator.relocate_files(serfile_list)
        
        
class FileTracker:
    
    def __init__(self, file_name='file_collection/downloaded_files'):
        self.file_name = file_name
        self.files_dict = load_obj(file_name)
        
    def wipe_download_records(self):
        self.files_dict = {}
        self.save_files_dict()
    
    def serfile_in_records(self, serfile: SerfFile) -> bool:
        dict_str = str(serfile.data_dict)
        return dict_str in self.files_dict
    
    @staticmethod
    def __check_standard_date(date_str):
        try:
            standard_date_str(date_str)
            pass
        except Exception as e:
            raise e
    
    def add_or_update_serfile(self, serfile: SerfFile, date_str):
        dict_str = str(serfile.data_dict)
        self.__check_standard_date(date_str)
        self.files_dict[dict_str] = date_str
        
    def update_pending(self, serfile: SerfFile, date_str) -> bool:
        """
        Check if there's an update for the SerfFile by comparing the date stored
        with the input date.
        ----------
        serfile : SerfFile
            DESCRIPTION.
        date_str : TYPE
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        self.__check_standard_date(date_str)
        input_date = standard_date(date_str)
        
        dict_str = str(serfile.data_dict)
        if dict_str in self.files_dict:
            date_str = self.files_dict[dict_str]
            current_date = standard_date(date_str)
            return (current_date > input_date)
        
        else:
            return True
            
    def save_files_dict(self):
        save_obj(self.files_dict, self.file_name)
        
    
        
        
        
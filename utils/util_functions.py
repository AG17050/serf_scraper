# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 15:26:56 2021

@author: AG17050
"""

import os
import shutil
from datetime import datetime
import pickle
from zipfile import ZipFile
# sys.path.insert(0, os.path.realpath(os.path.dirname(__file)))

def get_download_path():
    """
    

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')
    
def create_folder(folder_path):
    """
    

    Parameters
    ----------
    folder_path : TYPE
        DESCRIPTION.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    else:
        raise Exception(f"There is a {folder_path} folder already.")
        
def move_files_to_folder(source_path, dest_path, file_ext=None):
    """
    

    Parameters
    ----------
    source_path : TYPE
        DESCRIPTION.
    dest_path : TYPE
        DESCRIPTION.
    file_ext : TYPE, optional
        DESCRIPTION,

    Returns
    -------
    None.

    """
    source = os.listdir(source_path)
    if file_ext:
        for files in source:
            if files.endswith(file_ext):
                shutil.move(os.path.join(source_path, files), dest_path)
    else:
        files = os.listdir(source_path)
        for file in source:
            shutil.move(os.path.join(source_path, file), dest_path)
    
def standard_date_str(date_string):
    """
    This function is a standardizer for string dates and always returns 
    a string of format 'mm/dd/YY'.
    
    Will return an empty string if the string date is invalid.
    
    The class operates with the defined functions:
        - find_num_pages
        - check_row_validity
        - download_zips
    """
    yi = date_string.rfind('/') + 1
    if len(date_string[yi:]) > 2:
        date_string = date_string[:yi] + date_string[yi+2:]
        
    if '-' in date_string:
        date_obj = datetime.strptime(date_string, "%m-%d-%y")
        date_str = date_obj.strftime('%m/%d/%y')
        return date_str
            
    elif '/' in date_string:
        date_obj = datetime.strptime(date_string, "%m/%d/%y")
        date_str = date_obj.strftime('%m/%d/%y')
        return date_str
    
    else:
        return ''
    
def standard_date(date_string):
    """
    This function is a standardizer for string dates and always returns 
    a string of format 'mm/dd/YY'.
    
    Will return an empty string if the string date is invalid.
    
    The class operates with the defined functions:
        - find_num_pages
        - check_row_validity
        - download_zips
    """
    if "destruction" in date_string:
        idx = date_string.find("destruction")
        date_string = date_string[:idx]
        
    yi = date_string.rfind('/') + 1
    if len(date_string[yi:]) > 2:
        date_string = date_string[:yi] + date_string[yi+2:]
        
    if '-' in date_string:
        date_obj = datetime.strptime(date_string, "%m-%d-%y")
        return date_obj
            
    elif '/' in date_string:
        date_obj = datetime.strptime(date_string, "%m/%d/%y")
        return date_obj
    
    else:
        return ''
    
def get_quarter(date):
    if type(date) == str:
        date = standard_date(date)
    month = date.month
    year = date.year
    quarter = (month-1)//3 + 1
    return f'{year}_Q{quarter}'
    
# Dictionary saving/loading functions
def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def unzip_path(path, total_count=0):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file)
            if (not file_name.endswith('.zip')):
                # total_count += 1
                pass
            else:
                currentdir = file_name[:-4]
                if not os.path.exists(currentdir):
                    os.makedirs(currentdir)
                with ZipFile(file_name) as zipObj:
                    zipObj.extractall(currentdir)
                os.remove(file_name)
                total_count = unzip_path(currentdir, total_count)
        
def market_agg(string):
    string = string.lower()
    if 'ind' in string:
        return 'Individual'
    elif 'small' in string or ('s' in string and 'g' in string):
        return 'Small Group'

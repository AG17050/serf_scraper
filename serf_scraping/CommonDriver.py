# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 13:04:07 2021

@author: AG17050
"""

# Importing Libraries
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class CommonDriver(webdriver.Chrome):
    
    def __init__(self):
        
        chromeOptions = Options()
        chromeOptions.add_experimental_option('prefs',  {
            #"download.prompt_for_download": False,
            "download.directory_upgrade": True,
            #"plugins.always_open_pdf_externally": True,
            "plugins.plugins_disabled": ["Chrome PDF Viewer"]
            }
        )
        
        super().__init__(chrome_options=chromeOptions, 
                       desired_capabilities=chromeOptions.to_capabilities())
        
    
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 12:55:44 2021

@author: AG17050
"""
from CommonDriver import CommonDriver, By, WebDriverWait, EC
from abc import ABC, abstractmethod
from typing import List
from file_downloading import SerfFile

class SerfScraper(ABC):
    
    def __init__(self, url: str):
        self.url = url
        self.state = url[url.rfind('/') + 1:]
        self.driver = CommonDriver()
        self.driver.get(url); self.driver.maximize_window()
        self.serfiles = []
        
    def wait_for_and_find(self, tag: str, tag_type="selector", wait_time=15, wait_type='presence'):
        """
        Automatically give time for an element to render and then select it.
        tag_type: ['selector','xpath','link_text']
        wait_type: ['presence','visible']
        
        Parameters
        ----------
        tag : str
            Yhe tag string (css_selector, xpath, ect).
        tag_type : TYPE, optional
            The type of tag (css_select, xpath, ect). The default is "selector".
        wait_time : TYPE, optional
            The number of seconds to wait for element to render. The default is 60.
        Returns
        -------
        TYPE
            The element.
        """
        if tag_type == "selector":
            by = By.CSS_SELECTOR 
        
        elif tag_type == "xpath":
            by = By.XPATH
        
        elif tag_type == "link_text":
            by = By.LINK_TEXT
            
        if wait_type=='presence':
            return WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located((by, tag)))
        if wait_type=='visible':
            return WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located((by, tag)))
    
    @abstractmethod
    def scrape_website(self) -> List[SerfFile]:
        """
        Returns a list of the serf file objects (presumably corresponding to the
        list of files downloaded while scraping the site.)

        Returns
        -------
        List[SerfFile]
            DESCRIPTION.

        """
        pass
    
    @abstractmethod
    def create_serfile(self) -> SerfFile:
        """
        

        Returns
        -------
        SerfFile
            DESCRIPTION.

        """
        pass





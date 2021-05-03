# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 11:21:36 2021

@author: AG17050
"""
import numpy as np
import pandas as pd
from fuzzywuzzy import process#, fuzz
import re

class CarrierMatcher:
    
    def __init__(self, carrier_file_name = 'carrier_matching/Carrier_List.csv'):
        self.carrier_df = pd.read_csv(carrier_file_name)
        self.companies, self.carriers = self.__initial_data_processing()
        
        self.comp_to_carrier_dict = dict(zip(self.companies, self.carriers))
        self.fuzzy_matcher = FuzzyMatcher(self.companies)
        
    @staticmethod
    def __prep_string(string):
        string = re.sub('[,./?\:!@#$%^&*()-]', '', string)
        string = string.replace('_','')
        string = string.replace('\r',' ')
        string = string.upper()
        string = string.rstrip()
        return string
    
    def __initial_data_processing(self):
        carrier = self.carrier_df['Parent']
        carrier = carrier.apply(lambda x: self.__prep_string(x)).tolist()
        
        company = self.carrier_df['Filing Company']
        company = company.apply(lambda x: self.__prep_string(x)).tolist()
        
        return company, carrier
        
    @staticmethod
    def __extract_carrier_from_name(company_name: str):
        name_list = company_name.split()
        carrier = name_list[0]
        return carrier
    
    def match_to_carrier(self, query):
        query = self.__prep_string(query)
        match_dict = self.fuzzy_matcher.get_match(query)
        company = match_dict['match']
        score = match_dict['score']
        if score != -1:
            carrier = self.comp_to_carrier_dict[company]
        else:
            carrier = self.__extract_carrier_from_name(query)
        return carrier
    
    
class FuzzyMatcher():
    
    def __init__(self, choices):
        self.choices = choices
        self.file = open(r"matches.txt","w")
        self.file.write(f'query,match,score')
        
    def get_match(self, query, limit=10):
        
        results = process.extract(query, self.choices, limit=limit)
        best_index = np.argmax([x[1] for x in results])
        best_choice_output = results[best_index]
        
        match = best_choice_output[0]; score = best_choice_output[1]
        if score > 90:
            print('match returned')
            self.file.write(f'{query},{match},{score}')
            return {'match':match,'score':score}
        else:
            return {'match':'','score':-1}
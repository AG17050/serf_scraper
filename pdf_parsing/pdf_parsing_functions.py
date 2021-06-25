# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 10:02:30 2021

@author: AG17050
"""
import PyPDF2

def find_page_text(pdf_reader, text) -> str:
    for i in range(pdf_reader.numPages):
        page_handle = pdf_reader.getPage(i)
        page_text = page_handle.extractText().lower()
        if text in page_text:
            return page_text
    return None
    
def find_string_subtext(page_text, string) -> str:
    idx = page_text.rfind(string)
    subtext = page_text[idx:]
    
    idx = subtext.find('serff tracking')
    subtext = subtext[:idx]
    return subtext
    
def find_effective_date(page_text) -> str:
    idx = page_text.rfind('effective date')
    subtext = page_text[idx:]
    
    idx = subtext.find('serff tracking')
    subtext = subtext[:idx]
    
    strings = ['effective date', 'requested']
    for string in strings:
        subtext = find_string_subtext(page_text, string)
        if '/' not in subtext:
            continue
        else:
            date_idx = subtext.find('/') - 2
            date_str = subtext[date_idx:date_idx + 10]
            return date_str
    return ''

def find_pdf_effective_date(file_path):
    fhandle = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(fhandle)
    page_text = find_page_text(pdf_reader, 'filing at a glance')
    effective_date_str = find_effective_date(page_text)
    fhandle.close()
    return effective_date_str

# for f in os.listdir('pdf_filings'):
#     file = os.path.join('pdf_filings', f)
#     print(find_pdf_effective_date(file))

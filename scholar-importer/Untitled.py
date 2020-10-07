import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

url = "https://scholar.google.com.au/citations?user=KXU4cS8AAAAJ&hl=en&oi=sra"#'https://scholar.google.com.au/citations?user=KxPWaFgAAAAJ&hl=en&oi=ao'
response = requests.get(url)

soup = BeautifulSoup(response.text, “html.parser”)

rows = soup.findAll("td", {"class": "gsc_a_t"})

cols = ['Authors','Year','Title','Journal','Volume','Issue','Pages']
df = pd.DataFrame(np.zeros((len(rows),len(cols))),columns=cols)

r = -1;
for row in rows:
    r = r + 1;
    print("ROW " + str(r))
    authors = ""
    year = ""
    title = ""
    journal = ""
    issue = ""
    volume = ""
    pages = ""
    # segment the HTML
    row = rows[r]
    divs = row.findAll("div") # the first should be the authors, and the second should be the journal & year
    text = divs[1].get_text()
    # get the easy things first
    authors = divs[0].get_text()
    title = row.findAll("a")[0].get_text()
    # remove known bugs
    bugs = ["\u2010","\u2013","\u2014"] # symbol for a long hyphe
    for bug in bugs:
        text = re.sub(bug,"-",text)
        title = re.sub(bug,"-",title)
        authors = re.sub(bug,"-",authors)
    # get the year off the end
    if (len(divs[1].get_text()) > 0):
        year = re.findall(r'\d+', divs[1].findAll("span")[0].get_text())[0]
        text = text[0:len(text)-6] # remove ", [YEAR]"
        # get the text (journal name) up until first number (this might be a problem if journal names have numbers in them...)
        numbers = re.findall('\d+',text)
        if (len(numbers) == 0):
            journal = text
        else:
            journal = text[0:text.find(numbers[0])-1] # find just the letters (ignoring year, volume, issue, etc.)
            while (len(re.findall("[a-zA-Z]",journal[len(journal)-1])) == 0): # if the last character isn't a letter, delete it
                journal = journal[0:len(journal)-1]
            text = text[text.find(numbers[0]):len(text)] # remove journal name
            # check if there is an issue number (in parentheses)
            if (len(re.findall('[()]',text)) > 0):
                issue = re.findall('^.*?\([^\d]*(\d+)[^\d]*\).*$',text)[0]
                text = re.sub("".join(["\(",issue,"\)"]),"",text)
            # split by comma
            text = text.split(",")
            for i in range(0,len(text)):
                text[i] = re.sub(" ","",text[i])
                if (len(re.findall("http",text[i])) > 0):
                    text.pop(i)
            if (len(text) == 2):
                volume = text[0]
                pages = text[1]
            else:
                if (len(re.findall('-',text[0])) == 0):
                    volume = text[0] # note that this still could be the page number!
                else:
                    pages = "".join(re.findall('[-\d]',text[0]))
    df.Authors.iloc[r] = authors
    df.Year.iloc[r] = year
    df.Title.iloc[r] = title
    df.Journal.iloc[r] = journal
    df.Volume.iloc[r] = volume
    df.Issue.iloc[r] = issue
    df.Pages.iloc[r] = pages

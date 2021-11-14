'''
At the time of writing this code I'm learning BeautifulSoup, so a lot of comments are just to help me understand what bs4 functions are doing.
'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

def scrape_first_table(url,
                       headers_limit=2, 
                       headers_index=0, 
                       row_start=1, 
                       headers_start=0):
    '''
    Takes in a url string and soup slicing parameters, returns a df of the first table on the page.
    '''
    soup = url_to_soup(url)
    headers = get_table_headers(soup, headers_limit, headers_index)
    rows_data = get_row_data(soup, row_start)
    
    return pd.DataFrame(rows_data, columns = headers[headers_start:])

def scrape_mvp_vote_results_by_year(years):
    '''Takes in an iterable of years as ints, returns a pandas df of MVP voting results for the year ending in the given year.
    E.g: passing range(2020,2017,-1) returns results from 2020 descending to 2018
    
    Args:
        years ([int]):list of years
    
    Returns:
        pandas.Dataframe : dataframe of voting results
    '''
    df = pd.DataFrame()
    for year in years:
        t0 = time.time() #crawl delay initializer
        
        url = f'https://www.basketball-reference.com/awards/awards_{year}.html#mvp'        
        html = urlopen(url)
        soup = BeautifulSoup(html, 'lxml')

        season = get_seasons(soup.find('h1').getText())[0]
        headers = get_table_headers(soup, 2, 1)
        headers[0] = 'Season'

        rows = soup.findAll('tr')[2:]
        rows_data = [
                    [td.getText() for td in row.findAll('td')] 
                    for row in rows
                    ]

        rows_data = remove_results_after_first_table(rows_data)
        
        for row in rows_data:
            row.insert(0, season)

        df = df.append(pd.DataFrame(rows_data, columns = headers), ignore_index=True)

        time.sleep(3-(t0-time.time())) #BR requests a crawl-delay of 3 seconds

    return df

def scrape_team_index_pages(teams):
    '''
    Takes in an iterable of 3 letter team initials (e.g 'GSW') and returns a dataframe of the season results of those teams together in a single dataframe.
    
    Args:
        teams ([str])
        
    Returns:
        pandas.Dataframe: dataframe of season results for each teams season
    '''
    
    df = pd.DataFrame()
    
    for i,team in enumerate(teams):
        t0 = time.time() #crawl delay initializer
        
        url = f'https://www.basketball-reference.com/teams/{team}/'

        soup = url_to_soup(url)
        headers = get_table_headers(soup, 2, 0)
        rows_data = get_row_data(soup,1)
        seasons = [
                    row.find('th').getText() 
                    for row in soup.findAll('tr')[1:] 
                    ]

        for season,row in zip(seasons,rows_data):
            row.insert(0,season)
            
        for i,row in enumerate(rows_data):
            if row[0] == '1980-81':
                rows_data = rows_data[:i+1]
                break
                
        df_team = pd.DataFrame(rows_data, columns = headers)
        df_team.Team = team
        
        df = df.append(df_team, ignore_index=True)
        
        if len(teams)-(i+1):
            time.sleep(3-(t0-time.time()))
        
    return df

def test_print():
    ''' Test to make sure imports are working correctly'''
    print(1)

def url_to_soup(url):
    '''
    Takes in a URL string and returns a bs4 object
    '''
    html = urlopen(url)
    return BeautifulSoup(html, 'lxml')
    
def get_row_data(soup, start):
    '''
    Takes a bs4 object and a start index and returns a list of lists representing the table data
    
    
    '''    
    rows = soup.findAll('tr')[start:]
    rows_data = [
                [td.getText() for td in row.findAll('td')] 
                for row in rows
                ]
    
    return rows_data
    
def get_seasons(corpus):
    '''
    Takes a text corpus, returns a list of seasons found in the form yyyy-yy
    '''
    
    return re.findall(r'\d+-\d+', corpus)

def get_table_headers(soup, limit, index):
    '''
    Takes in a soup object, limit, and index
    
    Args:
        soup (bs4 object): soup object 
        limit (int): how many objects to find and return
        index (int): index of the header row among the 'tr' HTML objects, usually 0 or 1
        
    Returns:
        headers : list of strings which represent column labels
    '''
    headers = [
               header.getText() 
               for header in soup.findAll('tr', limit=limit)[index].findAll('th')
               ]
    return headers

def remove_results_after_first_table(row_data):
    for i,col in enumerate(row_data):
        if col:
            pass
        else:
            filtered_rows = row_data[:i]
            break
    
    return filtered_rows

def main():
    '''
    Scrapes relevant external data from the web to the external folder
    '''
    df_votes = scrape_mvp_vote_results_by_year(range(2020,1980,-1))
    #need to create folder in script data/raw
    #df_votes.to_csv('../data/raw/mvp-votes-2020-1981',index=False)
    
if __name__ == '__main__':

    main()
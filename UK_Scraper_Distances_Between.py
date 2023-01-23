from bs4 import BeautifulSoup, SoupStrainer
import requests
from selenium import webdriver
from datetime import date, datetime
from datetime import timedelta

from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count

import pandas as pd
import numpy as np

import re

import tqdm

begin_time = datetime.now()

options = webdriver.ChromeOptions()
options.add_argument('--headless')

driver = webdriver.Chrome('C:/Users/leish/Downloads/chromedriver_win32/chromedriver.exe', chrome_options=options)

month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10,
              'Nov': 11, 'Dec': 12}

race_id = 0

base_url = "https://www.racingpost.com"

def get_HTML_content(URL):
    html_content = requests.get(URL,headers={"User-Agent":"Mozilla/5.0"}).text
    return BeautifulSoup(html_content, 'html.parser')

def scrape(url,df):
    soup = get_HTML_content(url)
    if len(url.split("/")) < 6 or url == None:
        return df
    else:
        return get_distances(soup,df)

def get_all_URLs():
    df = pd.read_csv("linksArray.csv")

    df['link'] = [d.split(",") if isinstance(d, str) else [""] for d in df['link']]

    print(np.concatenate(df['link'].values).shape)

    df =  pd.DataFrame(columns=["link"], data=np.concatenate(df['link'].values))

    urls = df.to_numpy().flatten()
    a,c = np.unique(urls,return_index=True)
    b=urls[np.sort(c)]
    urls = b.tolist()

    return [base_url + d for d in urls]

def get_distances(html,df):
    try:
        length = html.findAll('span', class_="rp-horseTable__pos__length")
        length = [l.text.strip().split('\n')[-1].strip("[]").replace("½",".5").replace("¾",".75").replace("¼",".25").replace("-","") for l in length]
        length = [re.sub("[a-z]*",'',l) for l in length]
        length = [float(l) if l != '' else 0 for l in length ]
    except (AttributeError, IndexError):
        length = [None]

    try:
        if [a for a in html.find('link',{'rel':'canonical'})['href'].split("/")] == None:
            race_id = None
        else:
            race_id = [a for a in html.find('link',{'rel':'canonical'})['href'].split("/")][7]
            race_id = int(race_id)
    except Exception:
        race_id = [None]

    """try:
        race_info = html.findAll('span',class_='rp-raceInfo__value')
        race_info = race_info.text
        print(race_info)
    except Exception as e:
        print(e)
        race_info = None"""

    try:
        pedigree = html.findAll('tr', class_="rp-horseTable__pedigreeRow")
        male_pedigrees = []
        female_pedigrees = []
        older_pedigrees = []
        bs = []
        for idx,ped in enumerate(pedigree):
            a = ped.find('td')
            b = a.text.strip().replace("\n","")[:4].strip()
            pedigree_id = a.findAll('a', class_="ui-profileLink ui-link ui-link_table js-popupLink")
            pedigree_id = [id['href'].split('/')[3] for id in pedigree_id]
            while len(pedigree_id) < 3:
                pedigree_id.append(None)
            male_pedigrees.append(pedigree_id[0])
            female_pedigrees.append(pedigree_id[1])
            older_pedigrees.append(pedigree_id[2])
            bs.append(b)

    except Exception as E:
        print(E)
        pedigree_ids = [None]
    if race_id == 497988:
        print("go")
    #print(race_id)
    try:
        if len(df.loc[(race_id,slice(None))]) >= 1:
            try:
                df.loc[(race_id,slice(None)), 'length'],df.loc[(race_id, slice(None)), 'pedigree_info'],\
                df.loc[(race_id, slice(None)), 'male_pedigree'],df.loc[(race_id, slice(None)), 'female_pedigree'],\
                df.loc[(race_id, slice(None)), 'older_pedigree']  = [length,bs,male_pedigrees,female_pedigrees,older_pedigrees]
            except Exception as e:
                # 501342
                difference = len(length) - len(df.loc[(race_id,slice(None))])
                df.loc[(race_id, slice(None)), 'length'], df.loc[(race_id, slice(None)), 'pedigree_info'], \
                df.loc[(race_id, slice(None)), 'male_pedigree'], df.loc[(race_id, slice(None)), 'female_pedigree'], \
                df.loc[(race_id, slice(None)), 'older_pedigree'] = [length[:-difference], bs[:-difference], male_pedigrees[:-difference],
                                                                    female_pedigrees[:-difference],
                                                                    older_pedigrees[:-difference]
                                                                    ]
        #print(df.loc[(race_id, slice(None))])
    except:
        pass
    return df
    """        print([length,bs,male_pedigrees,female_pedigrees,older_pedigrees])
        print("Broken")
        print(race_id)
        print(idx)
        print(e)"""


def remove_trailing_values(df,nrows):
    last_value = df.iloc[:nrows].index[-1][0] # Get index of race_id from last value of dataframe
    number_of_trails = len(df.loc[(last_value,slice(None))])
    return number_of_trails

def return_Non_Null_Df(df,index):
    # Create dataframe to save that has all values computed with no NaN
    #last_value = df.iloc[:index].index[-1:][0]   Get index of race_id from last value of dataframe
    na_free = df.dropna(how='any')
    only_na = df[~df.index.isin(na_free.index)]
    return na_free, only_na




if __name__ == "__main__":
    urls = get_all_URLs()

    NROWS = 10000
    skip_rows = 0

    full_df = pd.read_csv(r"C:\Users\leish\Projects\Python\HorsebettingTipsterML\full_data.csv")
    column_names = full_df.columns
    full_df = full_df.set_index(['race_id','horse_ids'])
    all_ids = full_df.index
    test_df = pd.read_csv(r"C:\Users\leish\Projects\Python\HorsebettingTipsterML\runners_UK2.csv")
    print(test_df.loc[test_df.race_id == 501342])
    print(full_df.loc[(501342,slice(None))])
    print(column_names)


    df = pd.DataFrame(columns=["length","pedigree_info","male_pedigree","female_pedigree","older_pedigree"], index=all_ids)

    try:
        aquired_values = pd.read_csv(r"C:\Users\leish\Projects\Python\HorsebettingTipsterML\full_data4.csv")
        print("2")
        aquired_values.reset_index(inplace=True)
        print(list(aquired_values.columns)[:2])
        aquired_values.set_index(list(aquired_values.columns)[:2],inplace=True)
        df.loc[aquired_values.index,:] = aquired_values[:]
        na_free, df = return_Non_Null_Df(df,0)
        print("yes")
        #df = df.loc[aquired_values.index]
    except Exception as e:
        print(e)
        #pd.DataFrame(columns=["length","pedigree_info","male_pedigree","female_pedigree","older_pedigree"]).to_csv('full_data4.csv')

    number_of_trails = remove_trailing_values(df, NROWS)

    num_races = len(df.index.unique(level='race_id'))
    skip_rows = NROWS - number_of_trails

    print(len(urls[len(na_free.index.unique(level='race_id'))-1:]))
    for i,url in enumerate(urls[len(na_free.index.unique(level='race_id'))-1:]):
        df = scrape(url,df)
        if (i % (NROWS-number_of_trails) == 0 and i != 0):
            if isinstance(df,np.ndarray):
                print("break")
            print(df.head)
            na_free_df , only_na = return_Non_Null_Df(df , 0)
            print(len(na_free_df),len(only_na))
            na_free_df.to_csv('full_data4.csv',mode='a',header=False)
            df = only_na
            #full_df = pd.read_csv(r"C:\Users\leish\Projects\Python\HorsebettingTipsterML\full_data.csv", nrows=NROWS,skiprows=skip_rows,names=column_names)
            #full_df = full_df.set_index(['race_id', 'horse_ids'])
            #all_ids = full_df.index

            #df = pd.DataFrame(columns=["length", "pedigree_info", "male_pedigree", "female_pedigree", "older_pedigree"],
                              #index=all_ids)
            number_of_trails = remove_trailing_values(df,NROWS)

            #skip_rows = skip_rows + NROWS - number_of_trails

            num_races = len(df.index.unique('race_id'))

    na_free_df, only_na = return_Non_Null_Df(df, 0)
    print(len(na_free_df), len(only_na))
    na_free_df.to_csv('full_data4.csv', mode='a', header=False)

    print(datetime.now() - begin_time)
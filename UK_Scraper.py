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

import tqdm

begin_time = datetime.now()

options = webdriver.ChromeOptions()
options.add_argument('--headless')

driver = webdriver.Chrome('C:/Users/leish/Downloads/chromedriver_win32/chromedriver.exe', chrome_options=options)

month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10,
              'Nov': 11, 'Dec': 12}

race_id = 0

base_url = "https://www.racingpost.com"


def convertDistanceToYards(dist):
    total_yardage = 0
    if "m" in dist:
        total_yardage += int(dist[0]) * 1760
        if "½" in dist and dist[2] == "½":
            total_yardage += 110
        elif "f" in dist:
            total_yardage += int(dist[2]) * 220
            if dist[3] == "½":
                total_yardage += 110
    else:
        total_yardage += int(dist[0]) * 220
        if "½" in dist:
            total_yardage += 110
    if total_yardage == 0:
        print("Break")
        print(dist)
    return total_yardage


def convertWeightToPounds(wgt):
    wgt = wgt.split("-")
    return int(wgt[0]) * 14 + int(wgt[1])


def convertFractionalOddsToDecimalOdds(odd):
    odd = odd.split('/')
    try:
        return 1 + int(odd[0]) / int(odd[1])
    except ValueError:
        return None


def replaceAll(rep, txt):
    for r in ((rep[0], ""), (rep[1], ""), (rep[2], "1/1"), (rep[3], "")):
        txt = txt.replace(*r)
    return txt

runner_race_id = 0

def get_race_info(html):
    # Must start with ID
    #track_id = url.split('/')[0]
    try:
        track_name = html.find('a', class_ = "js-popupLink ui-link ui-link_table ui-link_marked rp-raceTimeCourseName__name").text.strip()
        track_id = html.find('a', class_ = "js-popupLink ui-link ui-link_table ui-link_marked rp-raceTimeCourseName__name")['href'].split("/")[3]
        race_id = [a for a in html.find('link', {'rel': 'canonical'})['href'].split("/")][7]
    except (AttributeError, IndexError, TypeError):
        track_name = None
        race_id = None
        track_id = None
    try:
        race_class = html.find('span', class_="rp-raceTimeCourseName_class").text.strip()
    except AttributeError:
        race_class = None
    try:
        distance = convertDistanceToYards(html.find('span', class_="rp-raceTimeCourseName_distance").text.strip())
    except AttributeError:
        distance = None
        print("False")
    try:
        going = html.find('span', class_="rp-raceTimeCourseName_condition").text.strip()
    except AttributeError:
        going = None
    try:
        date = html.find('span', class_="rp-raceTimeCourseName__date").text.strip()
    except AttributeError:
        date = None

    try:
        race_title = html.find('h2', class_="rp-raceTimeCourseName__title").text
        if "Chase" in race_title:
            race_type = "Chase"
        elif "Hurdle" in race_title:
            race_type = "Hurdle"
        else:
            race_type = "Flat"
        if "Handicap" in race_title:
            race_handicap = True
        else:
            race_handicap = False
        if "Grade" in race_title:
            race_class = "(Class 1)"
    except AttributeError:
        race_title = None
        race_type = None
        race_handicap = None

    try:
        race_band_age = html.find('span', class_="rp-raceTimeCourseName_ratingBandAndAgesAllowed").text.strip()
        race_band_age = race_band_age.split(',')[-1].replace(')','').replace('(','')
    except Exception:
        race_band_age = None

    d = {'race_id':race_id,
         #'race_title':race_title,
         'track_name':track_name,'track_id':track_id,
         'race_class':race_class,'distance':distance,
         'going':going,
         'race_age':race_band_age,
         'race_handicap': race_handicap,
         'race_type':race_type,
         'date':date}
    df = pd.DataFrame.from_dict(data=d,orient='index')
    df = df.transpose()
    return df

def get_runner_info(html):
    try:
        if [a for a in html.find('link',{'rel':'canonical'})['href'].split("/")] == None:
            race_id = None
        else:
            race_id = [a for a in html.find('link',{'rel':'canonical'})['href'].split("/")][7]
    except Exception:
        race_id = None

    try:
        horse_names = html.findAll('a', class_="rp-horseTable__horse__name ui-link ui-link_table js-popupLink")
        horse_names = [name.text.strip() for name in horse_names]
    except (AttributeError, IndexError):
        horse_names = [None]

    try:
        horse_ids = html.findAll('a', class_="rp-horseTable__horse__name ui-link ui-link_table js-popupLink")
        horse_ids = [id['href'].split('/')[3] for id in horse_ids]
    except (AttributeError, IndexError):
        horse_ids = [None]

    """try:
        horse_urls = html.findAll('a', class_="rp-horseTable__horse__name ui-link ui-link_table js-popupLink")
        horse_urls = [id['href'] for id in horse_urls]
    except AttributeError:
        horse_urls = [None]"""

    try:
        jockey_ids = html.findAll('a',
                                  class_="rp-horseTable__human__link ui-link ui-link_table ui-profileLink js-popupLink")
        jockey_ids = [id['href'].split('/')[3] for id in jockey_ids if "jockey" in id['href']]
    except (AttributeError, IndexError, TypeError):
        jockey_ids = [None]

    """try:
        jockey_urls = html.findAll('a',
                                   class_="rp-horseTable__human__link ui-link ui-link_table ui-profileLink js-popupLink")
        jockey_urls = [id['href'] for id in jockey_urls if "jockey" in id['href']]
    except (AttributeError, IndexError, TypeError):
        jockey_urls = [None]"""

    try:
        trainer_ids = html.findAll('a',
                                   class_="rp-horseTable__human__link ui-link ui-link_table ui-profileLink js-popupLink")
        trainer_ids = [id['href'].split('/')[3] for id in trainer_ids if "trainer" in id['href']]
        trainer_ids = list(dict.fromkeys(trainer_ids))
    except (AttributeError, IndexError):
        trainer_ids = [None]

    """try:
        trainer_urls = html.findAll('a',
                                    class_="rp-horseTable__human__link ui-link ui-link_table ui-profileLink js-popupLink")
        trainer_urls = [id['href'] for id in trainer_urls if "trainer" in id['href']]
        trainer_urls = list(dict.fromkeys(trainer_urls))
    except (AttributeError, IndexError):
        trainer_urls = [None]"""

    """days_since_last_race = []
    horse_win_percents = []
    mean_speed_figures = []
    last_figures = []
    best_figures_dist = []
    best_figures_going = []"""
    try:
        draws = html.findAll('sup', class_='rp-horseTable__pos__draw')
        draws = [draw.text.strip() for draw in draws]
        if draws == []:
            draws = [x for x in range(len(horse_ids))]
        else:
            draws = [draw.replace("(", "") for draw in draws]
            draws = [draw.replace(")", "") for draw in draws]
    except (AttributeError, IndexError, TypeError):
        draws = [None]

    """for idx, url in enumerate(horse_urls):
        get_horse_info(url)
        race_dates = get_race_dates()
        all_figures = get_all_figures(current_date, race_dates)

        horse_win_percents.append(get_win_percent(current_date, race_dates))
        days_since_last_race.append(get_days_since_last_race(current_date, race_dates))
        mean_speed_figures.append(get_mean_speed_figures(current_date, race_dates, all_figures))
        last_figures.append(get_last_figure(current_date, race_dates, all_figures))
        best_figures_dist.append(get_best_dist_figure(current_date, race_dates, distance, all_figures))
        best_figures_going.append(get_best_going_figure(current_date, race_dates, going, all_figures))

    jockey_win_percent = []
    for url in jockey_urls:
        get_jockey_info(url)
        race_dates = get_race_dates()
        jockey_win_percent.append(get_win_percent(current_date, race_dates))

    trainer_win_percent = []
    for url in trainer_urls:
        get_trainer_info(url)
        race_dates = get_race_dates()
        trainer_win_percent.append(get_win_percent(current_date, race_dates))"""

    try:
        horse_ages = html.findAll('td', class_="rp-horseTable__spanNarrow rp-horseTable__spanNarrow_age")
        horse_ages = [age.text.strip() for age in horse_ages]
    except (AttributeError, IndexError):
        horse_ages = [None]

    try:
        horse_weight = html.findAll('td', class_="rp-horseTable__spanNarrow rp-horseTable__wgt")
        horse_weight = [
            str(weight.find('span', class_='rp-horseTable__st').text) + "-" + str(weight.findAll('span')[1].text)
            for weight in horse_weight]
        horse_weight = [convertWeightToPounds(weight.strip()) for weight in horse_weight]
    except (AttributeError, IndexError):
        horse_weight = [None]

    try:
        top_speeds = html.findAll('td', class_="rp-horseTable__spanNarrow", attrs={'data-ending': "TS"})
        top_speeds = [speed.text.strip() for speed in top_speeds]
    except (AttributeError, IndexError):
        top_speeds = [None]

    try:
        ratings = html.findAll('td', class_="rp-horseTable__spanNarrow", attrs={'data-ending': "RPR"})
        ratings = [rating.text.strip() for rating in ratings]
    except (AttributeError, IndexError):
        ratings = [None]

    try:
        official_ratings = html.findAll('td', class_="rp-horseTable__spanNarrow", attrs={'data-ending': "OR"})
        official_ratings = [official_rating.text.strip() for official_rating in official_ratings]
    except (AttributeError, IndexError):
        official_ratings = [None]

    try:
        odds = html.findAll('span', class_="rp-horseTable__horse__price")
        odds = [convertFractionalOddsToDecimalOdds(replaceAll(['F', 'C', "Evens","J"], odd.text.strip())) for odd in odds]
    except (AttributeError , IndexError):
        odds = [None]

    try:
        places = html.findAll('span', class_="rp-horseTable__pos__number rp-horseTable__pos__number_noDraw")
        places = [place.text.strip() for place in places]
        if places == []:
            places = html.findAll('span', class_="rp-horseTable__pos__number")
            places = [place.text.strip()[0:place.text.strip().find("(")] for place in places]
    except (AttributeError, IndexError):
        places = [None]

    """d = {'race_id':[id for i in range(len(horse_ids))], 'horse_ids' :horse_ids,'horse_names': horse_names, 'draws' : draws, 'horse_ages': horse_ages, 'horse_weight':horse_weight, 'horse_win_percents':horse_win_percents,'jockey_ids': jockey_ids,'jockey_win_percent': jockey_win_percent,
         'trainer_ids':trainer_ids, 'trainer_win_percent':trainer_win_percent, 'days_since_last_race':days_since_last_race, 'mean_speed_figures':mean_speed_figures, 'last_figures':last_figures,
         'best_figures_dist':best_figures_dist, 'best_figures_going':best_figures_going, 'top_speeds':top_speeds, 'ratings':ratings, 'odds':odds, 'places':places}"""

    d = {'race_id': [race_id for i in range(len(horse_ids))], 'horse_ids': horse_ids, 'horse_names': horse_names,
         'draws': draws, 'horse_ages': horse_ages, 'horse_weight': horse_weight, 'jockey_ids': jockey_ids,
         'trainer_ids': trainer_ids, 'top_speeds': top_speeds,
         'ratings': ratings, 'official_ratings': official_ratings, 'odds': odds, 'places': places}
    df = pd.DataFrame.from_dict(data=d, orient='index')
    df = df.transpose()
    return df

def get_draws(html):
    try:
        race_id = [a for a in html.find('link', {'rel': 'canonical'})['href'].split("/")][7]
    except (AttributeError, IndexError, TypeError):
        race_id = None
    try:
        horse_ids = html.findAll('a', class_="rp-horseTable__horse__name ui-link ui-link_table js-popupLink")
        horse_ids = [id['href'].split('/')[3] for id in horse_ids]
    except (AttributeError, IndexError):
        horse_ids = [None]

    try:
        draws = html.findAll('sup', class_='rp-horseTable__pos__draw')
        draws = [draw.text.strip() for draw in draws]
        if draws == []:
            draws = [x for x in range(len(horse_ids))]
        else:
            draws = [draw.replace("(","") for draw in draws]
            draws = [draw.replace(")", "") for draw in draws]
    except (AttributeError, IndexError):
        draws = [None]
    d = {'race_id': [race_id for i in range(len(horse_ids))], 'horse_ids': horse_ids,
         'draws': draws}
    df = pd.DataFrame.from_dict(data=d, orient='index')
    df = df.transpose()
    return df

def get_trainer_info(trainer_id):
    # return get_HTML_content("https://www.racingpost.com" + trainer_id)
    get_HTML_content_selenium("https://www.racingpost.com" + trainer_id)


def get_jockey_info(jockey_id):
    # return get_HTML_content("https://www.racingpost.com" + jockey_id)
    get_HTML_content_selenium("https://www.racingpost.com" + jockey_id)


def get_horse_info(horse_id):
    # return get_HTML_content("https://www.racingpost.com" + horse_id +"/form")
    get_HTML_content_selenium("https://www.racingpost.com" + horse_id)


def get_win_percent(current_date, race_dates):
    total = 0
    wins = 0
    idx = 0
    if race_dates == []:
        return 0
    for tr in driver.find_elements_by_xpath("/html/body/main/div/section[2]/section[2]/div[2]/table/tbody/tr"):
        row = tr.find_elements_by_tag_name('td')
        try:
            if race_dates[idx] < current_date and len(row) > 2:
                if row[2].text[0] == "1" and row[2].text[1] == "/":
                    wins += 1
                total += 1
            if (len(row) < 4):
                idx -= 1
            else:
                idx += 1
        except IndexError:
            pass

    try:
        return wins / total
    except ZeroDivisionError:
        return 0

def get_days_since_last_race(current_date, race_dates):
    for idx, race_date in enumerate(race_dates):
        if race_date < current_date:
            return (current_date - race_date).days

def get_race_dates():
    race_dates = driver.find_elements_by_class_name("hp-formTable__dateWrapper")
    race_dates = [race_date.text.split('\n')[-1] for race_date in race_dates]
    race_dates = [["20" + race_date[-2:], race_date[2:5], race_date[0:2]] for race_date in race_dates]

    for i in range(len(race_dates)):
        for key in month_dict.keys():
            race_dates[i][1] = race_dates[i][1].replace(key, str(month_dict[key]))
    if race_dates == []:
        print("Stop")
    return [date(int(race_date[0]), int(race_date[1]), int(race_date[2])) for race_date in race_dates]

def get_mean_speed_figures(current_date, race_dates, speed_figures):
    sum = 0
    if 5 < len(speed_figures):
        for i in range(len(speed_figures[0:5])):
            sum += speed_figures[0:5][i][0]
        return sum / 5
    else:
        for i in range(len(speed_figures[0:])):
            sum += speed_figures[0:][i][0]
        return sum / (len(speed_figures[0:]) + 1)

def get_last_figure(current_date, race_dates, speed_figures):
    try:
        return speed_figures[0][0]
    except IndexError:
        return 0

def get_best_dist_figure(current_date, race_dates, dist, speed_figures):
    max = 0
    for idx, speed_figure in enumerate(speed_figures):
        if speed_figure[1] == dist:
            if speed_figure[0] > max:
                max = speed_figure[0]
    return max

def get_best_going_figure(current_date, race_dates, going, speed_figures):
    max = 0
    for idx, speed_figure in enumerate(speed_figures):
        if speed_figure[1] == going:
            if speed_figure[0] > max:
                max = speed_figure[0]
    return max

def get_all_figures(current_date, race_dates):
    speed_figures = []
    idx = 0
    if race_dates == []:
        return []
    for tr in driver.find_elements_by_xpath("/html/body/main/div/section[2]/section[2]/div[2]/table/tbody"):
        row = tr.find_elements_by_tag_name('td')
        if race_dates[idx] < current_date and len(row) == 12:
            try:
                speed_figures.append([int(row[9].text), convertDistanceToYards(row[2].text), row[3].text, row[4].text])
            except ValueError:
                speed_figures.append([0, convertDistanceToYards(row[2].text), row[3].text, row[4].text])
        if len(row) < 12:
            idx -= 1
        else:
            idx += 1
    """for idx,race_date in enumerate(race_dates):
        if race_date < current_date and int(all_figures[idx][9].text) > 0:
            # [Speed Rating, Distance, Going]
            speed_figures.append([int(all_figures[idx][9]), convertDistanceToYards(all_figures[idx][2]), all_figures[idx][3], all_figures[idx][4]])"""
    return speed_figures

def generate_URLS(start_date, end_date):
    dates = [(start_date + timedelta(x)).isoformat() for x in range((end_date - start_date).days + 1)]
    base_URL = "https://www.racingpost.com/results/"

    races = pd.DataFrame(columns=['track_id', 'race_class', 'distance', 'going', 'date'])
    runs = pd.DataFrame(columns=['horse_ids' ,'horse_names', 'draws' , 'horse_ages', 'horse_weight', 'horse_win_percents','jockey_ids','jockey_win_percent',
         'trainer_ids', 'trainer_win_percent', 'days_since_last_race', 'mean_speed_figures', 'last_figures',
         'best_figures_dist', 'best_figures_going', 'top_speeds', 'ratings', 'odds', 'places'],index=[])
    urls = []
    race_id = 0
    """for date in dates:
        links = get_all_result_index(base_URL + date)
        print(links)
        for link in links:
            urls.append(base_URL + link)
            html = get_HTML_content(base_URL + link)
            race_info, race_id = get_race_info(race_id,link, html)
            races = races.append(race_info)
            runner_info, race_id = get_runner_info(race_id,html)
            runs = runs.append(runner_info)
        print(date)
    races.to_csv(r"..\HorsebettingTipsterML\races_UK2.csv")
    runs.to_csv(r"..\HorsebettingTipsterML\runners_UK2.csv")"""

    for date in dates:
        links = get_all_result_index(base_URL + date)
        print(links)
        for link in links:
            urls.append(base_URL + link)
    print(urls)


def get_all_result_index(URL):
    soup = get_HTML_content(URL)
    links = soup.findAll('a', class_="rp-raceCourse__panel__race__info__buttons__link js-popupLink")
    return [link['href'].split('/', 2)[2] for link in links]


def get_HTML_content(URL):
    html_content = requests.get(URL,headers={"User-Agent":"Mozilla/5.0"}).text
    return BeautifulSoup(html_content, 'html.parser')

def get_HTML_content_by_class(URL, className):
    parse_only = SoupStrainer("div", class_="rp-raceCourse ui-accordion ng-isolate-scope")
    return BeautifulSoup()


def get_HTML_content_selenium(URL):
    driver.get(URL)

def get_all_URLs():
    df = pd.read_csv("linksArray.csv")

    df['link'] = [d.split(",") if isinstance(d, str) else [""] for d in df['link']]

    print(np.concatenate(df['link'].values).shape)

    df =  pd.DataFrame(columns=["link"], data=np.concatenate(df['link'].values))

    urls = df.to_numpy().flatten().tolist()

    return [base_url + d for d in urls]

#generate_URLS(date(2010, 1 , 1), date(2021, 4, 20))

def scrape(url):
    soup = get_HTML_content(url)
    if len(url.split("/")) < 6 or url == None:
        return pd.DataFrame(),pd.DataFrame()
    else:
        return get_race_info(soup), get_runner_info(soup)

def scrape_draws(url):
    soup = get_HTML_content(url)
    if len(url.split("/")) < 6 or url == None:
        return pd.DataFrame()
    else:
        return get_draws(soup)

if __name__ == "__main__":
    urls = get_all_URLs()
    urls = urls[220000:230000]

    races = pd.DataFrame(columns=['race_id','track_name', 'track_id','race_class', 'distance', 'going','race_age',
         'race_handicap','race_type', 'date'])
    runs = pd.DataFrame(
        columns=['race_id','horse_ids', 'horse_names', 'draws', 'horse_ages', 'horse_weight', 'horse_win_percents', 'jockey_ids',
                 'jockey_win_percent',
                 'trainer_ids', 'trainer_win_percent', 'days_since_last_race', 'mean_speed_figures', 'last_figures',
                 'best_figures_dist', 'best_figures_going', 'top_speeds', 'ratings','official_ratings', 'odds', 'places'])
    races = races.set_index(keys=races['race_id'])
    runs = runs.set_index(keys=runs['race_id'])
    """p = Pool(4)
    race_results, runner_results = p.map(scrape, urls)
    p.terminate()
    p.join()"""

    with Pool(processes=10) as pool, tqdm.tqdm(total=len(urls)) as pbar:
        races = pd.DataFrame(columns=['race_id', 'track_name', 'track_id', 'race_class', 'distance', 'going','race_age',
         'race_handicap','race_type', 'date'])
        runs = pd.DataFrame(
            columns=['race_id', 'horse_ids', 'horse_names', 'draws', 'horse_ages', 'horse_weight', 'horse_win_percents',
                     'jockey_ids',
                     'jockey_win_percent',
                     'trainer_ids', 'trainer_win_percent', 'days_since_last_race', 'mean_speed_figures', 'last_figures',
                     'best_figures_dist', 'best_figures_going', 'top_speeds', 'ratings','official_ratings', 'odds', 'places'])
        for race, run in pool.imap_unordered(scrape,urls):
            races = races.append(race)
            runs = runs.append(run)
            pbar.update()
            """print(kyraces.to_string())
            print(runs.to_string())"""
        """for draw in pool.imap_unordered(scrape_draws,urls):
            draws = draws.append(draw)
            pbar.update()"""
        pool.terminate()
        pool.join()

    print(races.to_string)
    print(runs.to_string)
    """draws.to_csv(r"..\HorsebettingTipsterML\draws.csv")"""

    old_races = pd.read_csv(r"races_UK2.csv")
    old_runs = pd.read_csv(r"runners_UK2.csv")

    old_races = old_races.drop(old_races.columns[:1],axis=1)
    old_runs = old_runs.drop(old_runs.columns[:1],axis=1)

    races = old_races.append(races)
    runs = old_runs.append(runs)

    races.to_csv(r"..\HorseBettinModel\races_UK2.csv")
    runs.to_csv(r"..\HorseBettingModel\runners_UK2.csv")

    print(datetime.now() - begin_time)

""" with ThreadPool(cpu_count() * 2) as pool:
        for race, run in pool.map(scrape, urls):
            races = races.append(race)
            runs = runs.append(run)
        pool.terminate()
        pool.join()
        print(races)
        print(runs)"""
"""
    for url in urls:
        race_temp, run_temp = scrape(url)
        races = races.append(race_temp)
        runs = runs.append(run_temp)"""





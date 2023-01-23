import pandas as pd
import numpy as np
import re


from datetime import date

month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
              'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10',
              'Nov': '11', 'Dec': '12'}


def convertStringIntoDate(newDate):
    #print(newDate)
    newDate = [x.strip() for x in newDate.split(" ")]
    newDate[1] = month_dict[newDate[1]]
    newDate[0] = int(newDate[0])
    newDate[1] = int(newDate[1])
    newDate[2] = int(newDate[2])
    return date(newDate[2],newDate[1],newDate[0])

def get_all_horse_races(person):
    values = {}
    # Create list of horses
    ids = df_runs[person].unique().tolist()
    df = df_runs.copy()

    df = df.pivot(index='horse_ids',columns='race_id')
    print(df.head())


    """for id in ids:
        temp = []
        for race_id in df_races.index:
            if id in df_runs.loc[(df_runs['race_id'] == race_id), person].values:
                temp.append(race_id)
        values[id] = temp"""
    """
    for horse_id in ids:
        temp = []
        for race_id in df_races.index:
            if horse_id in df_runs.loc[(df_runs['race_id'] == race_id), person].values:
                temp.append(race_id)
        values.append({person: horse_id,
                       'race_ids': temp})
    """
    return values

def get_days_since_last_race():
    values = get_all_horse_races("horse_ids")
    arr = []
    for idx in range(len(df_runs['race_id'])):
        min = 360
        for val in values:
            if val["horse_ids"] == df_runs.iloc[idx]["horse_ids"]:
                for race in val['race_ids']:
                    if df_races.loc[race, ['date']].values > df_races.loc[
                        df_races.index == df_runs.iloc[idx]['race_id'], ['date']].values:
                        temp = (df_races.loc[df_races.index == df_runs.iloc[idx]['race_id'],
                                           ['date']].values[0][0] -
                                (df_races.loc[race, ['date']].values[0])).days
                        if temp < min:
                            min = temp
        if min == 360:
            arr.append(0)
        else:
            arr.append(min)
    return arr

def get_mean_speed_figures():
    values = get_all_horse_races("horse_ids")
    arr = []
    for idx in range(len(df_runs['race_id'])):
        sum = 0
        total = 0
        for val in values:
            if val["horse_ids"] == df_runs.iloc[idx]["horse_ids"]:
                for race in val['race_ids']:
                    if df_races.loc[race, ['date']].values > df_races.loc[
                        df_races.index == df_runs.iloc[idx]['race_id'], ['date']].values:
                        print(df_runs.loc[(df_runs['race_id'] == race) &
                                           (df_runs['horse_ids'] == val['horse_ids']), ['top_speeds']].values[0][0])
                        sum += int(df_runs.loc[(df_runs['race_id'] == race) &
                                           (df_runs['horse_ids'] == val['horse_ids']), ['top_speeds']].values[0][0])
                        total += 1
        try:
            arr.append(sum/total)
        except ZeroDivisionError:
            arr.append(0)
    return arr

def get_last_figure():
    values = get_all_horse_races("horse_ids")
    arr = []
    for idx in range(len(df_runs['race_id'])):
        min = 360
        last = 0
        for val in values:
            if val["horse_ids"] == df_runs.iloc[idx]["horse_ids"]:
                for race in val['race_ids']:
                    if df_races.loc[race, ['date']].values > df_races.loc[
                        df_races.index == df_runs.iloc[idx]['race_id'], ['date']].values:
                        temp = (df_races.loc[df_races.index == df_runs.iloc[idx]['race_id'],
                                             ['date']].values[0][0] -
                                (df_races.loc[race, ['date']].values[0])).days
                        if temp < min:
                            last = df_runs.loc[(df_runs['race_id'] == race) & (df_runs['horse_ids'] == val['horse_ids']),['top_speeds']]
        if min == 360:
            arr.append(0)
        else:
            arr.append(min)
    return arr

def get_best_figures_dist():
    values = get_all_horse_races("horse_ids")
    arr = []
    for idx in range(len(df_runs['race_id'])):
        max = 0
        for val in values:
            if val["horse_ids"] == df_runs.iloc[idx]["horse_ids"]:
                for race in val['race_ids']:
                    if df_races.loc[race, ['date']].values > df_races.loc[
                        df_races.index == df_runs.iloc[idx]['race_id'], ['date']].values and df_races.loc[race, ['distance']].values == df_races.loc[df_runs.iloc[idx]['race_id'], ['distance']].values:
                        temp = df_runs.loc[df_runs['race_id'] == race, ['top_speeds']]
                        if temp > max:
                            max = temp
        arr.append(max)
    return arr

def get_best_figures_going():
    values = get_all_horse_races("horse_ids")
    arr = []
    for idx in range(len(df_runs['race_id'])):
        max = 0
        for val in values:
            if val["horse_ids"] == df_runs.iloc[idx]["horse_ids"]:
                for race in val['race_ids']:
                    if df_races.loc[race, ['date']].values > df_races.loc[
                        df_races.index == df_runs.iloc[idx]['race_id'], ['date']].values and df_races.loc[
                        race, ['going']].values == df_races.loc[df_runs.iloc[idx]['race_id'], ['going']].values:
                        temp = df_runs.loc[df_runs['race_id'] == race, ['top_speeds']]
                        if temp > max:
                            max = temp
        arr.append(max)
    return arr

def get_win_percent(person):
    values = get_all_horse_races(person)
    arr = []
    # Check each value of the runs df
    for idx in range(len(df_runs['race_id'])):
        sum = 0
        total = 0
        # Get all the races by this horse
        try:
            races_run_by_horse = values[df_runs.iloc[idx][person]]
        except KeyError:
            races_run_by_horse = []
        # Loop through all races run by specific horse
        for race in races_run_by_horse:
            # Check date of old race ran by horse is earlier than race of horse being checked
            if df_races.loc[race, ['date']].values[0] < df_races.loc[
                df_races.index == df_runs.iloc[idx]['race_id'], ['date']].values[0][0] and total < 7:
                # Get specific instance of the run where the race_id is equal to the race_id of the 'race'
                # and where the horse_id is equal to the horse that orginally ran
                if (df_runs.loc[(race == df_runs['race_id']) & (df_runs.iloc[idx][person] == df_runs[person]), ['places']].values[0][0]) == "1":
                    sum += 1
                total += 1
        try:
            arr.append(sum / total)
        except ZeroDivisionError:
            arr.append(0)
    return arr

def add_stats():
    values = get_all_horse_races("horse_ids")
    print("got")
    arr_best_fig_going = []
    arr_best_fig_dist = []
    arr_last_fig = []
    arr_mean_speed_figure = []
    arr_days_since_last_race = []
    weight_diff = []
    for idx in range(len(df_runs['race_id'])):
        print(idx)
        max_fig_going = 0
        max_fig_dist = 0
        min_last_date = 360
        sum_mean_speed_figure = 0
        total = 0
        found = False
        for race in values[df_runs.iloc[idx]["horse_ids"]]:
            if df_races.loc[race, ['date']].values[0] < df_races.loc[
                df_races.index == df_runs.iloc[idx]['race_id'], ['date']].values[0][0] and total < 7:
                if not found:
                    weight_diff.append(df_runs.iloc[idx]['horse_weight'].values[0][0] - df_runs.loc[
                        (df_runs['race_id'] == race) & (df_runs['horse_ids'] == df_runs.iloc[idx]["horse_ids"])])
                    found = True
                if df_races.loc[race, ['going']].values[0][0] == df_races.loc[df_runs.iloc[idx]['race_id'], ['going']].values[0][0]:
                    temp = int(df_runs.loc[(df_runs['race_id'] == race) & (df_runs['horse_ids'] == df_runs.iloc[idx]["horse_ids"]), ['top_speeds']].values[0][0])
                    print(temp)
                    if temp > max_fig_going:
                        max_fig_going = temp
                if df_races.loc[race, ['distance']].values[0] == df_races.loc[
                    df_runs.iloc[idx]['race_id'], ['distance']].values[0]:
                    temp = int(df_runs.loc[(df_runs['race_id'] == race) & (df_runs['horse_ids'] == df_runs.iloc[idx]["horse_ids"]), ['top_speeds']].values[0][0])
                    print(df_runs['horse_ids'])
                    print(df_runs.iloc[idx]["horse_ids"])
                    if temp > max_fig_dist:
                        max_fig_dist = temp

                last_date_temp = ((df_races.loc[df_races.index == df_runs.iloc[idx]['race_id'],
                                     ['date']].values[0][0]) - (df_races.loc[race, ['date']].values[0])).days
                if last_date_temp < min_last_date:
                    latest_fig = df_runs.loc[
                        (df_runs['race_id'] == race) & (df_runs['horse_ids'] == df_runs.iloc[idx]["horse_ids"]), [
                            'top_speeds']].values[0][0]
                    min_last_date = last_date_temp
                sum_mean_speed_figure += int(df_runs.loc[(df_runs['race_id'] == race) &
                                       (df_runs['horse_ids'] == df_runs.iloc[idx]["horse_ids"]), ['top_speeds']].values[0][0])
                total += 1
        arr_best_fig_going.append(max_fig_going)
        arr_best_fig_dist.append(max_fig_dist)
        if min_last_date == 360:
            arr_last_fig.append(0)
            arr_days_since_last_race.append(0)
        else:
            arr_last_fig.append(latest_fig)
            arr_days_since_last_race.append(min_last_date)
        try:
            arr_mean_speed_figure.append(sum_mean_speed_figure/total)
        except ZeroDivisionError:
            arr_mean_speed_figure.append(0)
    return arr_days_since_last_race,arr_mean_speed_figure,arr_last_fig,arr_best_fig_dist,arr_best_fig_going


if __name__ == "__main__":
    df_races = pd.read_csv(r"races_UK2.csv")
    df_runs = pd.read_csv(r"runners_UK2.csv")

    df_races = df_races[df_races['date'].notna()]

    # track_id should be track_name
    df_races.rename(columns={0: 'race_id'})
    df_races = df_races.drop('track_name',axis=1)
    df_races['race_class'] = df_races['race_class'].astype('category').cat.codes
    df_races['going'] = df_races['going'].astype('category').cat.codes
    df_races['race_age'] = df_races['race_age'].astype('category').cat.codes
    df_races['race_type'] = df_races['race_type'].astype('category').cat.codes
    df_races['date'] = df_races['date'].apply(lambda x: convertStringIntoDate(x))

    # encode values for runs DB
    df_runs.replace(u'\xa0',u'', regex=True, inplace=True)
    df_runs = df_runs.drop('horse_names', axis=1)
    df_runs['places'].replace({"F": 0, 'PU': 0, "DSQ":0, 'SU': 0,'BD': 0,'UR': 0,'RO':0,'RR':0,'REF':0,
                               'LFT':0,'CO':0,'VOI':0}, inplace=True)
    """df_runs['places'] = np.where((df_runs.places == "1" or df_runs.places == "2"
                                  or df_runs.places == "3"), 1, 0)"""
    df_runs['won'] = np.where((df_runs.places == "1"), 1, 0)
    df_runs = df_runs.replace('–',0)
    df_runs = df_runs.fillna(0)
    df_runs = df_runs.astype({'race_id': int, 'horse_ids': int,
         'draws': int, 'horse_ages': int, 'horse_weight': int, 'jockey_ids': int,
         'trainer_ids': int, 'top_speeds': int,
         'ratings': int, 'official_ratings': int, 'odds': float, 'places': int})
    df_runs['horse_ages'] = df_runs['horse_ages'].astype('category').cat.codes
    df_runs['horse_weight'] = df_runs['horse_weight']

    # print(horse_ids)
    # Get win percentages
    """#df_runs['true_id'] = (df_runs['race_id'].astype(str) + df_runs['horse_ids'].astype(str)).astype(int)
    #df_runs['true_id'] = df_runs['race_id'].astype(int)
    #df_runs = df_runs.set_index('true_id')

    #df_races = df_races.set_index('race_id')
    """
    df_races = df_races.drop(df_races.columns[:1],axis=1)
    df_runs = df_runs.drop(df_runs.columns[:1],axis=1)

    """df_races = df_races[~df_races.index.duplicated(keep="first")]
    df_runs = df_runs[~df_runs.index.duplicated(keep="first")]"""

    print(df_races.head().to_string())
    print(df_runs.head().to_string())

    print("go")
    days_since_last_race, mean_speed_figure, last_figure, best_fig_dist, best_fig_going = add_stats()

    df_runs['days_since_last_race'] = days_since_last_race
    df_runs['mean_speed_figures'] = mean_speed_figure
    df_runs['last_figures'] = last_figure
    df_runs['best_figures_dist'] = best_fig_dist
    df_runs['best_figures_going'] = best_fig_going

    df_runs['horse_win_percents'] = get_win_percent("horse_ids")
    df_runs['jockey_win_percent'] = get_win_percent("jockey_ids")
    df_runs['trainer_win_percent'] = get_win_percent("trainer_ids")

    df_races.to_csv(r"..\HorsebettingTipsterML\races_UK3.csv")
    df_runs.to_csv(r"..\HorsebettingTipsterML\runners_UK3.csv")






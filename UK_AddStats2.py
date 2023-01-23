import pandas as pd
import numpy as np
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
    #df_runs['true_id'] = df_runs['race_id'] + df_runs['horse_ids']
    df_runs = df_runs.astype({'race_id': int, 'horse_ids': int,
         'draws': int, 'horse_ages': int, 'horse_weight': int, 'jockey_ids': int,
         'trainer_ids': int, 'top_speeds': int,
         'ratings': int, 'official_ratings': int, 'odds': float, 'places': int})
    df_runs['horse_ages'] = df_runs['horse_ages'].astype('category').cat.codes
    df_runs['horse_weight'] = df_runs['horse_weight']

    df_races = df_races.drop(df_races.columns[:1], axis=1)
    df_runs = df_runs.drop(df_runs.columns[:1], axis=1)

    full_data = pd.merge(df_races,df_runs, on='race_id',how='inner')
    print(len(full_data))
    full_data = full_data.set_index(['race_id','horse_ids'])
    full_data = full_data.drop_duplicates()
    print(len(df_runs))
    print(len(df_races))
    print(len(full_data))
    full_data.to_csv(r"..\HorsebettingTipsterML\full_data.csv")
    #print(df_races)
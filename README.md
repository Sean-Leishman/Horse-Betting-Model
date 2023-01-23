# Horse Betting Model

## Instructions
Run scripts in the following order:
1. `python pip install -r requirements.txt` to install dependencies
1. `python UK_Scraper` in order to scrape data from [Racing Post](https://www.racingpost.com). This will generate `races.csv` and `runners.csv` where race details are held and runners details are held respectively. 
2. `python UK_AddStats2` in order to encode values and merge both `races.csv` and `runners.csv` into one file `fullData.csv`.
3. Afterwards run the following Jupyter Notebooks
    1. `data_prep.ipynb` to generate engineered features as listed in `full_data_with_features.csv`
   2. `data_normalization.ipynb` normalizes generated features as listed in `full_data_with_normalized_features.csv`
   3. `data_neural_network.ipynb` trains a neural network for win predictions

## Data 

- Race Description
  - race_id, track_id, race_class, distance, going, race_age, race_handicap, race_type, date
- Horse Detail
  - horse_id
  - draw
  - horse_age
  - horse_weight
  - horse_win_percent
  - days_since_last_race
  - Top Speed Figure 
    - mean_speed_figure, last_figure, best_figures_dist, best_figure_going
  - Rating
    - mean_rating, last_rating, difference_in_rating, best_rating_going, best_rating_dist
  - Official Rating
    - mean_official_rating, last_official_rating, difference_in_official_rating, best_official_rating_going, best_official_rating_dist
  - Win Percents
    - win_percent, win_percent_going, win_percent_dist
  - odds
  - place
  - placed
  - length
  - won
- Sire Detail
  - sire_id
  - sire_win_percent
  - sire_og_win_percent
  - sire_og_going_win_percent
  - sire_og_type_win_percent
  - sire_og_dist_win_percent
- Dam Detail
  - dam_id
  - dam_win_percent
  - dam_og_win_percent
  - dam_og_going_win_percent
  - dam_og_type_win_percent
  - dam_og_dist_win_percent
- Dam Sire Detail
  - dam_sire_id
  - dam_sire_win_percent
- Jockey Detail
  - jockey_id
  - jockey_win_percent
- Trainer Detail
  - trainer_id
  - trainer_win_percent
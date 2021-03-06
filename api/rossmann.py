import pickle
import inflection
import pandas as pd
import numpy as np
import math
import datetime


class Rossmann(object):
    def __init__(self):
        self.competition_distance_scaler = pickle.load(open('../scalers_model/competition_distance_scaler.pkl', 'rb'))
        self.competition_open_since_year_scaler = pickle.load(
            open('../scalers_model/competition_open_since_year_scaler.pkl', 'rb'))
        self.competition_time_month_scaler = pickle.load(
            open('../scalers_model/competition_time_month_scaler.pkl', 'rb'))
        self.promo2_since_year_scaler = pickle.load(open('../scalers_model/promo2_since_year_scaler.pkl', 'rb'))
        self.promo2_time_week_scaler = pickle.load(open('../scalers_model/promo2_time_week_scaler.pkl', 'rb'))
        self.store_scaler = pickle.load(open('../scalers_model/store_scaler.pkl', 'rb'))
        self.year_scaler = pickle.load(open('../scalers_model/year_scaler.pkl', 'rb'))

    def data_cleaning(self, df1):
        ## 1.1. Rename Columns
        cols_old = df1.columns.tolist()

        snakecase = lambda x: inflection.underscore(x)

        cols_new = list(map(snakecase, cols_old))

        # rename
        df1.columns = cols_new

        ## 1.3. Data Types
        df1['date'] = pd.to_datetime(df1['date'])

        # competition_distance
        df1['competition_distance'] = df1['competition_distance'].apply(lambda x: 200000.0 if math.isnan(x) else x)

        # competition_open_since_month
        df1['competition_open_since_month'] = df1['competition_open_since_month'].apply(
            lambda x: 1 if math.isnan(x) else x)

        # competition_open_since_year
        df1['competition_open_since_year'] = df1['competition_open_since_year'].apply(
            lambda x: 1900 if math.isnan(x) else x)

        # promo2_since_week
        df1['promo2_since_week'] = df1['promo2_since_week'].apply(lambda x: 1 if math.isnan(x) else x)

        # promo2_since_year
        df1['promo2_since_year'] = df1['promo2_since_year'].apply(lambda x: 2018 if math.isnan(x) else x)

        # promo interval
        df1['promo_interval'].fillna(0, inplace=True)

        ## 1.6. Change Data Types
        # competiton
        df1['competition_open_since_month'] = df1['competition_open_since_month'].astype('int64')
        df1['competition_open_since_year'] = df1['competition_open_since_year'].astype('int64')

        # promo2
        df1['promo2_since_week'] = df1['promo2_since_week'].astype('int64')
        df1['promo2_since_year'] = df1['promo2_since_year'].astype('int64')

        return df1

    def feature_engineering(self, df2):
        # year
        df2['year'] = df2['date'].dt.year

        # month
        df2['month'] = df2['date'].dt.month

        # day
        df2['day'] = df2['date'].dt.day

        # week of year
        df2['week_of_year'] = df2['date'].dt.weekofyear

        # year week
        df2['year-month'] = df2['date'].dt.strftime('%Y-%m')

        month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep',
                     10: 'Oct', 11: 'Nov', 12: 'Dec'}

        df2['month_map'] = df2['date'].dt.month.map(month_map)

        # create is promo2
        df2['is_promo2'] = df2[['promo_interval', 'month_map', 'year', 'competition_open_since_year']].apply(
            lambda x: 0 if x['promo_interval'] == 0 \
                else 1 if (x['month_map'] in x['promo_interval'].split(',')) & (
                        x['year'] <= x['competition_open_since_year']) \
                else 0, axis=1)

        # competition since
        df2['competition_since'] = df2.apply(
            lambda x: datetime.datetime(year=x['competition_open_since_year'], month=x['competition_open_since_month'],
                                        day=1), axis=1)
        df2['competition_time_month'] = ((df2['date'] - df2['competition_since']) / 30).apply(lambda x: x.days).astype(
            'int64')
        df2['competition_time_days'] = (df2['date'] - df2['competition_since']).apply(lambda x: x.days).astype('int64')

        # promo2 since
        df2['promo2_since'] = df2['promo2_since_year'].astype(str) + '-' + df2['promo2_since_week'].astype(str)
        df2['promo2_since'] = df2['promo2_since'].apply(
            lambda x: datetime.datetime.strptime(x + '-1', '%Y-%W-%w') - datetime.timedelta(days=7))
        df2['promo2_time_week'] = ((df2['date'] - df2['promo2_since']) / 7).apply(lambda x: x.days).astype('int64')
        df2['promo2_time_days'] = (df2['date'] - df2['promo2_since']).apply(lambda x: x.days).astype('int64')

        # assortment
        df2['assortment'] = df2['assortment'].apply(
            lambda x: 'basic' if x == 'a' else 'extra' if x == 'b' else 'extended')

        # state holiday
        df2['state_holiday'] = df2['state_holiday'].apply(lambda
                                                              x: 'public_holiday' if x == 'a' else 'easter_holiday' if x == 'b' else 'christmas' if x == 'c' else 'regular_day')

        return df2

    def data_preparation(self, df5):
        ## 5.2. Rescaling
        # competition distance
        print('entering data prep')

        df5['competition_distance'] = self.competition_distance_scaler.transform(df5[['competition_distance']].values)

        # competition time month
        df5['competition_time_month'] = self.competition_time_month_scaler.transform(df5[['competition_time_month']].values)

        # promo time week
        df5['promo2_time_week'] = self.promo2_time_week_scaler.transform(df5[['promo2_time_week']].values)

        # year
        df5['year'] = self.year_scaler.transform(df5[['year']].values)

        # competition open since year
        df5['competition_open_since_year'] = self.competition_open_since_year_scaler.transform(df5[['competition_open_since_year']].values)

        # promo 2 open since year
        df5['promo2_since_year'] = self.promo2_since_year_scaler.transform(df5[['promo2_since_year']].values)

        # store
        df5['store'] = self.store_scaler.transform(df5[['store']].values)


        ### 5.3.1. Encoding
        df5 = pd.get_dummies(df5, prefix=['state_holiday'], columns=['state_holiday'])

        df5 = pd.get_dummies(df5, prefix=['store_type'], columns=['store_type'])

        df5 = pd.get_dummies(df5, prefix=['assortment'], columns=['assortment'])

        ### 5.3.3. Nature Transformation
        # day of week
        df5['day_of_week_sin'] = df5['day_of_week'].apply(lambda x: np.sin(x * (2. * np.pi / 7)))
        df5['day_of_week_cos'] = df5['day_of_week'].apply(lambda x: np.cos(x * (2. * np.pi / 7)))

        # month
        df5['month_sin'] = df5['month'].apply(lambda x: np.sin(x * (2. * np.pi / 12)))
        df5['month_cos'] = df5['month'].apply(lambda x: np.cos(x * (2. * np.pi / 12)))

        # day
        df5['day_sin'] = df5['day'].apply(lambda x: np.sin(x * (2. * np.pi / 30)))
        df5['day_cos'] = df5['day'].apply(lambda x: np.cos(x * (2. * np.pi / 30)))

        # week of year
        df5['week_of_year_sin'] = df5['week_of_year'].apply(lambda x: np.sin(x * (2. * np.pi / 52)))
        df5['week_of_year_cos'] = df5['week_of_year'].apply(lambda x: np.cos(x * (2. * np.pi / 52)))

        print('encoding ok!!!!')

        cols_selected = ['store',
                         'promo',
                         'competition_distance',
                         'competition_open_since_year',
                         'promo2_since_year',
                         'competition_time_month',
                         'promo2_time_week',
                         'store_type_a',
                         'store_type_c',
                         'store_type_d',
                         'assortment_extended',
                         'assortment_extra',
                         'day_of_week_sin',
                         'day_of_week_cos',
                         'month_cos',
                         'day_sin',
                         'day_cos',
                         'week_of_year_cos']

        aux = pd.DataFrame(data=None, columns=cols_selected)
        aux2 = df5[(df5.columns) & (cols_selected)]
        df5 = pd.merge(aux2, aux, how='left').fillna(0.0)
        df5 = df5[cols_selected]

        return df5

    def get_prediction(self, model, original_data, test_data):
        # prediction
        pred = model.predict(test_data)

        # join pred into the original data
        original_data['prediction'] = np.expm1(pred)

        return original_data.to_json(orient='records', date_format='iso')
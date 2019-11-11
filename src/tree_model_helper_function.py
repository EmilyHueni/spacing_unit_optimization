#initial import of modules needed and formating prefrences
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns
from sqlalchemy import create_engine
import psycopg2

from matplotlib import pyplot as plt
import seaborn as sns
plt.style.use('fivethirtyeight')
sns.set_style("white")

#-----------------------------------------------------
import pandas as pd
import numpy as np

#----Model selection--------------------------------
from sklearn.model_selection import train_test_split
from sklearn import datasets
#----------------------------------------------------

#----Models--------------------------------
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, BaggingClassifier, BaggingRegressor
from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error

#----Tree visualization--------------------------------
from sklearn.tree import export_graphviz
from IPython.display import Image
from subprocess import check_call
from sklearn.externals.six import StringIO
from IPython.display import Image
from sklearn.tree import export_graphviz
import pydotplus
from sklearn import ensemble
import matplotlib as mpl
mpl.rcParams.update({
    'font.size'           : 20.0,
    'axes.titlesize'      : 'large',
    'axes.labelsize'      : 'medium',
    'xtick.labelsize'     : 'medium',
    'ytick.labelsize'     : 'medium',
    'legend.fontsize'     : 'large',
})
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
import warnings
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:,.2f}'.format

class model_data(object):
    def __init__(self, table_name, pw_text='postgres_connection.txt', y_label='cum_365_boe'):
        self.table_name = table_name
        # Write Results to final database
        self.postgres_connection_file = pw_text
        with open(selfpostgres_connection_file, 'r') as f:
            self.connection = f.read()
        self.engine = create_engine(self.connection)
        self.sql_get_table = """select *
        FROM production.m6_nw1_only_min_col_base_st_water_gor_rock_cluster
        """ % self.table_name
        self.df = pd.read_sql_query(self.sql, con=engine)
        self.y_label = y_label

    def upload_postgres(self):
        try:
            self.engine.execute('DELETE FROM production.%s' % self.table_name)
        except:
            pass
        self.df.to_sql(self.table_name, self.engine, schema="production", if_exists='append')

    def clean_df(self):
        self.df['nw1_dist_2d'].fillna(2000, inplace=True)
        self.df.drop_duplicates(subset=['api'], inplace=True)
        fill_col_mean = ['depth_diff', 'nw1_percent_near',
                         'nw1_days_prod_of_overlap_year', 'nw1_proppant_latlength',
                         'nw1_fluid_vol_latlength']
        self.df[fill_col_mean] = self.df[fill_col_mean].fillna(self.df[fill_col_mean].mean())
        self.df.dropna(subset=['stabilized_water_cut'], inplace=True)
        self.df = self.df[self.df['nw1_days_prod_of_overlap_year'] < 370]
    def create_train_test_split(self, x_columns):
        self.X = self.df[x_columns].to_numpy()
        self.y = self.df[y_label].to_numpy()
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    def create_model_predict(self):
        self.clf = GradientBoostingRegressor(learning_rate=0.02, min_samples_leaf=8, n_estimators=500, max_depth=18, max_features=4)
        self.clf.fit(self.X_train, self.y_train)
        self.feature_importances = clf.feature_importances_
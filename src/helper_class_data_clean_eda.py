import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class raw_data_helper_class(object):
    def __init__(self, file_path, working_dir, y_col='eur_bbl_ft',  n_rows=50):
        self.file_path = file_path
        self.working_dir = working_dir
        self.df=pd.read_excel(file_path, converters = {'API':str, 'SEQNUM':str, 'EXC_ID':str}, nrows = n_rows)
        self.y_col = y_col
        self.null_cols = []
        self.header_cols = []
        self.geo_cols = []
        self.prod_cols = []
        self.all_col_list = []
        self.non_null_col_list = []
        self.str_col_list = []
        self.time_stamp_col_list = []
        self.numeric_col_list = []


    def rename_cols(self):
        # clean up column names to drop special characters
        replace_values_lst = [('#', ''), ('.', '_'), (' ', '_'), (':', '_to_'), ('%', '_perc_'), ('+', 'plus')]

        for original_value, replace in replace_values_lst:
            self.df.columns = self.df.columns.str.replace(original_value, replace)
        self.df.columns = self.df.columns.str.lower()
        self.all_col_list = list(self.df.columns.values)

    def create_success_category(self, row):
        if row < 5:
            return '0-5'
        elif row < 10:
            return '5-10'
        elif row < 15:
            return '10-15'
        elif row < 20:
            return '15-20'
        elif row < 25:
            return '20-25'
        elif row < 30:
            return '25-30'
        else:
            return '30<'

    def add_features_to_df(self):
        self.df['saturation_length'] = (pd.to_datetime(self.df['first_prod'], 'day') - pd.to_datetime(self.df['frac_date'], 'day')).dt.days
        self.df['y_label_category'] = self.df['eur_bbl_ft'].apply(self.create_success_category)

    def update_null_cols_list(self):
        df_clean = self.df.dropna(how='all', axis='columns')
        self.non_null_col_list = list(df_clean.columns.values)
        self.null_cols = [a for a in self.all_col_list if a not in self.non_null_col_list]

    def update_header_cols(self, header_list):
        self.header_cols = header_list
        self.all_col_list = [a for a in self.all_col_list if a not in header_list]

    def parse_cols_type(self):
        for c in self.non_null_col_list:
            if c in self.header_cols:
                pass
            elif self.df[c].dtype == object:
                self.str_col_list.append(c)
            elif self.df[c].dtype == 'datetime64[ns]':
                self.time_stamp_col_list.append(c)
            else:
                self.numeric_col_list.append(c)

    def update_prod_cols(self, prod_col_list):
        self.prod_cols = prod_col_list
        self.all_col_list = [a for a in self.all_col_list if a not in prod_col_list]

    def update_financial_cols(self, financial_col_list):
        self.financial_col_list = financial_col_list
        self.all_col_list = [a for a in self.all_col_list if a not in financial_col_list]

    def return_plot_by_reservoir(self, cols, title=''):
        df_w = self.df.copy()
        df_w = df_w[cols]
        features = []
        for f in df_w.columns:
            if df_w[f].dtypes == 'object' or f == self.y_col:
                print(f)
            else:
                features.append(f)

        df_new = df_w.dropna()
        df_new.dropna(axis='columns', inplace=True)

        print('shape df: ', df_new.shape)
        print('columns used in pca: ')
        print(features)
        print('num features used in pca: ', len(features))

        # Separating out the features
        x = df_new.loc[:, features].values
        x = StandardScaler().fit_transform(x)

        # PCA Projection to 2D
        pca = PCA(n_components=2)

        principalComponents = pca.fit_transform(x)
        principalDf = pd.DataFrame(data=principalComponents, columns=['pca_1', 'pca_2'])
        finalDf = pd.concat([principalDf, df_new[['reservoir', 'api', 'y_label_category']].reset_index()], axis=1)

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlabel('pca_1', fontsize=15)
        ax.set_ylabel('pca_2', fontsize=15)

        targets = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30<', ]
        colors = ['red', 'r', 'y', 'grey', 'g', 'b', 'navy']
        markers = ['o', 'X']
        vendors = ['Niobrara', 'Codell']

        for i, v in enumerate(vendors):
            vendor_df = finalDf[finalDf['reservoir'] == v]
            for target, color in zip(targets, colors):
                indicesToKeep = vendor_df['y_label_category'] == target

                ax.scatter(vendor_df.loc[indicesToKeep, 'pca_1']
                           , vendor_df.loc[indicesToKeep, 'pca_2']
                           , c=color, edgecolors='k'
                           , s=180, marker=markers[i])

        y = finalDf['pca_2'].to_list()
        z = finalDf['pca_1'].to_list()
        n = finalDf['y_label_category'].to_list()
        for i, txt in enumerate(n):
            if txt == '0-5':
                ax.annotate(txt, (z[i] + .08, y[i] + 0.08), size=12)

        ax.legend(targets)
        ax.grid()

        evr = pca.explained_variance_ratio_
        perc_var = evr.sum() * 100

        ax.set_title(title, fontsize=20)
        text_annot = "Explained variance by 2 principal components: {}%".format(int(round(perc_var)))
        print(text_annot)

        ax.text(-1.5, 6.5, text_annot, fontsize=15)

        print(perc_var)
        plt.savefig('pca_raw_data.png')
        plt.show()

    def create_and_save_correlation_heatmap(self, cols, title, text_notes, text_loc=6, size=1):
        working_df = self.df.copy()
        working_df = working_df[cols]
        f_scale = 3  # 1
        l_width = .08  # .08
        title_size = 40  # 40
        dpi_size = 200  # 300
        fig_width_height = 50  # 40
        annot_size = 6  # 7

        df_corr = working_df.corr()
        sns.set(font_scale=f_scale)
        hm = sns.heatmap(df_corr,
                         xticklabels=df_corr.columns,
                         yticklabels=df_corr.columns, annot=True, annot_kws={"size": (annot_size)}, cmap="RdBu",
                         vmin=-1, vmax=1, linewidths=l_width).set_title(title, fontsize=title_size)

        heatmap1 = hm.get_figure()
        print(len(heatmap1.axes))
        ax = heatmap1.axes[0]
        ax.text(-text_loc, -text_loc, text_notes, fontsize=8)
        heatmap1.set_figwidth(fig_width_height)
        heatmap1.set_figheight(fig_width_height)
        heatmap1.savefig('heatmap_{}.png'.format(title), dpi=dpi_size, format='png')

if __name__ == '__main__':
    excel_file = r"C:\Users\ehueni\PycharmProjects\Heredot_EMH_Working\capstone2_wellrepo_regression\BasicWellDataRepository.Hereford.xlsx"
    emh_folder = r'C:\Users\ehueni\PycharmProjects\Heredot_EMH_Working\capstone2_wellrepo_regression'
    data = raw_data_helper_class(excel_file, emh_folder)
    data.rename_cols()
    data.update_null_cols_list()
    data.update_header_cols(['well_name', 'api', 'pad', 'seqnum', 'exc_id', 'afe', 'reservoir'])
    data.parse_cols_type()
    data.create_and_save_correlation_heatmap(['stabilized_watercut', 'niob_p90_ild', 'lateral_length',
       'nominal_well_equivalent', 'avg_pressure', 'spacing_interwell',
       'dsupriorcumoil', 'fluidperfoot'], 'testing', 'test_notes')
    print(data.all_col_list)

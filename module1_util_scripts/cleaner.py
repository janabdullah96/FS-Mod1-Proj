
import pandas as pd
import numpy as np


class DatasetCleaner():
    
    """
    class to clean dataframes 

    """
    
    def __init__(self, df, threshold_config):
        
        """
        construct all necessary attributes
        
        Args:
            df (pandas.DataFrame): df to be cleaned
            threshold_config (JSON): JSON object with cleaning configurations
        
        """
        self.config = threshold_config
        self.df = df
        return
    
    def identify_placeholders_outliers_iqr_method(self, col):
        
        """
        -method to replace numerical placeholders/outliers as np.nan
        -uses the interquartile range method to idenfity placeholders/outliers
         by identifying them as any data point outside of 
        iqr * ***configured_multiplier*** away from the median, on both sides
        
        Args:
            col (pandas.Series): series to be searched for outliers/placeholders
        
        Returns:
            col (pandas.Series): pandas.Series with all outliers/placeholders set to np.nan
        
        """
        median = col.median()
        Q1 = col.describe()['25%']
        Q3 = col.describe()['75%']
        iqr = Q3-Q1
        multiplier = self.config['numerical']['outlier_multipliers']['iqr']
        lower_limit = median - (iqr*multiplier)
        upper_limit = median + (iqr*multiplier)
        col = col.map(lambda x: x if ((x > lower_limit) & (x < upper_limit)) else np.nan)
        return col
    
    def identify_placeholders_outliers_stdev_method(self, col):
    
        """
        -method to replace numerical placeholders/outliers as np.nan
        -uses the standard deviation method to idenfity placeholders/outliers
         by identifying them as any data point outside of 
         stdev * ***configured_multiplier*** away from the mean, on both sides
        
        Args:
            col (pandas.Series): series to be searched for outliers/placeholders
        
        Returns:
            col (pandas.Series): pandas.Series with all outliers/placeholders set to np.nan
        
        """
        mean = col.mean()
        stdev = col.describe()['std']
        multiplier = self.config['numerical']['outlier_multipliers']['stdev']
        lower_limit = mean - (stdev*multiplier)
        upper_limit = mean + (stdev*multiplier)
        col = col.map(lambda x: x if ((x > lower_limit) & (x < upper_limit)) else np.nan)
        return col
    
    def replace_missing_categorical_data(self, col):
        
        """
        -method to replace missing categorical data in column with the
         most frequest value that appears in that column, if that value
         exceeds the configured normalized frequency percentage minimum
        
        Args:
            col (pandas.Series): series to search for missing categorical data
        
        Returns:
            col (pandas.Series): cleaned series
            num_missing_strings (int): numer of values that are valid python values but 
                                        actually denote that a datapoint is missing.
                                        i.e string values that are equal to 
                                        "missing", "null", etc.
        
        """
    
        missing_string_ls = self.config['categorical']['missing_string_values']
        num_missing_strings = len([x for x in col.values.tolist() if x in missing_string_ls])
        col = col.map(lambda x: np.nan if x in missing_string_ls else x)
        value_freq_pct = self.config['categorical']['value_freq_pct']
        value_counts_normalized_dict = col.value_counts(normalize=True).to_dict()
        dict_filter = {k: v for k, v in value_counts_normalized_dict.items() if v > value_freq_pct}
        if len(dict_filter) > 0:
            sorted_dict = sorted(dict_filter.items(), key=lambda x: x[1], reverse=True)
            most_freq_value = sorted_dict[0][0]
            col = col.map(lambda x: x if pd.notnull(x) else most_freq_value)
        else:
            pass
        return col, num_missing_strings
    
    def clean_small_dataset(self, df):
        
        """
        -method to clean small dataset of missing values
        -this doesn't remove any data, all it does 
         is convert numerical placeholders/outliers to np.nan
         using the iqr method to identify placeholders/outliers
        
        Args:
            df (pandas.DataFrame): small dataframe to be cleaned
        
        Returns
            df (pandas.DataFrame): cleaned small dataframe
        
        """
        cols = df.columns.values.tolist()
        for elem in self.config['ignore_cols']:
            try:
                cols.remove(elem)
                print(f'removing {elem} col')
            except:
                continue

        for col in cols:
            try:
                df[col] = self.identify_placeholders_outliers_iqr_method(df[col].astype(float))
            except ValueError:
                continue
        return df

    def clean_large_dataset(self, df):
        
        """
        -method to clean large dataset of missing values
        -uses the hierachy of removing, replacing, and keeping missing/null data based on
         the magnitude of missing/null data with respect to size of entire dataframe
        -thresholds are set in the configuration file
        -generally, if the number of missing values are a small portion of overall dataset,
         the data points are removed. If the number of missing values is a slightly larger portion
         of overall dataset, the data points are replaced with a different value, and if the number of missing 
         values is a substantial portion of the overall dataset, nothing is done and missing data is kept.
        -this method uses the stdev method to idenfity numerical placeholders and outliers
        -after the above methods are applied on the COLUMN axis, this method looks to the INDEX axis to identify
         any rows with a substantially missing amount of data. The missing pct threshold is set in the configuration.
         is the number of such rows is less than a certain percentage of the total dataset (set in configuration),
         these rows are removed
        
        Args:
            df (pandas.DataFrame): large dataframe to be cleaned
        
        Returns:
            df (pandas.DataFrame): cleaned large dataframe
        
        """
        
        processed_cols = []
        
        cols = df.columns.values.tolist()
        for elem in self.config['ignore_cols']:
            try:
                cols = [i for i in cols if i != elem]
            except ValueError:
                continue
        
        for col in cols:
            fails = 0
            nan_count = df[col].isna().sum()
            all_values_numeric_check = all(df[col]
                                           .dropna()
                                           .apply(lambda x: all(i.isdigit() for i in (str(x)
                                                                                    .replace(',', '')
                                                                                    .replace('.', '')
                                                                                   )
                                                             )))
            try:
                if all_values_numeric_check:
                    df[col] = df[col].str.replace(',', '')
                    df[col] = df[col].astype(float)
                else:
                    pass
            except AttributeError:
                pass
            try:
                placeholder_count = self.identify_placeholders_outliers_stdev_method(df[col].astype(float)).isna().sum()
                total_null_values = nan_count + placeholder_count
                col_null_pct = total_null_values / len(df)
                if col_null_pct and col_null_pct < self.config['numerical']['method_thresholds']['remove']:
                    df.drop(df[df[col].isna()].index, inplace=True)
                elif col_null_pct and col_null_pct < self.config['numerical']['method_thresholds']['replace']:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    pass
                processed_cols.append(col)
            except:
                fails+=1

            try:
                if not all_values_numeric_check:
                    replacement_col, placeholder_count = self.replace_missing_categorical_data(df[col])
                    missing_string_ls = self.config['categorical']['missing_string_values']
                    total_null_values = nan_count + placeholder_count
                    col_null_pct = total_null_values / len(df)
                    if col_null_pct and col_null_pct < self.config['categorical']['method_thresholds']['remove']:
                        df.drop(df[df[col].isna()].index, inplace=True)
                        rows_with_placeholder_strings = df[df[col].isin(missing_string_ls)]
                        if len(rows_with_placeholder_strings) > 0:
                            df.drop(rows_with_placeholder_strings.index, inplace=True)
                        else:
                            pass
                    elif col_null_pct and col_null_pct < self.config['categorical']['method_thresholds']['replace']:
                        df[col] = replacement_col
                    else:
                        pass
                else:
                    pass
                processed_cols.append(col)
            except:
                fails+=1

            if fails == 2:
                print(f'ERROR! Could not clean col {col}')
            else:
                pass
 
        df['row_missing_pct'] = df.isna().sum(axis=1) / len(df.columns.values)
        rows_breaking_missing_threshold = df[df['row_missing_pct'] >= self.config['row_missing_pct_threshold']]
        agg_row_missing_pct = len(rows_breaking_missing_threshold) / len(df)
        if agg_row_missing_pct and agg_row_missing_pct <= self.config['agg_row_missing_pct_threshold']:
                df.drop(rows_breaking_missing_threshold.index, inplace=True) 
        else:
            pass
        df.drop('row_missing_pct', axis=1, inplace=True)
        unprocessed_cols = [i for i in cols if i not in processed_cols]
        print('Unprocessed cols: ', unprocessed_cols)
        return df

    @classmethod
    def clean(cls, df, config):
        
        """
        -method that asseses whether a dataframe is small or large, and then applies
         the correspinding cleaning method
        -dataset size to distinguish whether a dataframe is small or large is set
         in the configuration
         
        Args:
            df (pandas.DataFrame): dataframe to be cleaned
        
        Returns
            df (pandas.DataFrame): cleaned dataframe
        
        """
        print('=' *30)
        print(f'Cleaning dataset with {cls.__name__}')
        obj = cls(df, config)
        if len(df) <= obj.config['df_len_cutoff']:
            clean_df = obj.clean_small_dataset(df)
        elif len(df) > obj.config['df_len_cutoff']:
            clean_df = obj.clean_large_dataset(df)
        else:
            pass
        print(f'Finished cleaning dataset with {cls.__name__}')
        print('=' *30)
        return clean_df



import gzip
import os
import pandas as pd
import sqlite3
import json

import warnings
warnings.filterwarnings("ignore")

class Loader():
    
    """
    class for loading/reading/uploading datasets and reading JSON configs
    
    """
    def __init__(self, **folderpath_kwargs):
        
        """
        Kwargs:
            datasets_folderpath (str): folderpath of datasets
            configs_foldetpath (str): folderpath of JSON config files
        
        """
        self.datasets_folderpath = folderpath_kwargs['datasets_folderpath']
        self.configs_folderpath = folderpath_kwargs['configs_folderpath']
        return

    def csv_reader(self, file):
        
        print(f'Reading {file} with {self.__class__.__name__}')
        return pd.read_csv(self.datasets_folderpath + file, compression='gzip')
    
    def tsv_reader(self, file):
        
        print(f'Reading {file} with {self.__class__.__name__}')
        return pd.read_csv(
            self.datasets_folderpath + file, 
            compression='gzip',
            index_col=0, 
            delimiter='\t',
            encoding='unicode_escape'
        )
    
    def read_datasets(self):
        
        """
        reads datasets in datasets folderpath
        
        Returns:
            dataset_dict (dict): dictionary of datasets with dataset names as keys
                                 and corresponding pandas DataFrames as values
        """
        print('='*50)
        dataset_dict = {}
        for filename in os.listdir(self.datasets_folderpath):
            if '.csv' in filename:
                df = self.csv_reader(filename)
            elif '.tsv' in filename:
                df = self.tsv_reader(filename)
            else:
                print('Unsupported filetype. Add reader method for this filetype!')
            for char in ['.csv', '.tsv', '.gz']:
                filename = filename.replace(char, '')
            filename = filename.replace('.', '_')
            dataset_dict[filename] = df
        print('='*50)
        return dataset_dict
    
    def read_configs(self):
        
        """
        reads JSON files in configs folderpath
        
        Returns:
            config_dict (dict): dictionary of JSON objects with config names as keys
                                and correspinding JSON objects as values
        """
        
        print('='*50)
        for filename in os.listdir(self.configs_folderpath):
            print(f'Reading {filename} with {self.__class__.__name__}')
            config_dict = {}
            with open(self.configs_folderpath + filename, 'r') as f:
                filename = filename.replace('.json','')
                config = json.loads(f.read())
                config_dict[filename] = config
        print('='*50)
        return config_dict
    
    @classmethod
    def load_to_sql(cls, db, dataset_dict, remove=True):

        """
        loads dictionary of datasets to database
        Args:
            db (str): name of the database
            dataset_dict (dict): dict where keys = table names (str) and values = tables (pandas dataframes)
            remove (bool): Bool val to determine whether to remove existing db or not

        """
        print('='*50)
        if remove:
            os.remove(db)
            print(f'Removed existing database file {db} with {cls.__name__}!')
        else:
            pass
        conn = sqlite3.connect(db)
        for table_name, df in dataset_dict.items():
            try:
                df.to_sql(table_name, conn)
                print(f'Sucessfully uploaded {table_name} to {db} with {cls.__name__}!')
            except Exception as e:
                print(e)
                print(f'Failed to upload {table_name} to {db} with {cls.__name__}!')
        print('='*50)


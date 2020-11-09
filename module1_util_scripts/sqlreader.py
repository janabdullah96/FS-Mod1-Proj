
import sqlite3
import pandas as pd


class SQLReader():
    
    """
    class to read sql queries and return query results as pandas dataframes
    
    """
    @classmethod
    def read(cls, query, db):
    
        """
        method to read sql queries and return pandas DataFrame
        
        Args:
            query (str): sql query string
            db (str): name of database to connect to
        
        Returns:
            df (pandas.DataFrame): pandas dataframe of query results
        
        """
        print('=' *30)
        print(f'Processing SQL Query with {cls.__name__}')
        conn = sqlite3.connect(db)
        print(f'Connecting to {db} with {cls.__name__}')
        cur = conn.cursor()
        query_results = cur.execute(query).fetchall()
        print(f'Sucessfully fetched query results with {cls.__name__}')
        df = pd.DataFrame(query_results)
        df.columns = [col[0] for col in cur.description]
        conn.close()
        print(f'Closed connection to {db} with {cls.__name__}')
        print('=' *30)
        return df


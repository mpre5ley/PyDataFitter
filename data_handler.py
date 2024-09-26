# data_importer.py

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql import text



class DataImporter:
    """ 
    Class to import data into a database 

    Args: session (Session): An instance of the database session object 
    """
    def __init__(self, session):
        self.session = session

    def import_data(self, data, table_name):
        """
        Imports data into a database table
        
        Args:
        data (DataFrame): The dataframe that holds the data to import
        table_name (str): The name of the table to create in the database
         
        Returns:
        None
        """
        data.to_sql(table_name, self.session.bind, if_exists='replace', index=False)
        self.session.commit()
        print(f'Imported data into table {table_name}')

    def import_data_from_csv(self, file_path, table_name):
        """
        Imports data from CSV into Pandas DataFrame
        
        Args:
        file_path (str): relative path of the CSV file
        table_name (str): The name of the table to create in the database
         
        Returns:
        None        
        """
        data = pd.read_csv(file_path)
        self.import_data(data, table_name)

    def load_list_to_df(self, db_engine, col_list):
        """
        Imports list of columns from database table into Pandas DataFrame
        
        Args:
        db_engine (Engine): database engine object
        col_list (list): list of columns to import from database table
         
        Returns:
        DataFrame: A Pandas DataFrame containing the data
        """
        df = pd.DataFrame(columns=col_list)
        with db_engine.connect() as conn:
            for col in col_list:
                col_list_result = conn.execute(text("SELECT " + col + " FROM ideal_function"))
                df[col] = col_list_result.fetchall()
                #convert tuples to floats
                for i in range(len(df[col])):
                    df[col][i] = df[col][i][0]
        return df

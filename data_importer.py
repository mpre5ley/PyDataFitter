# data_importer.py

import pandas as pd
from sqlalchemy.orm import Session

class DataImporter:
    """ 
    Class to import data into a database 

    Args: session (Session): An instance of the database session object 
    """
    def __init__(self, session: Session):
        self.session = session

    def import_data(self, data: pd.DataFrame, table_name: str):
        """
        Imports data into a database table
        
        Args:
        data (DataFrame): The dataframe that holds the data to import
        table_name (str): The name of the table to create in the database
         
        Returns:
        None
        """
        data.to_sql(table_name, self.session.bind, if_exists='append', index=False)
        self.session.commit()
        print(f'Imported data into table {table_name}')

    def import_data_from_csv(self, file_path: str, table_name: str):
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
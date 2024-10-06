import pandas as pd
from sqlalchemy.sql import text

class DataImporterBase:
    """ 
    Base Class to handle data

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
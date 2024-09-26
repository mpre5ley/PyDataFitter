# data_fitter.py

#from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql import text
import pandas as pd
import numpy as np

class DataFitter:
    """ 
    Class to fit data using the Sum of Squared Errors method

    Args: engine (Engine): An instance of the database engine object 
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.best_fit_functions = []
    
    def calculate_SSE(y_train, y_ideal):
        """
        Calculate the sum of squared errors between the training data and ideal functions
         
        Args:
        y_train (float): y-coordinate from the training data
        y_ideal (float): y-coordinate from the ideal functions
          
        Returns:
        float: The sum of squared errors between the training data and ideal functions
        """

        return np.sum((y_train - y_ideal)**2)
    
    def load_data(self, table_name):
        """
        Load data from the database using engine object
         
        Args:
        table_name (str): The name of the table to load data from
          
        Returns:
        DataFrame: A Pandas DataFrame containing the data
        """

        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM " + table_name))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

    def fit_train_data(self, data_table, ideal_table):
        """
        Finds ideal function that best fits the training function
         
        Args:
        data_table (str): The name of the table that holds the data
        ideal_table (str): The name of the table that holds the ideal functions
          
        Returns:
        None
        """

        # Load data from database to Pandas DataFrame
        df_training = self.load_data(data_table)
        df_ideal = self.load_data(ideal_table)

        # Fit data to ideal functions
        for df_train_col in df_training.columns[1:]:
            best_fit_function = []
            best_sse = float('inf')
            for df_ideal_col in df_ideal.columns[1:]:
                sse = np.sum((df_training[df_train_col] - df_ideal[df_ideal_col])**2)
                if sse < best_sse:
                    best_sse = sse
                    best_fit_function = df_ideal_col
            self.best_fit_functions.append(best_fit_function)

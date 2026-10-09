import pandas as pd
import numpy as np

class DataMismatchError(Exception):
    """
    User-defined exception raised when datasets cannot be compared
    because their x coordinates do not match
    """
    pass

class DataFitter:
    """ 
    Class to fit data using the Sum of Squared Errors method

    Args: engine (Engine): An instance of the database engine object 
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.best_fit_functions = []
        # Largest deviation between each training function and its chosen ideal function
        self.max_deviations = {}
    
    @staticmethod
    def calculate_SSE(y_train, y_ideal):
        """
        Calculate the sum of squared errors between the training data and ideal functions
         
        Args:
        y_train (Series): y-coordinates from the training data
        y_ideal (Series): y-coordinates from the ideal functions
          
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

        return pd.read_sql_table(table_name, self.engine)

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

        # Functions are compared row by row, so the x coordinates must be identical
        if not df_training['x'].equals(df_ideal['x']):
            raise DataMismatchError(
                f"x coordinates in '{data_table}' do not match those in '{ideal_table}'")

        # Fit data to ideal functions
        for df_train_col in df_training.columns[1:]:
            best_fit_function = []
            best_sse = float('inf')
            for df_ideal_col in df_ideal.columns[1:]:
                sse = self.calculate_SSE(df_training[df_train_col], df_ideal[df_ideal_col])
                if sse < best_sse:
                    best_sse = sse
                    best_fit_function = df_ideal_col
            self.best_fit_functions.append(best_fit_function)
            # Record the largest deviation for the test data mapping criterion
            self.max_deviations[best_fit_function] = np.max(
                np.abs(df_training[df_train_col] - df_ideal[best_fit_function]))

        
    def find_delta_y(self, best_fit_func, best_fit_df, test_data_df):
        """
        Find deviation in Y coordinate between test data and best fit ideal functions.
        A test point is only mapped to an ideal function if its deviation does not
        exceed the largest training deviation for that function by more than sqrt(2).
         
        Args:
        best_fit_func (list): A list of the best fit ideal functions
        best_fit_df (DataFrame): A Pandas DataFrame containing the best fit ideal functions x-y coordinates
        test_data_df (DataFrame): A Pandas DataFrame containing the test data x-y coordinates
          
        Returns:
        y_delta_num: A list containing the delta in Y coordinate between test data and best fit ideal functions,
                     or None where no ideal function meets the criterion
        y_delta_func: A list containing the name of the ideal function with the smallest y-coordinate deviation,
                      or None where no ideal function meets the criterion
        """
        # Line up each test point with the ideal function values at the same x coordinate
        merged = test_data_df[['x', 'y']].merge(best_fit_df, on='x', how='left')
        missing_x = merged.loc[merged[best_fit_func].isna().any(axis=1), 'x']
        if not missing_x.empty:
            raise DataMismatchError(
                f"Test data x coordinates not found in ideal functions: {missing_x.tolist()}")

        y_delta_num = []
        y_delta_func = []
        for _, row in merged.iterrows():
            y_delta_small = None
            y_delta_col_small = None
            for best_fit_col in best_fit_func:
                y_delta = abs(row[best_fit_col] - row['y'])
                within_limit = y_delta <= self.max_deviations[best_fit_col] * np.sqrt(2)
                if within_limit and (y_delta_small is None or y_delta < y_delta_small):
                    y_delta_small = y_delta
                    y_delta_col_small = best_fit_col
            y_delta_num.append(y_delta_small)
            y_delta_func.append(y_delta_col_small)
        
        return y_delta_num, y_delta_func

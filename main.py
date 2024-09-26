from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from data_handler import DataImporter
from data_fitter import DataFitter
from sqlalchemy import select
from sqlalchemy.sql import text
import pandas as pd 
from collections import Counter


def create_session(db_engine):
    """
    Returns an instance of the database session configuration
    
    Args:
    db_engine (Engine): An instance of the database engine object
         
    Returns:
    session_instance (Session): An instance of the database session 
                                configuration
    """
    base = declarative_base()
    base.metadata.create_all(db_engine)
    session = sessionmaker(bind=db_engine)
    session_instance = session()
    return session_instance

def main():
    """ Main function to run the program """

    # Create a SQLite database engine
    db_engine = create_engine('sqlite:///data.db')
    # Create a session
    session_instance = create_session(db_engine)

    # Create model to move data to database
    data_import = DataImporter(session_instance)
    # Import data from CSVs to database
    data_import.import_data_from_csv('./dataset/train.csv', 'training_data')
    data_import.import_data_from_csv('./dataset/ideal.csv', 'ideal_function')
    data_import.import_data_from_csv('./dataset/test.csv', 'test_data')

    # Fit training data to find 4 ideal functions
    data_fit = DataFitter(db_engine)
    data_fit.fit_train_data('training_data', 'ideal_function')
    best_fit = data_fit.best_fit_functions
    # Add x column for ideal function x coordinate
    best_fit.append('x')

    # Load best fit ideal functions from database
    '''
    df = pd.DataFrame(columns=best_fit)
    print(df)
    with db_engine.connect() as conn:
        for col in best_fit:
            best_fit_result = conn.execute(text("SELECT " + col + " FROM ideal_function"))
            df[col] = best_fit_result.fetchall()
            #convert tuples to floats
            for i in range(len(df[col])):
                df[col][i] = df[col][i][0]
    '''
    df = data_import.load_list_to_df(db_engine, best_fit)
    
    # Load test data from database into dataframe
    with db_engine.connect() as conn:
        test_data_result = conn.execute(text("SELECT * FROM test_data"))
    test_data_df = pd.DataFrame(test_data_result.fetchall(), columns=test_data_result.keys())

    # Find deviation in Y coordinate between test data and best fit ideal functions, record the smallest deviation into lists
    y_delta_list = []
    y_delta_col_list = []
    for test_data_index in range(len(test_data_df)):
        for best_fit_col in best_fit[:-1]:
            for df_index in range(len(df)):
                if df['x'][df_index] == test_data_df['x'][test_data_index]:
                    y_delta = abs(df[best_fit_col][df_index] - test_data_df['y'][test_data_index])
                    y_delta_col = best_fit_col
                    break # When X coodinates match, break loop and compare y deviation

            # Compare the current deviation to the previous smallest deviation
            try:
                y_delta_small
            except NameError:
                y_delta_small = y_delta
                y_delta_col_small = y_delta_col
            else:
                if y_delta < y_delta_small:
                    y_delta_small = y_delta
                    y_delta_col_small = y_delta_col
        
        # Store y delta and ideal function name in lists for dataframe
        y_delta_list.append(y_delta_small)
        y_delta_col_list.append(y_delta_col_small)

        # Display number of times ideal function has the smallest deviation
        print(Counter(y_delta_col_list))

        # Delete variables for next row of test data
        del y_delta_small
        del y_delta_col_small

    print(test_data_df.head())
    session_instance.close()
    db_engine.dispose()

if __name__ == "__main__":
    main()
# code can be found at https://github.com/mpre5ley/PyDataFitter

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from data_handler import DataHandler
from data_fitter import DataFitter, DataMismatchError
import matplotlib.pyplot as plt
import sys

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
    data_import = DataHandler(session_instance)
    # Import data from CSVs to database
    data_import.import_data_from_csv('./dataset/train.csv', 'training_data')
    data_import.import_data_from_csv('./dataset/ideal.csv', 'ideal_function')
    data_import.import_data_from_csv('./dataset/test.csv', 'test_data')

    # Fit training data to find 4 ideal functions
    data_fit = DataFitter(db_engine)
    data_fit.fit_train_data('training_data', 'ideal_function')
    best_fit_func = data_fit.best_fit_functions

    # Load x column and best fit ideal functions from database into dataframe
    best_fit_df = data_import.load_list_to_df(db_engine, ['x'] + best_fit_func)
    
    # Load test data from database into dataframe
    test_data_df = data_import.copy_table_to_df(db_engine, 'test_data')

    # Load training data from database into dataframe for visualization
    train_data_df = data_import.copy_table_to_df(db_engine, 'training_data')

    # Find deviation in Y coordinate between test data and best fit ideal functions
    y_delta_num, y_delta_func = data_fit.find_delta_y(best_fit_func, best_fit_df, test_data_df)
    test_data_df['Delta Y (test func)'] = y_delta_num
    test_data_df['No. of ideal func'] = y_delta_func

    # Import test data with deviation in Y coordinate and ideal function number into database
    data_import.import_data(test_data_df, 'test_data')

    # Visualize training data, best fit ideal functions, and test data
    test_plot = test_data_df.plot(x='x', y='y', kind='scatter', rot=45, title='Test Data and Best Fit Ideal Functions')
    best_fit_df.plot(x='x', y=best_fit_func, kind='line', rot=45, ax=test_plot)
    best_fit_df.plot(x='x', y=best_fit_func, kind='line', rot=45, subplots=True, title = 'Best Fit Ideal Functions')
    train_data_df.plot(x='x', y=['y1', 'y2', 'y3', 'y4'], kind='line', rot=45, title='Training Data', subplots=True)
    plt.show()

    # Close the session and dispose the engine
    session_instance.close()
    db_engine.dispose()

if __name__ == "__main__":
    try:
        main()
    except DataMismatchError as error:
        sys.exit(f"Error: {error}")
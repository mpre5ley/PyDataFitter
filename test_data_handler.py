import pandas as pd
import pytest
from sqlalchemy import create_engine
from data_handler import DataHandler
from main import create_session

@pytest.fixture
def db_engine(tmp_path):
    """ Creates a SQLite database engine in a temporary directory """
    engine = create_engine(f'sqlite:///{tmp_path / "test.db"}')
    yield engine
    engine.dispose()

def test_can_load_list_to_df(db_engine):
    """ 
    Tests that the function to load a list of columns from 
    the database to a dataframe works

    Args:
    db_engine (Engine): A temporary database engine

    Returns:
    None
    """
    # Create model to move data to database
    data = DataHandler(create_session(db_engine))
    data.import_data_from_csv('./dataset/ideal.csv', 'ideal_function')
    # create random list of columns from ideal function table
    col_list = ['y1', 'y2', 'y3']
    test_df = data.load_list_to_df(db_engine, col_list)
    assert list(test_df.columns) == col_list
    assert len(test_df) == 400
    expected = pd.read_csv('./dataset/ideal.csv')[col_list]
    pd.testing.assert_frame_equal(test_df, expected)

def test_import_and_copy_table_round_trip(db_engine):
    """ 
    Tests that data imported into the database can be copied back
    into an identical dataframe

    Args:
    db_engine (Engine): A temporary database engine

    Returns:
    None
    """
    data = DataHandler(create_session(db_engine))
    df = pd.DataFrame({'x': [1.0, 2.0], 'y': [3.0, 4.0]})
    data.import_data(df, 'round_trip')
    pd.testing.assert_frame_equal(data.copy_table_to_df(db_engine, 'round_trip'), df)

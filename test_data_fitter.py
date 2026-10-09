import pandas as pd
import pytest
from sqlalchemy import create_engine
from data_fitter import DataFitter, DataMismatchError
from data_handler import DataHandler
from main import create_session

@pytest.fixture
def db_engine(tmp_path):
    """ Creates a SQLite database engine in a temporary directory """
    engine = create_engine(f'sqlite:///{tmp_path / "test.db"}')
    yield engine
    engine.dispose()

def test_calculate_SSE():
    """ Tests the sum of squared errors calculation """
    assert DataFitter.calculate_SSE(pd.Series([1.0, 2.0]), pd.Series([0.0, 4.0])) == 5.0

def test_fit_train_data_selects_closest_ideal_function(db_engine):
    """ 
    Tests that each training function is matched to the ideal function
    with the smallest sum of squared errors

    Args:
    db_engine (Engine): A temporary database engine

    Returns:
    None
    """
    data = DataHandler(create_session(db_engine))
    x = [0.0, 1.0, 2.0]
    data.import_data(pd.DataFrame({'x': x, 'y1': [0.1, 1.1, 2.1]}), 'training_data')
    data.import_data(pd.DataFrame({'x': x, 'y1': [5.0, 5.0, 5.0], 'y2': [0.0, 1.0, 2.0]}), 'ideal_function')

    fitter = DataFitter(db_engine)
    fitter.fit_train_data('training_data', 'ideal_function')

    assert fitter.best_fit_functions == ['y2']
    assert fitter.max_deviations['y2'] == pytest.approx(0.1)

def test_find_delta_y_applies_sqrt2_criterion():
    """ 
    Tests that test points are only mapped to an ideal function when the
    deviation is within sqrt(2) times the largest training deviation

    Args:
    None

    Returns:
    None
    """
    fitter = DataFitter(engine=None)
    fitter.max_deviations = {'y2': 1.0}
    best_fit_df = pd.DataFrame({'x': [0.0, 1.0], 'y2': [0.0, 1.0]})
    # First point deviates by 1.4 (< sqrt(2)), second by 1.5 (> sqrt(2))
    test_df = pd.DataFrame({'x': [0.0, 1.0], 'y': [1.4, 2.5]})

    y_delta_num, y_delta_func = fitter.find_delta_y(['y2'], best_fit_df, test_df)

    assert y_delta_num[0] == pytest.approx(1.4)
    assert y_delta_func == ['y2', None]
    assert y_delta_num[1] is None

def test_fit_train_data_raises_on_mismatched_x(db_engine):
    """ 
    Tests that DataMismatchError is raised when the training data and
    ideal functions do not share the same x coordinates

    Args:
    db_engine (Engine): A temporary database engine

    Returns:
    None
    """
    data = DataHandler(create_session(db_engine))
    data.import_data(pd.DataFrame({'x': [0.0, 1.0], 'y1': [0.0, 1.0]}), 'training_data')
    data.import_data(pd.DataFrame({'x': [0.0, 2.0], 'y1': [0.0, 1.0]}), 'ideal_function')

    with pytest.raises(DataMismatchError):
        DataFitter(db_engine).fit_train_data('training_data', 'ideal_function')

def test_find_delta_y_raises_on_unknown_test_x():
    """ 
    Tests that DataMismatchError is raised when a test data x coordinate
    does not exist in the ideal functions

    Args:
    None

    Returns:
    None
    """
    fitter = DataFitter(engine=None)
    fitter.max_deviations = {'y2': 1.0}
    best_fit_df = pd.DataFrame({'x': [0.0, 1.0], 'y2': [0.0, 1.0]})
    test_df = pd.DataFrame({'x': [5.0], 'y': [0.0]})

    with pytest.raises(DataMismatchError, match='5.0'):
        fitter.find_delta_y(['y2'], best_fit_df, test_df)

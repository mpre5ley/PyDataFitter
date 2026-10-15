import pandas as pd
import pytest
from sqlalchemy import create_engine

import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """ Flask test client backed by a small temporary database """
    engine = create_engine(f'sqlite:///{tmp_path}/test.db')
    x = [0.0, 1.0, 2.0]
    pd.DataFrame({'x': x, 'y1': [0.1, 1.1, 2.1], 'y2': [5.0, 5.2, 4.9]}).to_sql(
        'training_data', engine, index=False)
    pd.DataFrame({'x': x, 'y1': [0.0, 1.0, 2.0], 'y2': [5.0, 5.0, 5.0], 'y3': [100.0, 100.0, 100.0]}).to_sql(
        'ideal_function', engine, index=False)
    pd.DataFrame({
        'x': [2.0, 0.0, 1.0],
        'y': [2.05, 50.0, 5.1],
        'Delta Y (test func)': [0.05, None, 0.1],
        'No. of ideal func': ['y1', None, 'y2'],
    }).to_sql('test_data', engine, index=False)
    engine.dispose()

    monkeypatch.setattr(app, 'DB_URL', f'sqlite:///{tmp_path}/test.db')
    return app.app.test_client()


def test_index_page_renders(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'PyDataFitter Results' in response.data


def test_api_results(client):
    payload = client.get('/api/results').get_json()

    assert [p['ideal'] for p in payload['pairs']] == ['y1', 'y2']
    assert payload['pairs'][1]['max_deviation'] == pytest.approx(0.2)
    assert payload['pairs'][1]['tolerance'] == pytest.approx(0.2 * 2 ** 0.5)
    assert payload['x'] == [0.0, 1.0, 2.0]
    assert list(payload['ideal']) == ['y1', 'y2']
    assert payload['counts'] == {'y1': 1, 'y2': 1, 'unmapped': 1}

    # Test points are sorted by x and NULLs come back as JSON null
    assert [p['x'] for p in payload['test_points']] == [0.0, 1.0, 2.0]
    assert payload['test_points'][0] == {'x': 0.0, 'y': 50.0, 'delta_y': None, 'ideal': None}
    assert payload['test_points'][2]['ideal'] == 'y1'

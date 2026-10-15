"""
Flask dashboard that visualizes the results stored in data.db by main.py.

Run locally:  flask --app app run
Production:   gunicorn app:app
"""

import math
import os

import pandas as pd

from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine

from data_fitter import DataFitter

DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///data.db')

app = Flask(__name__)


def load_results():
    """
    Reads the training data, chosen ideal functions and mapped test data from
    the database and returns them as plain Python structures for the page.
    """
    engine = create_engine(DB_URL)
    try:
        fitter = DataFitter(engine)
        fitter.fit_train_data('training_data', 'ideal_function')
        best_fit = fitter.best_fit_functions

        train_df = fitter.load_data('training_data')
        ideal_df = fitter.load_data('ideal_function')[best_fit]
        test_df = fitter.load_data('test_data')
    finally:
        engine.dispose()

    train_cols = list(train_df.columns[1:])
    pairs = [
        {
            'train': train_col,
            'ideal': ideal_col,
            'max_deviation': float(fitter.max_deviations[ideal_col]),
            'tolerance': float(fitter.max_deviations[ideal_col] * math.sqrt(2)),
        }
        for train_col, ideal_col in zip(train_cols, best_fit)
    ]

    test_df = test_df.sort_values('x')
    test_points = [
        {
            'x': float(row['x']),
            'y': float(row['y']),
            'delta_y': None if pd.isna(row['Delta Y (test func)']) else float(row['Delta Y (test func)']),
            'ideal': None if pd.isna(row['No. of ideal func']) else row['No. of ideal func'],
        }
        for _, row in test_df.iterrows()
    ]

    counts = {col: 0 for col in best_fit}
    counts['unmapped'] = 0
    for point in test_points:
        counts[point['ideal'] if point['ideal'] else 'unmapped'] += 1

    return {
        'pairs': pairs,
        'x': train_df['x'].tolist(),
        'training': {col: train_df[col].tolist() for col in train_cols},
        'ideal': {col: ideal_df[col].tolist() for col in best_fit},
        'test_points': test_points,
        'counts': counts,
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/results')
def results():
    return jsonify(load_results())


if __name__ == '__main__':
    app.run(debug=True)

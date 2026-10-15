# DLMDSPWP01 - Programming with Python Assignment

## About The Project:

The Python program uses training data to find four ideal functions. Then those four ideal functions are used to find the best fit for the test data.

## Built With:

Pandas\
SQLAlchemy\
PyTest\
NumPy\
Matplotlib\
Flask\
Plotly.js

## Usage:

```
pip install -r requirements.txt
python main.py
pytest
```

## Dashboard:

A Flask dashboard visualizes the results stored in `data.db` by `main.py`, so run `python main.py` first. To host it locally:

```
flask --app app run
```

Then open http://127.0.0.1:5000. To deploy it on [fly.io](https://fly.io) using the included `Dockerfile` and `fly.toml`:

```
fly launch --no-deploy   # pick an app name, keeps the existing fly.toml
fly deploy
```

## Changes:

See [CHANGES.md](CHANGES.md) for a summary of the fixes and improvements made after the initial submission.

## Contact:

Matthew Presley - @mpresley - matthew.presley@iu-study.org\
Project Link: https://github.com/mpre5ley/PyDataFitter

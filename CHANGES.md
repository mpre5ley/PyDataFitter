# Summary of Changes

Changes from commit `15d6abc` (Final commit, added GitHub repo address) to `2c4f7bd` (Regenerate data.db with sqrt(2) mapping criterion results).

| Commit | Description |
|---|---|
| `3ce4195` | Fix pandas 3 crash and apply sqrt(2) test data mapping criterion |
| `c4aaa31` | Make tests self-contained and add DataFitter tests |
| `4c851cd` | Add .gitignore, requirements.txt and usage instructions |
| `7c34e96` | Merge pull request #1 from mpre5ley/recommended-changes |
| `2c4f7bd` | Regenerate data.db with sqrt(2) mapping criterion results |

## Bug Fixes

### Crash on pandas 3 (`data_handler.py`)
`load_list_to_df` filled the DataFrame with chained assignment (`df[col][i] = ...`). Under pandas 3 Copy-on-Write this raises a `ValueError`, so the program and the original unit test both failed. Table reads now use `pd.read_sql_table`, which also replaces SQL queries built by string concatenation (`"SELECT * FROM " + table_name`). The same change was applied to `copy_table_to_df` and `DataFitter.load_data`.

### Test data mapping criterion (`data_fitter.py`)
Previously every test point was assigned to the nearest ideal function, no matter how far away it was. For example, the point x=1.9, y=-7730.09 was mapped to `y13` with a deviation of 7728.89.

A test point is now only mapped to an ideal function when its deviation does not exceed the largest deviation between the training data and that ideal function by more than a factor of sqrt(2). To support this:
- `fit_train_data` records the maximum training deviation of each chosen ideal function in `max_deviations`.
- `find_delta_y` was rewritten to line up test points with the ideal functions by x coordinate and apply the criterion. Test points that meet no function's criterion get `None` for both the deviation and the function name, which is stored as NULL in the database.

### `calculate_SSE` could not be called (`data_fitter.py`)
The method had neither a `self` parameter nor `@staticmethod`, and it was never used because `fit_train_data` repeated the formula inline. It is now a static method and `fit_train_data` calls it.

### Hardcoded function names and list mutation (`main.py`)
- `main.py` appended `'x'` to `DataFitter.best_fit_functions`, changing the fitter's own results, and `find_delta_y` skipped the last list element to undo this. The `x` column is now requested separately with `['x'] + best_fit_func`.
- The plots used hardcoded column names (`y13`, `y24`, `y36`, `y40`). They now plot whichever ideal functions were selected, and the test data plot shows all four functions instead of only `y40`.

## Results

The same four ideal functions are selected before and after the changes: `y13`, `y24`, `y36` and `y40`.

| Ideal function | Test points before | Test points after |
|---|---|---|
| `y13` | 20 | 8 |
| `y24` | 26 | 9 |
| `y36` | 22 | 10 |
| `y40` | 32 | 7 |
| Not mapped | 0 | 66 |

Every test point that is still mapped has the same ideal function and deviation as before. `data.db` was regenerated with these results.

## Tests

- `test_data_handler.py` no longer reads the committed `data.db`, so it no longer depends on `main.py` having been run first. Each test builds its own temporary database.
- The `load_list_to_df` test now checks the column order and values against `ideal.csv`, not just that the columns exist.
- New test for an import and read-back round trip through the database.
- New `test_data_fitter.py` covering the SSE calculation, selection of the closest ideal function, the recorded maximum deviation, and both sides of the sqrt(2) limit.

All 5 tests pass on pandas 2.x and pandas 3.0.

## Housekeeping

- Added `.gitignore` for `__pycache__/`, `*.pyc`, `.DS_Store` and `.pytest_cache/`, and stopped tracking the previously committed compiled files and `.DS_Store`.
- Added `requirements.txt` listing pandas, SQLAlchemy (2.0 or later), NumPy, Matplotlib and pytest.
- Added a Usage section to `README.md` with install, run and test commands.

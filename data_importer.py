# data_importer.py

import pandas as pd
from sqlalchemy.orm import Session

class DataImporter:
    def __init__(self, session: Session):
        self.session = session

    def import_data(self, data: pd.DataFrame, table_name: str):
        data.to_sql(table_name, self.session.bind, if_exists='append', index=False)
        self.session.commit()
        print(f'Imported data into table {table_name}')

    def import_data_from_csv(self, file_path: str, table_name: str):
        data = pd.read_csv(file_path)
        self.import_data(data, table_name)
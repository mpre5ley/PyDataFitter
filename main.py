from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from data_importer import DataImporter


def create_session(db_engine):
    base = declarative_base()
    base.metadata.create_all(db_engine)
    session = sessionmaker(bind=db_engine)
    session_instance = session()
    return session_instance
    

def main():
    # Create a SQLite database engine
    db_engine = create_engine('sqlite:///data.db')
    # Create a session
    session_instance = create_session(db_engine)
    # Create model to copy CSV data to database
    data_import = DataImporter(session_instance)
    # Import training data from CSVs to database
    data_import.import_data_from_csv('./dataset/train.csv', 'training_data')
    data_import.import_data_from_csv('./dataset/test.csv', 'test_data')
    data_import.import_data_from_csv('./dataset/ideal.csv', 'ideal_function')
    

if __name__ == "__main__":
    main()












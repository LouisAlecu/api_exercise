from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


class DbConnecter:
    def __init__(self, config):
        """Initialize the attributes with the given config. Tries to establish connection."""
        self._db_path = config["db_path"]
        self._db_con = None
        self._db_cur = None
        self.session = None

        self._establish_connection_()

    def __del__(self):
        """Closes the connection on class destructor."""
        self._db_con.close()
        print("Connection has been closed.")

    def get_db_path(self):
        return self._db_path

    def get_db_engine(self):
        return self._engine

    def create_session(self):
        self.session = sessionmaker(bind=self._engine)

    def _establish_connection_(self):
        """Establish connection and makes the cursor and connection attributes."""
        self._engine = create_engine(f"sqlite:///{self._db_path}")
        self._db_con = self._engine.raw_connection()
        self._db_cur = self._db_con.cursor()

    def execute_query(self, query):
        """
        Executes a query in the database. Because of how sqlalchemy works, 
        the transaction is committed automatically. Autocommit can be set 
        to off manually.
        """
        print(query)
        self._db_cur.execute(query)

    def read_query(self, query):
        """Returns the result of a query."""
        self._db_cur.execute(query)

        result = self._db_cur.fetchall()

        return result


def get_config():
    # config = {
    #     "db_path": os.environ["FCA_DB_PATH"],
    # }
    config = {"db_path": "asdf"}

    return config


def connect_to_database(config=None):
    """
    Returns an object with a connection to the specified database.
    If config is not specified it tried to check in the environment
    for the database configuration.
    """
    if config is None:
        config = get_config()
    db_con = DbConnecter(config)

    return db_con

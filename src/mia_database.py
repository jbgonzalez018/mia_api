import psycopg2 as sql
import json

from mia_exception import *

class MIADatabase:

    __database_connection = None
    __database_cursor = None

    __name = None
    __user = None
    __password = None
    __host = None

    def __init__(self, configuration_file: str):
        with open(configuration_file, 'r') as configuration:
            try:
                config = json.loads(''.join(configuration.readlines()))

            except Exception:
                raise MIAException(MIASystem.DATABASE,
                                   MIASeverity.FATAL,
                                   'Configuration is not a json file')

        try:
            self.__name = config['database']['name']
            self.__user = config['database']['user']
            self.__password = config['database']['password']
            self.__host = config['database']['host']

        except Exception:
            raise MIAException(MIASystem.DATABASE,
                               MIASeverity.FATAL,
                               'Configuration file does not contain the required properties')

        try:
            self.__database_connection = \
                sql.connect(f'dbname={self.__name} user={self.__user} password={self.__password} host={self.__host}')
            self.__database_connection.autocommit = True

            self.__database_cursor = self.__database_connection.cursor()

        except Exception:
            raise MIAException(MIASystem.DATABASE,
                               MIASeverity.FATAL,
                               'Database could not be connected to')
        return

    def is_connected(self):
        return not(self.__database_connection is None)

    def execute(self, query: str):
        try:
            self.__database_cursor.execute(query)

        except Exception:
            raise MIAException(MIASystem.DATABASE,
                               MIASeverity.WARNING,
                               'Query did not execute successfully')

        return None if query.split(' ')[0] != 'SELECT' else self.__database_cursor.fetchall()

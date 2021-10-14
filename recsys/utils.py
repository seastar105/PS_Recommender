import os
import json
import requests
import time
from typing import Tuple, Optional, Dict
import MySQLdb as mysql
import myloginpath

class NoConnectionError(Exception):
    """Exception when make connection fails max_try times"""
    pass

class DBHelper(object):
    """
    Helper class for mysql client. 
    It refresh if connection is dead when query.

    Parameters
    --------------------
    conf_path : Optional[str]
        configure file's path created by mysql_config_editor

    Attributes
    --------------------
    connection : mysql.Connection
        connection to corresponding server.
    conf : Dict
        Mysql server confiuration
    db_name : str
        name of target db in server.
    max_try : int
        try to make connection each second at most max_try when 
        mysql.OperationalError has been raised.
    """
    def __init__(self, conf_path: Optional[str] = None):
        self.db_name = "PS"
        if conf_path:
            try:
                self.conf = myloginpath.parse(self.db_name, path=conf_path)
            except FileNotFoundError:
                print("No such configure file %s" %conf_path)
                print("Use Default Path for configure file")
                conf_path = None
        if conf_path is None:
            try:
                self.conf = myloginpath.parse(self.db_name)
            except FileNotFoundError:
                print("No configure file exists")
                print("Can not make connection to DB server")
                return
        self.connection = None
        self.max_try = 5
        try:
            self.make_connection()
        except NoConnectionError as e:
            print(e)
        # self.connection = mysql.connect(**self.conf, database=self.db_name)


    def make_connection(self, times: int = 1):
        """ Make connection to MySQL server according to configure.

        Raises
        --------------------
        NoConnectionError
            If it fails to connect server for max_try times with 1 second interval
        """
        try:
            self.connection = mysql.connect(**self.conf, db=self.db_name)
        except mysql.OperationalError as e:
            if times < self.max_try:
                time.sleep(1)
                self.make_connection(times+1)
            else:
                raise NoConnectionError(f'Fails {self.max_try} time to connect mysql server. Please check server')
            

    def query(self, query_string: str) -> Optional[Tuple]:
        """ Returns all result by tuple of dictionary, one row per dict.

        It returns query result by tuple (row1, row2, ..., row n)
        If query_string is wrong(Programming Error), returns None.
        
        Parameters
        --------------------
        query_string : str
            Query string that mysql db would execute
        
        Returns
        --------------------
        ret : Optional[Tuple]
            Tuple of dicts. Each dict is one row in query result. 
            None if query_string is invalid

        Examples
        --------------------
        >>> db = DBHelper('./.mylogin.cnf')
        >>> query_string = 'SELECT * FROM user WHERE handle=\'seastar105\''
        >>> db.query(query_string)
        ({'id': 52, 'handle': 'seastar105'},)
        """
        try:
            cur = self.connection.cursor(cursorclass=mysql.cursors.DictCursor)
            cur.execute(query_string)
        except mysql.OperationalError:
            try:
                self.make_connection()
            except NoConnectionError as e:
                print(e)
                return None
            return self.query(query_string)
        except mysql.ProgrammingError:
            print(f'Wrong Query String \"{query_string}\"')
            return None
        ret = cur.fetchall()
        return ret


def call_file_sorted(path):
    directory = os.fsencode(path)
    ret = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        filename = os.path.join(path, filename)
        ret.append(filename)
    ret.sort()
    return ret


def change_path(target_path, source_path, ext):
    basename = os.path.basename(source_path)
    basename = os.path.splitext(basename)[0]
    return_path = os.path.join(target_path, basename) + ext
    return return_path


def main():
    db = DBHelper()
    print(db.query("SELECT * FROM user LIMIT 10"))
    db.connection.close()
    print(db.query("SELECT * FROM tag LIMIT 10"))
    wrong_string = "SELECT * FROM users LIMIT 10"
    print(db.query(wrong_string))


if __name__ == "__main__":
    main()
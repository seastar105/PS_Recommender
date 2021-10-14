import os
import json
import requests
import time
from typing import Tuple, Optional, Dict
import MySQLdb as mysql
import myloginpath


class DBHelper(object):
    """
    Attributes
    --------------------
        connection : mysql.Connection
    """
    def __init__(self):
        self.db_name = "PS"
        self.conf = myloginpath.parse(self.db_name, path="./.mylogin.cnf")
        self.connection = mysql.connect(**self.conf, database=self.db_name)

    def make_connect(self):
        """ Make connection to MySQL server according to configure.
        """
        try:
            self.connection = mysql.connect(**self.conf, db=self.db_name)
        except Exception as e:
            # TODO : if error occurs, what to do?
            print(e)

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
        """
        try:
            cur = self.connection.cursor(cursorclass=mysql.cursors.DictCursor)
            cur.execute(query_string)
        except mysql.OperationalError:
            self.make_connect()
            cur = self.connection.cursor(cursorclass=mysql.cursors.DictCursor)
            return self.query(query_string)
        except mysql.ProgrammingError as e:
            print('Wrong Query String \"%s\"' %query_string)
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
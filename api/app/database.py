<<<<<<< Updated upstream
import os
import json
import requests
import time
from typing import Tuple, Optional, Dict, List
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
            # Is it best practice?
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
        result : Optional[Tuple]
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
        result = cur.fetchall()
        return result


    def get_problem_exp(self, problem_id: int) -> Tuple:
        """Returns corresponding problem's id and exp, empty tuple if not exist.

        Parameters
        --------------------
        problem_id : int
            problem id of target problem
        """
        return self.query(f'SELECT * FROM problem WHERE id={problem_id}')


    def get_problem_tags(self, problem_id: int) -> Optional[Dict]:
        """Returns tags, exp of corresponding problem

        It returns dictionary of corresponding problem.

        Parameters
        --------------------
        problem_id : int
            problem id of target problem
        
        Returns
        --------------------
        result : Dict
            If there's no corresponding problem, it's empty dictoionary
            result has this format {"exp" : int, "tags" : List[int]}
            exp is problem's exp, problem is not ratable or unrated, exp is zero
            tags is list of tag id. it can be empty
        """
        problem_info = self.get_problem_exp(problem_id)
        if bool(problem_info) is False: # empty row
            return None

        result = {'exp' : problem_info[0]['exp']}
        result['tags'] = list()
        if result['exp'] == 0:
            return result

        query_string = f'\
            SELECT tag_id \
            FROM problem join problem_tag on problem.id = problem_tag.problem_id \
            WHERE problem.id = {problem_id}'
        temp = self.query(query_string)
        for row in temp:
            result['tags'].append(row['tag_id'])
        return result


    def get_user_tags(self, handle: str) -> Optional[Dict]:
        """Returns exp of each tags user solved.

        Parameters
        --------------------
        handle : str
            user handle

        Returns
        --------------------
        result : Optional[Dict]
            exp of tags user solved. It has only tag with exp > 0. 
            Format : { tag_id[int] : exp_sum[int] }
            It is None if there's no such user.
            
        """
        if not self.check_user(handle):
            return None
        query_string = f'\
            SELECT SUM(exp) as exp_sum, tag_id \
            FROM ( \
                SELECT t2.id, exp \
                FROM ( \
                    SELECT problem_id \
                    FROM user join ac ON user.id = ac.user_id \
                    WHERE user.handle = \'{handle}\' \
                ) AS t1 JOIN problem AS t2 ON t1.problem_id = t2.id \
            ) AS p1 join problem_tag AS p2 ON p1.id = p2.problem_id \
            GROUP BY tag_id \
            ORDER BY exp_sum DESC'
        query_res = self.query(query_string)
        result = dict()
        for row in query_res:
            tag_id = row['tag_id']
            exp_sum = row['exp_sum']
            result[tag_id] = int(exp_sum)
        return result
    
    def get_user_problems(self, handle: str) -> Optional[List[int]]:
        """Returns list of problems user solved
        
        Parameters
        --------------------
        handle : str
            user handle

        Returns
        --------------------
        result : Optional[List[int]]
            list of the number of problems user solved.
            It is None if there's no such user.
        """
        if not self.check_user(handle):
            return None
        query_string=f'\
            SELECT problem_id \
            FROM user join ac on user.id = ac.user_id \
            WHERE user.handle = \'{handle}\' '
        query_res = self.query(query_string)
        result = [row['problem_id'] for row in query_res]
        
        return result
    
    def topk_problems(self, handle: str, k: int) :
        """Returns list of top k problems user solved.
        """
        if not self.check_user(handle):
            return None
        query_string=f'\
            SELECT problem.id, problem.tier, problem.exp\
            FROM ( \
                SELECT problem_id \
                FROM user join ac on user.id = ac.user_id \
                WHERE user.handle = \'{handle}\' \
               ) AS t1 join problem on problem.id = t1.problem_id \
            ORDER BY tier DESC \
            LIMIT {k}'
            
        query_res = self.query(query_string)
        result = [row for row in query_res]
        
        return result

    
    def check_user_problem(self, handle: str, problem_id: int) -> bool:
        """Returns True if user solved problem_id, False if not.

        Parameters
        --------------------
        handle : str
            user handle
        problem_id : int
            target problem id

        Returns
        --------------------
        True if user with handle solved problem_id, False if not.
        """
        query_string = f'\
            SELECT * \
            FROM ac \
            WHERE user_id in (SELECT id FROM user WHERE handle=\'{handle}\') and problem_id={problem_id}'
        res = self.query(query_string)
        return bool(res)

    
    def check_user(self, handle: str) -> bool:
        """Returns True if user with handle exists in DB, False if not

        Parameters
        --------------------
        handle : str
            user handle

        Returns
        --------------------
        True if user with handle exists in DB, False if not. 
        """
        query_string = f'\
            SELECT * \
            FROM user \
            WHERE handle = \'{handle}\''
        res = self.query(query_string)
        return bool(res)        

def main():
    db = DBHelper()
    """
    print(db.query("SELECT * FROM user LIMIT 10"))
    # Should work if connection has been closed.
    db.connection.close()
    print(db.query("SELECT * FROM tag LIMIT 10"))
    wrong_string = "SELECT * FROM users LIMIT 10"
    print(db.query(wrong_string))
    """
    #print(db.get_user_problems('dtc03003'))
    print(db.check_user('raar'))


if __name__ == "__main__":
=======
import os
import json
import requests
import time
from typing import Tuple, Optional, Dict, List
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
            # Is it best practice?
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
        result : Optional[Tuple]
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
        result = cur.fetchall()
        return result


    def get_problem_exp(self, problem_id: int) -> Tuple:
        """Returns corresponding problem's id and exp, empty tuple if not exist.

        Parameters
        --------------------
        problem_id : int
            problem id of target problem
        """
        return self.query(f'SELECT * FROM problem WHERE id={problem_id}')


    def get_problem_tags(self, problem_id: int) -> Optional[Dict]:
        """Returns tags, exp of corresponding problem

        It returns dictionary of corresponding problem.

        Parameters
        --------------------
        problem_id : int
            problem id of target problem
        
        Returns
        --------------------
        result : Dict
            If there's no corresponding problem, it's empty dictoionary
            result has this format {"exp" : int, "tags" : List[int]}
            exp is problem's exp, problem is not ratable or unrated, exp is zero
            tags is list of tag id. it can be empty
        """
        problem_info = self.get_problem_exp(problem_id)
        if bool(problem_info) is False: # empty row
            return None

        result = {'exp' : problem_info[0]['exp']}
        result['tags'] = list()
        if result['exp'] == 0:
            return result

        query_string = f'\
            SELECT tag_id \
            FROM problem join problem_tag on problem.id = problem_tag.problem_id \
            WHERE problem.id = {problem_id}'
        temp = self.query(query_string)
        for row in temp:
            result['tags'].append(row['tag_id'])
        return result


    def get_user_tags(self, handle: str) -> Optional[Dict]:
        """Returns exp of each tags user solved.

        Parameters
        --------------------
        handle : str
            user handle

        Returns
        --------------------
        result : Optional[Dict]
            exp of tags user solved. It has only tag with exp > 0. 
            Format : { tag_id[int] : exp_sum[int] }
            It is None if there's no such user.
            
        """
        if not self.check_user(handle):
            return None
        query_string = f'\
            SELECT SUM(exp) as exp_sum, tag_id \
            FROM ( \
                SELECT t2.id, exp \
                FROM ( \
                    SELECT problem_id \
                    FROM user join ac ON user.id = ac.user_id \
                    WHERE user.handle = \'{handle}\' \
                ) AS t1 JOIN problem AS t2 ON t1.problem_id = t2.id \
            ) AS p1 join problem_tag AS p2 ON p1.id = p2.problem_id \
            GROUP BY tag_id \
            ORDER BY exp_sum DESC'
        query_res = self.query(query_string)
        result = dict()
        for row in query_res:
            tag_id = row['tag_id']
            exp_sum = row['exp_sum']
            result[tag_id] = int(exp_sum)
        return result
    
    def get_user_problems(self, handle: str) -> Optional[List[int]]:
        """Returns list of problems user solved
        
        Parameters
        --------------------
        handle : str
            user handle

        Returns
        --------------------
        result : Optional[List[int]]
            list of the number of problems user solved.
            It is None if there's no such user.
        """
        if not self.check_user(handle):
            return None
        query_string=f'\
            SELECT problem_id \
            FROM user join ac on user.id = ac.user_id \
            WHERE user.handle = \'{handle}\' '
        query_res = self.query(query_string)
        result = [row['problem_id'] for row in query_res]
        
        return result
    
    def topk_problems(self, handle: str, k: int) :
        """Returns list of top k problems user solved.
        """
        if not self.check_user(handle):
            return None
        query_string=f'\
            SELECT problem.id, problem.tier, problem.exp\
            FROM ( \
                SELECT problem_id \
                FROM user join ac on user.id = ac.user_id \
                WHERE user.handle = \'{handle}\' \
               ) AS t1 join problem on problem.id = t1.problem_id \
            ORDER BY tier DESC \
            LIMIT {k}'
            
        query_res = self.query(query_string)
        result = [row for row in query_res]
        
        return result

    
    def check_user_problem(self, handle: str, problem_id: int) -> bool:
        """Returns True if user solved problem_id, False if not.

        Parameters
        --------------------
        handle : str
            user handle
        problem_id : int
            target problem id

        Returns
        --------------------
        True if user with handle solved problem_id, False if not.
        """
        query_string = f'\
            SELECT * \
            FROM ac \
            WHERE user_id in (SELECT id FROM user WHERE handle=\'{handle}\') and problem_id={problem_id}'
        res = self.query(query_string)
        return bool(res)

    
    def check_user(self, handle: str) -> bool:
        """Returns True if user with handle exists in DB, False if not

        Parameters
        --------------------
        handle : str
            user handle

        Returns
        --------------------
        True if user with handle exists in DB, False if not. 
        """
        query_string = f'\
            SELECT * \
            FROM user \
            WHERE handle = \'{handle}\''
        res = self.query(query_string)
        return bool(res)        

def main():
    db = DBHelper()
    """
    print(db.query("SELECT * FROM user LIMIT 10"))
    # Should work if connection has been closed.
    db.connection.close()
    print(db.query("SELECT * FROM tag LIMIT 10"))
    wrong_string = "SELECT * FROM users LIMIT 10"
    print(db.query(wrong_string))
    """
    #print(db.get_user_problems('dtc03003'))
    print(db.check_user('raar'))


if __name__ == "__main__":
>>>>>>> Stashed changes
    main()
from utils import DBHelper
db = DBHelper('./.mylogin.cnf')
query_string = 'SELECT * FROM user WHERE handle = \'seastar105\''
print(db.query(query_string))

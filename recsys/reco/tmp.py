import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils import DBHelper
db=DBHelper('.mylogin.cnf')
print(db.get_problem_tags(1000))

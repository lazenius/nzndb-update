import pymysql
import urllib.request as req
import json
from include.common import *

seq = '174'

jdata = get_jobInfo(seq)

# print_formJson(jdata)
print(jdata['baseInfo'])
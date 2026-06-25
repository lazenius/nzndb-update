import pymysql
import urllib.request as req
from bs4 import BeautifulSoup
from include.common import *

svcCode = 'MAJOR'
gubun = 'univ_list' # 학교분류(필수)
# 고등학교 : high_list, 56개, lc: 6 fn: 1046 ms: 2 mc: 8
# 대학교 : univ_list, 501개, lc: 5 fn: 2196 ms: 5 mc: 13
subject = '' # 학과 계열

# 학과 계열
subject_list = {"100391":"인문계열", "100392":"사회계열", "100393":"교육계열", "100394":"공학계열", "100395":"자연계열", "100396":"의약계열", "100397":"예체능계열",}
reversed_subject = {value: key for key, value in subject_list.items()}

full_url = school_xml_url + '?&apiKey=' + apiKey + '&svcType=api' + '&svcCode=' + svcCode + '&contentType=' + contentType + '&gubun=' + gubun + '&subject=' + subject

f = req.urlopen(full_url + '&thisPage=1&perPage=1000')
soup = BeautifulSoup(f, 'xml')
# print(soup)
# print(soup.prettify())

num = 0

# lClass_max = 0
# facilName_max = 0
# majorSeq_max = 0
# mClass_max = 0

cur = con.cursor()

for n in soup.find_all('content'):
    # break
    # print(n)
    num += 1
    # print(num)

    school = gubun.replace('_list', '')

    # print("lClass:", n.lClass.text) # 계열
    faculty = reversed_subject[n.lClass.text] if n.lClass.text in reversed_subject else n.lClass.text
    # print("facilName:", n.facilName.text) # 세부학과명
    others = n.facilName.text
    # print("majorSeq:", n.majorSeq.text) # 학과코드
    seq = n.majorSeq.text
    # print("mClass:", n.mClass.text) # 학과(명)
    name = n.mClass.text
    # print("totalCount:", n.totalCount.text)
    # print("--" * 20)

    # lClass_max = max(lClass_max, len(n.lClass.text))
    # facilName_max = max(facilName_max, len(n.facilName.text))
    # majorSeq_max = max(majorSeq_max, len(n.majorSeq.text))
    # mClass_max = max(mClass_max, len(n.mClass.text))

    query = f"INSERT INTO CAREER_DB.subject_list (school, seq, name, faculty, others, recv_time) VALUES ('{school}', '{seq}', '{name}', '{faculty}', '{others}', NOW()) on duplicate key update name='{name}', faculty='{faculty}', others='{others}', recv_time=NOW()"

    # print(query)
    cur.execute(query)

con.commit()
con.close()

# print("lc:", lClass_max, "fn:", facilName_max, "ms:", majorSeq_max, "mc:", mClass_max)

# create table CAREER_DB.subject_list (
#     school char(4) not null default '',
#     seq int unsigned not null default 0,
#     name varchar(30) not null default '',
#     faculty char(6) not null default '',
#     others varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(school, seq),
#     key(name)
# );

# 고등학교
# lClass: 기타
# facilName: 환경과, 환경산업과, 도시공간개발과, 도시환경과, 발명환경공업과
# majorSeq: 41
# mClass: 환경
# totalCount: 56

# 대학교
# lClass: 사회계열
# facilName: e-경영학전공,e-비즈니스학과,e비즈니스학과,e비즈니스학전공,IT비즈니스학과,디지털비즈니스학과,전자상거래학과
# majorSeq: 666
# mClass: e-비즈니스학과
# totalCount: 501
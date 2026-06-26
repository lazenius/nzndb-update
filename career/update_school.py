import pymysql
import urllib.request as req
from bs4 import BeautifulSoup
from include.common import *

svcCode = 'SCHOOL' # 서비스코드(필수)
gubun = 'high_list' # 학교분류(필수)
# 초등학교 : elem_list, 6327개 cn: 0 ci: 0 st: 0 sg: 0 ln: 70 ad: 122 sn: 17 rg: 7 et: 2
# 중학교 : midd_list, 3284개 cn: 0 ci: 0 st: 0 sg: 0 ln: 68 ad: 55 sn: 21 rg: 7 et: 2
# 고등학교 : high_list, 2382개 cn: 0 ci: 0 st: 5 sg: 5 ln: 56 ad: 63 sn: 24 rg: 7 et: 2
# 대학교 : univ_list, 475개 cn: 5 ci: 0 st: 9 sg: 7 ln: 51 ad: 46 sn: 21 rg: 7 et: 2
# 특수학교 : seet_list, 197개 cn: 0 ci: 0 st: 0 sg: 0 ln: 50 ad: 48 sn: 9 rg: 7 et: 2
# 기타 : alte_list	510개 cn: 0 ci: 0 st: 0 sg: 0 ln: 202 ad: 110 sn: 30 rg: 7 et: 8

region = '' # 지역
sch1 = '' # 학교유형1
sch2 = '' # 학교유형2
est = '' # 설립유형
# 대학교 : 국립, 사립, 공립
# 대안학교 : 인가, 비인가, 위탁형

# 학교
school_list = {"elem":"초등학교", "midd":"중학교", "high":"고등학교", "univ":"대학교", "seet":"특수학교", "alte":"기타"}

# 지역
region_list	= {"100260":"서울특별시", "100267":"부산광역시", "100269":"인천광역시", "100271":"대전광역시", "100272":"대구광역시", "100273":"울산광역시","100275":"광주광역시", "100276":"경기도", "100278":"강원특별자치도", "100280":"충청북도", "100281":"충청남도", "100282":"전북특별자치도", "100283":"전라남도", "100285":"경상북도", "100291":"경상남도", "100292":"제주도",}
reversed_region = {value: key for key, value in region_list.items()}
# "전라북도" -> "전북특별자치도" 변경

# 학교유형1
sch1_list = {"100362":"일반고", "100363":"특성화고", "100364":"특수목적고", "100365":"자율고", "100366":"기타", "100322":"전문대학", "100323":"대학(4년제)",}
reversed_sch1 = {value: key for key, value in sch1_list.items()}

# 학교유형2
sch2_list = {"104228":"일반고", "100368":"대안교육", "100369":"직업교육", "100370":"기타", "100371":"과학계열", "100372":"외국어국제계열", "100373":"예술체육계열", "100374":"마이스터고", "100375":"자율형사립", "100376":"자율형공립", "100377":"영재학교", "100324":"전문대학", "100325":"기능대학", "100326":"사이버대학(2년제)", "100327":"각종대학(전문)", "100328":"일반대학", "100329":"교육대학", "100330":"산업대학", "100331":"사이버대학(대학)", "100332":"각종대학(대학)",}
# "기능대학(폴리텍대학)" -> "기능대학" 변경
# "사이버대학(4년제)" -> "사이버대학(대학)" 변경
reversed_sch2 = {value: key for key, value in sch2_list.items()}

# 설립유형
estType = {"100334":"국립", "100335":"사립", "100336":"공립",}
reversed_est = {value: key for key, value in estType.items()}

full_url = school_xml_url + '?&apiKey=' + apiKey + '&svcType=api' + '&svcCode=' + svcCode + '&contentType=' + contentType + '&gubun=' + gubun + '&region=' + region + '&sch1=' + sch1 + '&sch2=' + sch2 + '&est=' + est

f = req.urlopen(full_url + '&thisPage=1&perPage=10000')
soup = BeautifulSoup(f, 'xml')
# print(soup)
# print(soup.prettify())



num = 0

cur = con.cursor()

for n in soup.find_all('content'):
    num += 1

    campus = ''
    info = ''
    sch1 = ''
    sch2 = ''

    school = gubun.replace('_list', '')

    if gubun == 'univ_list': 
        campus = n.campusName.text
        info = n.collegeinfourl.text

    if gubun == 'univ_list' or gubun == 'high_list': 
        sch2 = reversed_sch2[n.schoolType.text] if n.schoolType.text in reversed_sch2 else n.schoolType.text
        sch1 = reversed_sch1[n.schoolGubun.text] if n.schoolGubun.text in reversed_sch1 else n.schoolGubun.text

    # print(n.schoolType.text)

    link = n.link.text
    address = n.adres.text
    name = n.schoolName.text
    region = reversed_region[n.region.text] if n.region.text in reversed_region else n.region.text
    est = reversed_est[n.estType.text] if n.estType.text in reversed_est else n.estType.text
    seq = n.seq.text

    query = f"INSERT INTO CAREER_DB.school_list (school, seq, name, campus, sch1, sch2, region, est, address, link, info, recv_time) VALUES ('{school}', '{seq}', '{name}', '{campus}', '{sch1}', '{sch2}', '{region}', '{est}', '{address}', '{link}', '{info}', NOW()) on duplicate key update name='{name}', campus='{campus}', sch1='{sch1}', sch2='{sch2}', region='{region}', est='{est}', address='{address}', link='{link}', info='{info}', recv_time=NOW()"

    # print(query)
    cur.execute(query)

con.commit()
con.close()

# create table CAREER_DB.school_list (
#     school char(4) not null default '',
#     seq int unsigned not null default 0,
#     name varchar(50) not null default '',
#     campus varchar(50) not null default '',
#     sch1 char(6) not null default '',
#     sch2 char(6) not null default '',
#     region char(6) not null default '',
#     est char(6) not null default '',
#     address varchar(200) not null default '',
#     link varchar(300) not null default '',
#     info varchar(300) not null default '',
#     recv_time DATETIME not null,
#     primary key(school, seq),
#     key(name)
# );

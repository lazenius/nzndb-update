import pymysql
import urllib.request as req
import json
from include.common import *

# 적성유형
apt_list = {"104718":"운동 관련직", "104719":"무용 관련직", "104720":"안전 관련직", "104721":"일반운전 관련직", "104722":"기능직", "104723":"의복제조 관련직", "104724":"조리 관련직", "104725":"이미용 관련직", "104726":"기타 게임·오락·스포츠 관련직", "104727":"고급 운전 관련직", "104728":"공학 기술직", "104729":"공학 전문직", "104730":"음악 관련직", "104731":"악기 관련직", "104732":"연기 관련직", "104733":"웹·게임·애니메이션 관련직", "104734":"미술 및 공예 관련직", "104735":"기타 특수 예술직", "104736":"사회서비스직", "104737":"인문계 교육 관련직", "104738":"이공계 교육 관련직", "104739":"의료관련 전문직", "104740":"IT 관련전문직", "104741":"금융 및 경영 관련직", "104742":"인문 및 사회과학 관련직", "104743":"회계 관련직", "104744":"언어 관련 전문직", "104745":"작가 관련직", "104746":"교육관련 서비스직", "104747":"기획서비스직", "104748":"매니지먼트 관련직", "104749":"보건의료 관련 서비스직", "104750":"사무 관련직", "104751":"영업관련 서비스직", "104752":"일반 서비스직", "104753":"디자인 관련직", "104754":"영상 관련직", "104755":"예술기획 관련직", "104756":"자연친화 관련직", "104757":"농생명산업 관련직", "104758":"환경관련 전문직", "104759":"법률 및 사회활동 관련직", "104760":"이학 전문직", }
reversed_apt = {value: key for key, value in apt_list.items()}  

# 직업분류
cat_list = {"0":"경영·사무·금융·보험직", "1":"연구직 및 공학 기술직", "2":"교육·법률·사회복지·경찰·소방직 및 군인", "3":"보건·의료직", "4":"예술·디자인·방송·스포츠직", "5":"미용·여행·숙박·음식·경비·청소직", "6":"영업·판매·운전·운송직", "7":"건설·채굴직", "8":"설치·정비·생산직", "9":"농림어업직"}
reversed_cat = {value: key for key, value in cat_list.items()}


# searchThemeCode = ''
# searchAptdCodes = ''
# searchJobCd = ''

# full_url = jobs_json_url + '?&apiKey=' + apiKey + '&searchThemeCode=' + searchThemeCode  + '&searchAptdCodes=' + searchAptdCodes + '&searchJobCd=' + searchJobCd

# f = req.urlopen(full_url + '&pageIndex=3&pageSize=1000')
# data = f.read().decode('utf-8')
# json_data = json.loads(data)

# print(json_data)
# formatted_json_data = json.dumps(json_data, indent=4, ensure_ascii=False)
# print(formatted_json_data)

page = 1
num = 1

cur = con.cursor()

while(page < 100):
    json_data = get_jobList(page, searchThemeCode='', searchAptdCodes='', searchJobCd='')

    if len(json_data['jobs']) == 0:
        break

    for job in json_data['jobs']:
        print('-----------------------------------')
        
        jcode = job['job_cd']
        print('#', num, jcode)

        jdata = get_jobInfo(jcode)
        # print_formJson(jdata)
        # print(jdata['baseInfo'])

        code = jdata['baseInfo'].get('job_cd', '') # 직업코드
        name = jdata['baseInfo'].get('job_nm', '') # 직업명
        std_code = jdata['baseInfo'].get('std_job_cd', '') # 표준직업코드
        std_name = jdata['baseInfo'].get('std_job_nm', '') # 표준직업명
        emp_code = jdata['baseInfo'].get('emp_job_cd', '') # 고용코드
        emp_name = jdata['baseInfo'].get('emp_job_nm', '') # 고용코드명
        apt_name = jdata['baseInfo'].get('aptit_name', '') # 적성유형
        apt_code = reversed_apt[apt_name] if apt_name in reversed_apt else apt_name # 적성유형코드
        related_job = jdata['baseInfo'].get('rel_job_nm', '') # 관련직업
        social = jdata['baseInfo'].get('social', '') # 사회공헌
        balance = jdata['baseInfo'].get('wlb', '') # 워라벨
        satisfication = float(jdata['baseInfo'].get('satisfication', '0')) # 직업만족도
        wage = int(jdata['baseInfo'].get('wage', '0').replace(',', '')) # 평균연봉
        edit_date = jdata['baseInfo'].get('edit_dt', '') # 수정일
        reg_date = jdata['baseInfo'].get('reg_dt', '') # 작성일
        views = jdata['baseInfo'].get('views', '') # 조회수
        likes = jdata['baseInfo'].get('likes', '') # 추천수
        tag = jdata['baseInfo'].get('tag', '') # 태그

        query = f"INSERT INTO CAREER_DB.job_list (code, name, std_code, emp_code, apt_code, related_job, social, balance, satisfication, wage, edit_date, reg_date, views, likes, tag, recv_time) VALUES ('{code}', '{name}', '{std_code}', '{emp_code}', '{apt_code}', '{related_job}', '{social}', '{balance}', '{satisfication}', '{wage}', '{edit_date}', '{reg_date}', '{views}', '{likes}', '{tag}', NOW()) on duplicate key update name='{name}', std_code='{std_code}', emp_code='{emp_code}', apt_code='{apt_code}', related_job='{related_job}', social='{social}', balance='{balance}', satisfication='{satisfication}', wage='{wage}', edit_date='{edit_date}', reg_date='{reg_date}', views='{views}', likes='{likes}', tag='{tag}', recv_time=NOW()"
        print(query)
        
        std_query = f"INSERT INTO CAREER_DB.code_list (code, name, recv_time) VALUES ('{std_code}', '{std_name}', NOW()) on duplicate key update name='{std_name}', recv_time=NOW()"
        print(std_query)
        
        emp_query = f"INSERT INTO CAREER_DB.code_list (code, name, recv_time) VALUES ('{emp_code}', '{emp_name}', NOW()) on duplicate key update name='{emp_name}', recv_time=NOW()"
        print(emp_query)

        # break
        cur.execute(query)
        cur.execute(std_query)
        cur.execute(emp_query)
        num += 1

    # break
    page += 1
    
con.commit()
con.close()


# create table CAREER_DB.job_list (
#     code int unsigned not null default 0,
#     name varchar(100) not null default '',
#     std_code char(6) not null default '',
#     emp_code char(6) not null default '',
#     apt_code char(6) not null default '',
#     thm_code char(6) not null default '',
#     cat_code char(6) not null default '',
#     related_job varchar(300) not null default '',
#     social varchar(10) not null default '',
#     balance varchar(10) not null default '',
#     satisfication decimal(4,1) unsigned not null default 0,
#     wage int unsigned not null default 0,
#     edit_date DATE not null default '0000-00-00',
#     reg_date DATE not null default '0000-00-00',
#     views int unsigned not null default 0,
#     likes int unsigned not null default 0,
#     tag varchar(300) not null default '',
#     recv_time DATETIME not null,
#     primary key(code),
#     key(name),
#     key(apt_code),
#     key(thm_code),
#     key(cat_code)
# );

# create table CAREER_DB.job_work_list (
#     jcode int unsigned not null default 0,
#     work varchar not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(work)
# );

# create table CAREER_DB.interest_list (
#     jcode int unsigned not null default 0,
#     interest varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(interest)
# );

# create table CAREER_DB.research_list (
#     jcode int unsigned not null default 0,
#     research varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(research)
# );

# create table CAREER_DB.job_ready_list (
#     jcode int unsigned not null default 0,
#     recruit varchar(3000) not null default '',
#     certificate varchar(3000) not null default '',
#     training varchar(3000) not null default '',
#     curriculum varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(recruit)
# );

# create table CAREER_DB.forecast_list (
#     jcode int unsigned not null default 0,
#     forecast varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(forecast)
# );

# create table CAREER_DB.edu_chart (
#     jcode int unsigned not null default 0,
#     chart_name varchar(50) not null default '',
#     chart_data varchar(50) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(chart_name)
# );

# create table CAREER_DB.perform_list (
#     jcode int unsigned not null default 0,
#     environment varchar(3000) not null default '',
#     perform varchar(3000) not null default '',
#     knowledge varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(environment)
# );

# create table CAREER_DB.major_chart (
#     jcode int unsigned not null default 0,
#     major varchar(50) not null default '',
#     major_data varchar(50) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(major)
# );

# create table CAREER_DB.ability_list (
#     jcode int unsigned not null default 0,
#     SORT_ORDR char(6) not null default '',
#     ability_name varchar(50) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(ability_name)
# );

# create table CAREER_DB.depart_list (
#     jcode int unsigned not null default 0,
#     depart_id int unsigned not null default 0,
#     depart_name varchar(50) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode, depart_id),
#     key(depart_name)
# );

# create table CAREER_DB.rel_sol_list (
#     jcode int unsigned not null default 0,
#     rel_sol varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(rel_sol)
# );

# create table CAREER_DB.tag_list (
#     jcode int unsigned not null default 0,
#     tag varchar(50) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(tag)
# );

# create table CAREER_DB.certi_list (
#     jcode int unsigned not null default 0,
#     certi varchar(50) not null default '',
#     LINK varchar(300) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(certi)
# );

# create table CAREER_DB.rel_video_list (
#     jcode int unsigned not null default 0,
#     video_name varchar(50) not null default '',
#     THUMBNAIL_FILE_SER int unsigned not null default 0,
#     OUTPATH3 varchar(300) not null default '',
#     video_id int unsigned not null default 0,
#     CID int unsigned not null default 0,
#     recv_time DATETIME not null,
#     primary key(jcode, video_id),
#     key(video_name)
# );

# create table CAREER_DB.aptitude_list (
#     jcode int unsigned not null default 0,
#     aptitude varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(aptitude)
# );

# create table CAREER_DB.job_rel_org_list (
#     jcode int unsigned not null default 0,
#     rel_org varchar(50) not null default '',
#     rel_org_url varchar(300) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(rel_org)
# );

# create table CAREER_DB.rel_jinsol_list (
#     jcode int unsigned not null default 0,
#     rel_jinsol varchar(3000) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(rel_jinsol)
# );

# create table CAREER_DB.indicator_chart (
#     jcode int unsigned not null default 0,
#     indicator varchar(50) not null default '',
#     indicator_data varchar(50) not null default '',
#     source varchar(300) not null default '',
#     recv_time DATETIME not null,
#     primary key(jcode),
#     key(indicator)
# );
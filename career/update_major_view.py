import pymysql
import urllib.request as req
import re
from bs4 import BeautifulSoup
from include.common import *

def print_content(n, tag_name, subtags):
    t = n.find(tag_name)
    for s in t.find_all('content'):
        for subtag in subtags:
            try:
                text = s.find(subtag).text
                if len(text):
                    print(f"- {subtag}:", text)
            except AttributeError:
                pass

svcCode = 'MAJOR_VIEW'
gubun = 'univ_list' # 학교분류(필수)
# 고등학교 : high_list
# 대학교 : univ_list
majorSeq = 8

full_url = school_xml_url + '?&apiKey=' + apiKey + '&svcType=api' + '&svcCode=' + svcCode + '&contentType=' + contentType + '&gubun=' + gubun + '&majorSeq=' + str(majorSeq)

f = req.urlopen(full_url + '&thisPage=1&perPage=1000')
soup = BeautifulSoup(f, 'xml')
# print(soup)
print(soup.prettify())
exit()

school = gubun.replace('_list', '') # school : 학교분류 x

if school == 'high':
    n = soup.find('content')

    if n.major is None:
        exit()

    print(f"- major: {n.major.text} ({majorSeq})", ) # 학과명 x
    print("- department:", n.department.text) # 세부관련학과 x
    print("- summary:", n.summary.text) # 학과개요
    print("- purpose:", n.purpose.text) # 주요교육내용
    print("- interest:", n.interest.text) # 흥미와 적성
    print("- relatedjob:", n.relatedjob.text) # 진출분야 및 관련 직업

    print("\n[설치학교]")
    for s in n.setshl.find_all('content'):
        print(s.schoolName.text)
        print("\t", s.area.text)
        print("\t", s.schoolURL.text)
        print("\t", s.majorName.text)

    print("\n[졸업자 현황]")
    for s in n.graduation_gender.find_all('content'):
        item = s.IEM.text
        data = s.DATA.text
        print(item, data)

else:
    n = soup.find('content')

    if n.major is None:
        exit()

    print(f"- major(학과명): {n.major.text} ({majorSeq})", ) # 학과명 x
    print("- salary(졸업 후 직장임금):", n.salary.text) # 졸업 후 직장임금
    salary = n.salary.text
    # print("- employment:", n.employment.text) # 취업률
    employment = re.search(r'[0-9]+[.]*[0-9]*', n.employment.text).group(0)
    print(f"- employment(취업률): {employment}", ) # 취업률
    print("- department(세부관련학과):", n.department.text) # 세부관련학과 x
    print("- summary(학과개요):", n.summary.text) # 학과개요
    summary = n.summary.text
    print("- job(관련직업)):", n.job.text) # 관련직업
    job = n.job.text
    print("- qualifications(관련자격):", n.qualifications.text) # 관련자격
    qualifications = n.qualifications.text
    print("- interest(흥미와 적성):", n.interest.text) # 흥미와 적성
    interest = n.interest.text
    print("- property(학과특성):", n.property.text) # 학과특성
    property = n.property.text

    print_content(n, 'relate_subject', ['subject_name', 'subject_description'])
    print_content(n, 'career_act', ['act_name', 'act_description'])
    print_content(n, 'enter_field', ['gradeuate', 'description'])
    print_content(n, 'main_subject', ['SBJECT_NM', 'SBJECT_SUMRY'])

    # print("\n[관련 고교 교과목]")
    # for s in n.relate_subject.find_all('content'):
    #     if len(s.subject_description.text):
    #         print("- name:", s.subject_name.text)
    #         print("- description:", s.subject_description.text)
    
    # print("\n[진로 탐색 활동]")
    # for s in n.career_act.find_all('content'):
    #     if len(s.act_description.text):
    #         print("- name:", s.act_name.text)
    #         print("- description:", s.act_description.text)

    # print("\n[졸업 후 진출분야]")
    # for s in n.enter_field.find_all('content'):
    #     if len(s.description.text):
    #         print("- gradeuate:", s.gradeuate.text)
    #         print("- description:", s.description.text)

    # print("\n[대학 주요 교과목]")
    # for s in n.main_subject.find_all('content'):
    #     if len(s.SBJECT_SUMRY.text):
    #         print("- NM:", s.SBJECT_NM.text)
    #         print("- SUMRY:", s.SBJECT_SUMRY.text)

    print("\n[개설대학]")
    for s in n.university.find_all('content'):
        print(s.schoolName.text)
        print("\t", s.area.text)
        print("\t", s.schoolURL.text)
        print("\t", s.campus_nm.text)
        print("\t", s.majorName.text)

    print("\n[입학상황]")
    for s in n.chartData.applicant.find_all('content'):
        item = s.find('item').text
        data = s.find('data').text
        name = s.find('name').text
        print(item, data)

    print("\n[입학상황(성별)]")
    for s in n.chartData.gender.find_all('content'):
        item = s.find('item').text
        data = s.find('data').text
        name = s.find('name').text
        print(item, data)

    print("\n[취업률]")
    for s in n.chartData.employment_rate.find_all('content'):
        item = s.find('item').text
        data = s.find('data').text
        name = s.find('name').text
        print(item, data)

    print("\n[졸업 후 첫 취업 분야]")
    for s in n.chartData.field.find_all('content'):
        item = s.find('item').text
        data = s.find('data').text
        name = s.find('name').text
        print(item, data)

    print("\n[졸업 후 첫 직장 월평균 임금]")
    for s in n.chartData.avg_salary.find_all('content'):
        item = s.find('item').text
        data = s.find('data').text
        name = s.find('name').text
        print(item, data)

    print("\n[첫 직장 만족도]")
    for s in n.chartData.satisfaction.find_all('content'):
        item = s.find('item').text
        data = s.find('data').text
        name = s.find('name').text
        print(item, data)

    print("\n[졸업 후 상황]")
    for s in n.chartData.after_graduation.find_all('content'):
        item = s.find('item').text
        data = s.find('data').text
        name = s.find('name').text
        print(item, data)

    print("\n[특성(성별비율)-많이본)]")
    for s in n.GenCD.popular.find_all('content'):
        pcnt = s.find('PCNT').text
        name = s.find('GEN_NM').text
        print(name, pcnt)

    print("\n[특성(성별비율)-관심직업)]")
    for s in n.GenCD.bookmark.find_all('content'):
        pcnt = s.find('PCNT').text
        name = s.find('GEN_NM').text
        print(name, pcnt)

    print("\n[특성(학교급별비율)-많이본)]")
    for s in n.SchClass.popular.find_all('content'):
        pcnt = s.find('PCNT').text
        name = s.find('SCH_CLASS_NM').text
        print(name, pcnt)

    print("\n[특성(학교급별비율)-관심직업)]")
    for s in n.SchClass.bookmark.find_all('content'):
        pcnt = s.find('PCNT').text
        name = s.find('SCH_CLASS_NM').text
        print(name, pcnt)

    print("\n[특성(중학생적성유형)-많이본)]")
    for s in n.lstMiddleAptd.popular.find_all('content'):
        rank = s.find('RANK').text
        order = s.find('CD_ORDR').text
        name = s.find('CD_NM').text
        print(name, rank, order)

    print("\n[특성(중학생적성유형)-관심직업)]")
    for s in n.lstMiddleAptd.bookmark.find_all('content'):
        rank = s.find('RANK').text
        order = s.find('CD_ORDR').text
        name = s.find('CD_NM').text
        print(name, rank, order)

    print("\n[특성(고등학생적성유형)-많이본)]")
    for s in n.lstHighAptd.popular.find_all('content'):
        rank = s.find('RANK').text
        order = s.find('CD_ORDR').text
        name = s.find('CD_NM').text
        print(name, rank, order)

    print("\n[특성(고등학생적성유형)-관심직업)]")
    for s in n.lstHighAptd.bookmark.find_all('content'):
        rank = s.find('RANK').text
        order = s.find('CD_ORDR').text
        name = s.find('CD_NM').text
        print(name, rank, order)

    print("\n[특성(선호직업가치)-많이본)]")
    for s in n.lstVals.popular.find_all('content'):
        rank = s.find('RANK').text
        order = s.find('CD_ORDR').text
        name = s.find('CD_NM').text
        print(name, rank, order)

    print("\n[특성(선호직업가치)-관심직업)]")
    for s in n.lstVals.bookmark.find_all('content'):
        rank = s.find('RANK').text
        order = s.find('CD_ORDR').text
        name = s.find('CD_NM').text
        print(name, rank, order)

    print("--" * 20)


# 대학정보 테이블 (university)
# 학교 정보를 저장할 테이블로서, 학교명, 지역, 캠퍼스명, 학교 URL 등의 정보를 포함합니다.
# CREATE TABLE university (
#     university_id INT AUTO_INCREMENT PRIMARY KEY,
#     school_name VARCHAR(255),
#     area VARCHAR(50),
#     campus_name VARCHAR(50),
#     school_url VARCHAR(255)
# );

# 전공정보 테이블 (major)
# 학과 정보를 저장할 테이블로서, 학과명과 해당하는 학교의 ID를 참조합니다.
# CREATE TABLE major (
#     major_id INT AUTO_INCREMENT PRIMARY KEY,
#     major_name VARCHAR(255),
#     university_id INT,
#     FOREIGN KEY (university_id) REFERENCES university(university_id)
# );

# 학과 상세 정보 테이블 (major_detail)
# 학과에 대한 상세 정보를 저장할 테이블로서, 학과명, 평균연봉, 취업률 등의 정보를 포함합니다.
# CREATE TABLE major_detail (
#     major_detail_id INT AUTO_INCREMENT PRIMARY KEY,
#     major_id INT,
#     salary FLOAT,
#     employment_rate FLOAT,
#     qualifications TEXT,
#     job_opportunities TEXT,
#     interest TEXT,
#     properties TEXT,
#     FOREIGN KEY (major_id) REFERENCES major(major_id)
# );

# 학과 관련 과목 테이블 (related_subject)
# 학과와 관련된 과목 정보를 저장할 테이블로서, 과목명과 과목 설명을 포함합니다.
# CREATE TABLE related_subject (
#     subject_id INT AUTO_INCREMENT PRIMARY KEY,
#     major_id INT,
#     subject_name VARCHAR(255),
#     subject_description TEXT,
#     FOREIGN KEY (major_id) REFERENCES major(major_id)
# );

# 입학 상황 테이블 (admission_status)
# 학과의 입학 상황 정보를 저장할 테이블로서, 지원자 수, 입학자 수 등의 정보를 포함합니다.
# CREATE TABLE admission_status (
#     status_id INT AUTO_INCREMENT PRIMARY KEY,
#     major_id INT,
#     applicants INT,
#     enrollments INT,
#     FOREIGN KEY (major_id) REFERENCES major(major_id)
# );

# 취업 상황 테이블 (employment_status)
# 졸업 후 취업 상황 정보를 저장할 테이블로서, 취업률, 첫 직장 만족도 등의 정보를 포함합니다.
# CREATE TABLE employment_status (
#     employment_id INT AUTO_INCREMENT PRIMARY KEY,
#     major_id INT,
#     employment_rate FLOAT,
#     job_satisfaction VARCHAR(50),
#     avg_salary FLOAT,
#     first_job_field VARCHAR(255),
#     FOREIGN KEY (major_id) REFERENCES major(major_id)
# );

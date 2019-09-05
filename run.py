import re
import pymysql
import logging
from lxml import etree
from pipelines import MySQLPipeLine
from requests_login import requests_login

week_choice = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def get_term_list(session):
    r = session.post('http://54.222.196.251:81/yjlgxy_jsxsd/xskb/xskb_list.do')
    html_tree = etree.HTML(r.text)
    term_list = html_tree.xpath('//*[@id="xnxq01id"]/option/text()')[:9]
    return [str(i) for i in term_list]


def parse(session):
    # 获取所有学期
    term_list = get_term_list(session)
    for term in term_list:
        # print(f'开始爬取{term}学期的课程表')
        for zc in range(1, 31):
            # print(f'开始爬取第{zc}周的课程表')
            data = [('zc', str(zc)), ('xnxq01id', term)]
            r = session.post('http://54.222.196.251:81/yjlgxy_jsxsd/xskb/xskb_list.do', data=data)
            html_tree = etree.HTML(r.text)
            flag = html_tree.xpath('//*[@id="kbtable"]//tr[3]/th/text()')
            # flag为[],则该学期课表为空
            if not flag:
                break
            # 学号
            student_id = re.findall('\d+', str(html_tree.xpath('//*[@id="Top1_divLoginName"]/text()')[0]))[0]
            # 学期
            semester = data[1][1]
            # 周次
            weekly_times = int(data[0][1])
            tr_list = html_tree.xpath('//table[@id="kbtable"]//tr')[1:-1]
            for i, tr in enumerate(tr_list):
                # 课时
                class_times = i + 1
                td_list = tr.xpath('./td')
                for j, td in enumerate(td_list):
                    # 星期几
                    week = week_choice[j]
                    curriculum = ''.join(td.xpath('./div[2]//text()'))
                    if curriculum.strip():
                        yield {
                            'student_id': student_id,
                            'semester': semester,
                            'weekly_times': weekly_times,
                            'week': week,
                            'class_times': class_times,
                            'curriculum': curriculum
                        }


def main():
    # db = pymysql.connect(host='127.0.0.1', user='root', password='Root@2018', port=3306, db='free_school')
    db = pymysql.connect(host='152.136.145.193', user='root', password='School@2018', port=3306, db='free_school')
    cursor = db.cursor()
    sql = "SELECT student_id,student_pwd FROM t_school_administration WHERE fresh_state = 0 and abnormal_state = 0 and school_code = 1 and usable_state = 0 GROUP BY student_id,student_pwd"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        session = requests_login(row[0], row[1])
        logging.info(f'开始爬取学号为{row[0]}的课程表')
        for res in parse(session):
            MySQLPipeLine.save_to_mysql(res)
        logging.info(f'学号为{row[0]}的课程表爬取完毕')
        cursor.execute("UPDATE t_school_administration SET fresh_state = 1 WHERE student_id = '%s'" % (row[0]))
        db.commit()
    db.close()


if __name__ == '__main__':
    main()

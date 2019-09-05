import pymysql


class MySQLPipeLine:
    @staticmethod
    def save_to_mysql(data):
        # db = pymysql.connect(host='127.0.0.1', user='root', password='Root@2018', port=3306, db='free_school')
        db = pymysql.connect(host='152.136.145.193', user='root', password='School@2018', port=3306, db='free_school')
        cursor = db.cursor()
        sql = 'INSERT INTO t_school_timetable(student_id, semester, weekly_times, week, class_times, curriculum) values(%s, %s, %s, %s, %s, %s)'
        try:
            if cursor.execute(sql, tuple(data.values())):
                db.commit()
        except:
            db.rollback()
        db.close()

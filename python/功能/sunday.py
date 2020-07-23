import calendar
import datetime

# print(datetime.date.today())


def get_current_week():
    monday, sunday = datetime.date.today(), datetime.date.today()
    one_day = datetime.timedelta(days=1)
    while monday.weekday() != 0:
        monday -= one_day
    while sunday.weekday() != 6:
        sunday += one_day
    # 返回当前的星期一和星期天的日期
    return str(monday), str(sunday)

s, m = get_current_week()
sql = 'select a.openid,SUM(a.wight) as allwight,b.wxname,b.id AS userid,b.user_img from Deliver as a \
                left JOIN userInfo as b on a.openid = b.openid \
                where a.create_time BETWEEN "{s}" and "{m}"  and b.wxname is not NULL \
                GROUP BY b.openid  \
                order BY allwight desc'.format(s=s, m=m)
print(sql)

from base.newdb import Smart_Mysql
from base.shop_base import callJson
import datetime

#每日一答
class Answer():

    def __init__(self, user_id):
        #登录态
        self.user_id = user_id
        self.dbCursor = None

    def checkLog(self, dbCursor=None):
        # 查询最新一条记录
        sql = f"SELECT * FROM tbActAnswerLog WHERE iUserId = {self.user_id} \
                ORDER BY dtCreateTime DESC LIMIT 1 FOR UPDATE"
        return Smart_Mysql.query(sql, dbCursor=dbCursor)

    def selQuestion(self, question_id, dbCursor=None):
        # 根据id查题目
        sql = f"SELECT * FROM tbActAnswer WHERE id = {question_id}"
        return Smart_Mysql.query(sql, dbCursor=dbCursor)

    def selAnswer(self, totalright, continueright, dbCursor=None):
        #处理题目
        data = Smart_Mysql.query("SELECT * FROM tbActAnswer WHERE NOT EXISTS ( \
                                SELECT iQuestionId FROM tbActAnswerLog WHERE \
                                tbActAnswerLog.iQuestionId = tbActAnswer.id \
                                AND iUserId = %s) ORDER BY RAND() LIMIT 1",
                                param=[self.user_id], dbCursor=dbCursor)
        question_id = data[0].get('id')
        Smart_Mysql.insert("INSERT INTO tbActAnswerLog SET iUserId=%s, \
                                    iQuestionId=%s, iAnswerIndex=-1, iRight=-1, \
                                    iTotalRight=%s, iContinueRight=%s",
                                param=[self.user_id,
                                        question_id,
                                        totalright,
                                        continueright], dbCursor=dbCursor)
        return data[0]

    def upAnswer(self, question_id, answerindex, right, totalright, continueright, dbCursor=None):
        return Smart_Mysql.update("UPDATE tbActAnswerLog SET iQuestionId=%s, \
                                    iAnswerIndex=%s, iRight=%s, \
                                    iTotalRight=%s, iContinueRight=%s \
                                    WHERE iUserId=%s",
                                param=[question_id,
                                        answerindex,
                                        right,
                                        totalright,
                                        continueright,
                                        self.user_id], dbCursor=dbCursor)

    def get_answer(self):
        # 取得今日题目
        conn, cursor = Smart_Mysql.getConn()
        log = self.checkLog(dbCursor=cursor)
        result = ''
        if log:
            answer = log[0]
            log_time = answer.get('dtCreateTime').strftime("%Y-%m-%d")
            now_time = datetime.datetime.now().strftime("%Y-%m-%d")
            if log_time < now_time:
                result = self.selAnswer(totalright=answer.get('iTotalRight'), 
                                        continueright=answer.get('iContinueRight'), 
                                        dbCursor=cursor)
            else:
                result = self.selQuestion(question_id=answer.get('iQuestionId'),
                                        dbCursor=cursor)
        else:
            result = self.selAnswer(totalright=0, 
                                    continueright=0, 
                                    dbCursor=cursor)
        Smart_Mysql.dispose(conn=conn, cursor=cursor)
        return {
            "ret": 0,
            "msg": "操作成功",
            "result": result
        }

    def daily_answer(self, chose_id):
        #每日一答
        #查答题记录
        log = self.checkLog()
        t = int(log[0].get('iTotalRight')) 
        c = int(log[0].get('iContinueRight'))
        answer_id = log[0].get('iQuestionId')
        if int(log[0].get('iRight')) == -1:
            return {
                'ret' : -2,
                'msg' : '已经答过题'
            }
        #查题目
        data = self.selQuestion(question_id=answer_id)
        sOption = data[0]['sOption'].split('__')
        iRight = data[0]['iRight'].split('__')
        r = 0
        if int(iRight[chose_id]) == 1:
            #回答正确
            t += 1
            c += 1
            r = 1
        else:
            c = 0
        suc = self.upAnswer(question_id=answer_id, 
                        answerindex=chose_id, 
                        right=r, 
                        totalright=t, 
                        continueright=c)
        if suc:
            return {
                'ret' : 0,
                'msg' : '答题成功',
                'totalright': t,
                'continueright': c,
                'right': r
            }
        else:
            return {
                'ret' : -2,
                'msg' : '系统繁忙'
            }


#签到
class Signin():

    def main(self, user_id):
        user_id = user_id
        data = {}
        sql = "select id from tbActSignin where iUserId = %s AND \
            to_days(dtCreateTime)=to_days(now())"
        check = Smart_Mysql.query(sql, param=[user_id])
        if check:
            data['ret'] = -2
            data['msg'] = '打卡失败：已经打卡'
        else:
            sql = "INSERT INTO tbActSignin SET iUserId = %s"
            suc = Smart_Mysql.insert(sql, param=[user_id])
            if suc:
                data['ret'] = 0
                data['msg'] = '打卡成功'
            else:
                data['ret'] = -2
                data['msg'] = '打卡出现异常'
        return data

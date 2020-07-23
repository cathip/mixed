import time

from base.cmysql import Mysql

#预扣限量
def hold_yukou(holds, user_id, source, mysql=None):
    holds = holds 
    #[
    # {
    # key:product_1909_20,
    # use:222,
    # total:5555}, 
    # {
    # key:product_1909_20,
    # use:222, #使用数量
    # total:5555}, #资格总数
    # ]
    mysql = mysql if mysql else Mysql()
    source = source #来源
    mysql = mysql
    data = {}
    if len(holds) > 5:
        data['ret'] = -2
        data['msg'] = "holdkey参数过长最多五个"
        return data
    for i in holds:
        sql = "SELECT * FROM tbHold WHERE iUserId = %s AND sHoldKey = %s FOR UPDATE"
        check = mysql.getOne(sql, param=[user_id, i.get('key')])
        if not check:
            if int(i.get('use')) > int(i.get('total')):
                data['ret'] = -2
                data['msg'] = f"[{i.get('ext')}]超出购买上限"
                break
            sql = "INSERT INTO tbHold SET iUserId = %s , sHoldKey = %s, iNumUsed = 0, \
                    iNumFreeze = %s, iNumTotal = %s, sSource = %s"
            mysql.insertOne(sql, param=[user_id, 
                                        i.get('key'), 
                                        i.get('use'), 
                                        i.get('total'), 
                                        source])
            data['ret'] = 0
            data['msg'] = "预扣成功"
        else:
            check_num = int(i.get('use')) \
                        + int(check.get('iNumUsed')) \
                        + int(check.get('iNumFreeze'))
            print('-------check_num-------')
            print(check_num)
            if check.get('iNumFreeze') != 0:
                data['ret'] = -2
                data['msg'] = f"[{i.get('ext')}]已有冻结限量"
                break
            if check_num > int(i.get('total')):
                data['ret'] = -2
                data['msg'] = f"[{i.get('ext')}]已达购买上限"
                break
            #开始扣除
            sql = "UPDATE tbHold SET iNumFreeze = %s, \
                    iNumTotal = %s WHERE id = %s"
            mysql.update(sql, param=[i.get('use'), i.get('total'), check.get('id')])
            data['ret'] = 0
            data['msg'] = "预扣成功"
    if data['ret'] == -2:
        mysql.errdispose()
        return data
    mysql.dispose()
    return data

#实扣限量
def hold_shikou(holds, user_id, mysql=None):
    hold_key = holds
    #[
    # {
    # key:product_1909_20
    # {
    # key:product_1909_20
    # ]
    mysql = mysql if mysql else Mysql()
    data = {}
    for i in hold_key:
        sql = "SELECT * FROM tbHold WHERE iUserId = %s AND sHoldKey = %s FOR UPDATE"
        check = mysql.getOne(sql, param=[user_id, i.get('key')])
        if not check:
            data['ret'] = -2
            data['msg'] = f"{i.get('ext')}参数出现问题"
            break
        if int(check.get('iNumFreeze')) <= 0:
            data['ret'] = -2
            data['msg'] = f"[{i.get('ext')}]限量已回滚扣除失败"
            break
        else:
            sql = "UPDATE tbHold SET iNumUsed = iNumUsed + %s, iNumFreeze = 0 WHERE id = %s"
            suc = mysql.update(sql, param=[check.get('iNumFreeze'), check.get('id')])
            if not suc:
                data['ret'] = -2
                data['msg'] = f"[{i.get('ext')}]更新实扣出现问题"
            data['ret'] = 0
            data['msg'] = "实扣成功"
    if data['ret'] == -2:
        mysql.errdispose()
        return data
    mysql.dispose()
    return data

#回滚限量
def hold_huigun(holds, user_id, mysql=None):
    hold_key = holds
    mysql = mysql if mysql else Mysql()
    data = {}
    for i in hold_key:
        sql = "SELECT * FROM tbHold WHERE iUserId = %s AND sHoldKey = %s FOR UPDATE"
        check = mysql.getOne(sql, param=[user_id,  i.get('key')])
        data = {}
        if not check:
            data['ret'] = -2
            data['msg'] = "参数出现问题"
            break
        else:
            sql = "UPDATE tbHold SET iNumFreeze = 0 WHERE id = %s"
            suc = mysql.update(sql, param=[check.get('id')])
            if not suc:
                data['ret'] = -2
                data['msg'] = "回滚限量失败"
                break
            data['ret'] = 0
            data['msg'] = "回滚成功"
    if data['ret'] == -2:
        mysql.errdispose()
        return data
    mysql.dispose()
    return data
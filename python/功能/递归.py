def range_sql(sql_parentid):
    sql = "SELECT acti_parentId FROM activity_class WHERE id = '{id}'".format(id=sql_parentid)
    sql_parentid = mysql.getOne(sql)
    if sql_parentid.get('acti_parentId') > 0:
        sql = "SELECT acti_parentId FROM activity_class WHERE id = '{id}'".format(id=sql_parentid.get('acti_parentId'))
        info = mysql.getOne(sql)
        range_sql(sql_parentid=info.get('acti_parentId'))
    else:
        #删除~~~~~~~~~~~~~
        pass

sql = "SELECT acti_parentId FROM activity_class WHERE id = '{id}'".format(id=self.__reqData['id'])
            parent_info = mysql.getOne(sql)
            if parent_info:
                sql = "SELECT acti_parentId FROM activity_class WHERE id = '{id}'".format(id=parent_info.get('acti_parentId'))
                parent_two_info = mysql.getOne(sql)
                if parent_two_info:
                    sql = "SELECT acti_parentId FROM activity_class WHERE id = '{id}'".format(id=parent_two_info.get('acti_parentId'))
                    parent_three_info = mysql.getOne(sql)
                    if parent_three_info:
                        sql = "SELECT acti_parentId FROM activity_class WHERE id = '{id}'".format(id=parent_three_info.get('acti_parentId'))
                        parent_four_info = mysql.getOne(sql)
                        if parent_four_info:
                            rencai = "你真的是人才"
                            return rencai
                        else:
                            sql = "DELETE FROM activity_class WHERE id = '{id}'".format(id=parent_three_info.get('acti_parentId'))
                            suc = mysql.delete(sql)
                            if suc:
                                return 1
                            else:
                                return 0 
                    else:
                        sql = "DELETE FROM activity_class WHERE id = '{id}'".format(id=parent_three_info.get('acti_parentId'))
                        suc = mysql.delete(sql)
                        if suc:
                            return 1
                        else:
                            return 0 
                else:
                    sql = "DELETE FROM activity_class WHERE id = '{id}'".format(id=parent_three_info.get('acti_parentId'))
                    suc = mysql.delete(sql)
                    if suc:
                        return 1
                    else:
                        return 0 
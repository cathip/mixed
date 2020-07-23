import json
from django.http import request, HttpResponse, JsonResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings, callJson
import itertools

#增加商户商品
class Add_Mer_Product(View):
    
    def post(self, request):
        self.params = {}
        self.params['product_name'] = request.POST.get('product_name')
        self.params['mer_id'] = request.POST.get('mer_id')
        self.params['product_img'] = request.POST.get('product_img')
        self.params['min_price'] = request.POST.get('min_price')
        self.params['max_price'] = request.POST.get('max_price')
        self.params['hhcoin'] = request.POST.get('hhcoin')
        self.params['product_type'] = int(request.POST.get('product_type')) #传0代表无规格商品 传1代表有规格商品
        self.params['min_buy'] = request.POST.get('min_buy')
        self.params['max_buy'] = request.POST.get('max_buy')
        self.params['product_spec'] = json.loads(request.POST.get('spec_list')) 
        #[{'颜色' :['黑色','白色','红色']},{'类型' :['长','短','粗']}]
        self.params['product_stock'] = json.loads(request.POST.get('product_stock')) 
        #[{'hehe':1, 'price':22, 'stockname':'zzz-黑色-长', 'specdetail':'黑色,长', 'min_buy':1, 'max_buy':2}]
        print(self.params)
        try:
            mysql = Mysql()
            sql = "INSERT INTO mer_product SET mer_id='{mer_id}', \
                    product_name='{product_name}', product_img='{product_img}', \
                    min_price='{min_price}', max_price='{max_price}', hhcoin='{hhcoin}'".format(\
                    mer_id=self.params['mer_id'], product_name=self.params['product_name'], \
                    product_img=self.params['product_img'], min_price=self.params['min_price'],\
                    max_price=self.params['max_price'], hhcoin=self.params['hhcoin'])
            product_id = mysql.insertOne(sql)
            if self.params['product_type'] == 0:
                sql = "INSERT INTO mer_stock SET product_id='{product_id}', stock_name='{stock_name}', \
                    price='{price}', hhcoin='{hhcoin}', min_buy='{min_buy}', max_buy='{max_buy}'" \
                    .format(product_id=product_id, stock_name=self.params['product_name'], max_buy=self.params['max_buy'], \
                    price=self.params['min_price'], hhcoin=self.params['hhcoin'], min_buy=self.params['min_buy'])
                mysql.insertOne(sql)
                mysql.dispose()
                return HttpResponse(1)
            if self.params['product_type'] == 1:
                data = {}
                for i in self.params['product_spec']:
                    for k, v in i.items():
                        sql = "INSERT INTO mer_spec SET spec_name='{spec_name}', \
                            product_id='{product_id}'".format(spec_name=k, product_id=product_id)
                        spec_id = mysql.insertOne(sql)
                        for s in v:
                            sql = "INSERT INTO mer_specdetail SET detail_name='{detail_name}', \
                                spec_id='{spec_id}', product_id='{product_id}'".format(detail_name=s,\
                                spec_id=spec_id, product_id=product_id)
                            specdetail_id = mysql.insertOne(sql)
                            data[s] = specdetail_id
                for stock in self.params['product_stock']:
                    specdetail = stock.get('specdetail')
                    list_a = specdetail.split(',')
                    list_b = []
                    for detail in list_a:
                        list_b.append(str(data.get(detail)))
                    print(list_b)
                    #print(",".join('%s' %detail_id for detail_id in list_b))
                    #stock_specs = ','.join(list_b)
                    stock_specs = ",".join(list_b)
                    sql = "INSERT INTO mer_stock SET product_id='{product_id}', stock_specs_name='{specdetail}', stock_specs='{stock_specs}', \
                        stock_name='{stock_name}', price='{price}', hhcoin='{hhcoin}', min_buy = '{min_buy}', max_buy = '{max_buy}' \
                        ".format(product_id=product_id, specdetail=specdetail, \
                        stock_specs=stock_specs, stock_name=stock.get('stockname'), price=float(stock.get('price')), \
                        hhcoin=int(stock.get('hhcoin')), min_buy=stock.get('min_buy'), max_buy=stock.get('max_buy'))
                    mysql.insertOne(sql)
                mysql.dispose()
                return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#编辑商户商品
class Edit_Mer_Product(View):
    
    def post(self, request):
        self.params = {}
        self.params['product_id'] = request.POST.get('product_id')
        self.params['product_name'] = request.POST.get('product_name') 
        self.params['product_img'] = request.POST.get('product_img')
        self.params['min_price'] = request.POST.get('min_price')
        self.params['max_price'] = request.POST.get('max_price')
        self.params['hhcoin'] = request.POST.get('hhcoin')
        self.params['product_stock'] = json.loads(request.POST.get('product_stock')) 
        #[{'stockname':'xx',hhcoin':1, 'price':22, 'stock_id':222, 'min_buy':1, 'max_buy':2}, {...}]
        self.params['delete_stock'] = json.loads(request.POST.get('delete_stock')) #[1,3,4,5]
        print(self.params)
        try:
            mysql = Mysql()
            sql = "UPDATE mer_product SET  product_name='{product_name}', \
                    product_img='{product_img}', min_price='{min_price}', \
                    max_price='{max_price}', hhcoin='{hhcoin}' \
                    WHERE product_id='{product_id}'".format(product_id=self.params['product_id'], \
                    product_name=self.params['product_name'], product_img=self.params['product_img'],\
                    min_price=self.params['min_price'], max_price=self.params['max_price'], \
                    hhcoin=self.params['hhcoin'])
            mysql.update(sql)
            for i in self.params['product_stock']:
                sql = "UPDATE mer_stock SET stock_name='{stock_name}', \
                price='{price}', hhcoin='{hhcoin}', min_buy='{min_buy}', max_buy='{max_buy}' \
                WHERE stock_id ='{stock_id}'".format(stock_name=i.get('stockname'), min_buy=i.get('min_buy'),\
                price=i.get('price'), hhcoin=i.get('hhcoin'), stock_id=i.get('stock_id'), max_buy=i.get('max_buy'))
                print(sql)
                mysql.update(sql)
            for x in self.params['delete_stock']:
                sql = "DELETE FROM mer_stock WHERE stock_id = '{stock_id}'".format(stock_id=x)
                mysql.delete(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#删除商户商品 
class Del_Mer_Product(View):
    
    def post(self, request):
        self.params = {}
        self.params['product_id'] = request.POST.get('product_id')
        mysql = Mysql()
        sql = "DELETE FROM mer_product WHERE \
            product_id = '{product_id}'".format(product_id=self.params['product_id'])
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#查看单个商户商品
class Sel_Mer_Product(View):
    
    def get(self, request):
        self.params = {}
        self.params['product_id'] = request.GET.get('product_id')
        mysql = Mysql()
        data = {}
        sql = "SELECT * FROM mer_product WHERE product_id \
            = '{product_id}'".format(product_id=self.params['product_id'])
        product_info = mysql.getOne(sql)
        data['product_info'] = product_info
        #商品所对应的库存商品
        sql = "SELECT * FROM mer_stock WHERE product_id = \
            '{product_id}'".format(product_id=self.params['product_id'])
        stock_check = mysql.getOne(sql)
        stock = mysql.getAll(sql)
        data['stock'] = stock
        if stock_check.get('stock_specs'):
            #商品所拥有的规格以及 规格详情
            sql = "SELECT * FROM mer_spec WHERE product_id \
                = '{product_id}'".format(product_id=self.params['product_id'])
            spec_info = mysql.getAll(sql)
            list_a = []
            for i in spec_info:
                spec_dict = {}
                sql = "SELECT spec_detail_id, detail_name FROM mer_specdetail WHERE spec_id = \
                    '{spec_id}'".format(spec_id=i.get('spec_id'))
                spec_detail_info = mysql.getAll(sql)
                spec_dict['spec_id'] = i.get('spec_id')
                spec_dict['spec_name'] = i.get('spec_name')
                #spec_dict['spec_detail'] = [x.get('detail_name') for x in spec_detail_info]
                spec_dict['spec_detail'] = [x for x in spec_detail_info]
                list_a.append(spec_dict)
            data['spec'] = list_a
        mysql.dispose()
        data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
        return HttpResponse(data)

#查看商户对应的全部商品
class All_Mer_Product(View):

    def get(self, request):
        self.params = {}
        self.params['mer_id'] = request.GET.get('mer_id')
        self.params['row'] = request.GET.get('row')
        self.params['page'] = request.GET.get('page')
        self.params['product_name'] = request.GET.get('product_name')
        mysql = Mysql()
        sql = "SELECT * FROM mer_product WHERE mer_id = {mer_id} AND product_name \
            LIKE '%{product_name}%'".format(mer_id=self.params['mer_id'], product_name=self.params['product_name'])
        print(sql)
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sumpage, info = Pagings.paging(info, row=self.params['row'], page=self.params['page'])
            data = {}
            data['sumpage'] = sumpage
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)

#删除商户商品规格
class Del_Mer_Specdeatil(View):

    def post(self, request):
        self.params = {}
        self.params['spec_id'] = request.POST.get('spec_id')
        self.params['spd_id'] = request.POST.get('spec_detail_id')
        self.params['check_num'] = int(request.POST.get('check_num')) #第一次点击传 1第二次确认删除传2
        mysql = Mysql()
        try:
            if self.params['check_num'] == 1:
                sql = "SELECT * FROM mer_stock WHERE FIND_IN_SET \
                    ('{spd_id}', mer_stock.stock_specs)".format(spd_id=self.params['spd_id'])
                stock_info = mysql.getAll(sql)
                if stock_info:
                    mysql.dispose()
                    stock_info = json.dumps(stock_info, ensure_ascii=False, sort_keys=True, indent=4)
                    return HttpResponse(stock_info)
                else:
                    mysql.errdispose()
                    return HttpResponse('规格详情id错误')
            if self.params['check_num'] == 2:
                self.params['stock_list'] = json.loads(request.POST.get('stock_list')) #stockid check_num=2传过来
                sql = "DELETE FROM mer_specdetail WHERE spec_detail_id='{spd_id}'".format(spd_id=self.params['spd_id'])
                mysql.delete(sql)
                sql = "SELECT * FROM mer_specdetail WHERE spec_id = '{spec_id}'".format(spec_id=self.params['spec_id'])
                check_spec = mysql.getOne(sql)
                for i in self.params['stock_list']:
                    sql = "DELETE FROM mer_stock WHERE stock_id = '{stock_id}'".format(stock_id=i)
                    mysql.delete(sql)
                if check_spec:
                    pass
                else:
                    #sql = "DELETE FROM mer_spec WHERE spec_id = '{spec_id}'".format(spec_id=self.params['spec_id'])
                    mysql.errdispose(sql)
                    return HttpResponse(2)
                mysql.dispose()
                return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)
            
#编辑商户库存商品(暂时不用)
class Edit_Mer_Stock(View):

    def post(self, request):
        self.params = {}
        self.params['stock_id'] = request.POST.get('stock_id')
        self.params['price'] = float(request.POST.get('price'))
        self.params['hhcoin'] = int(request.POST.get('hhcoin'))
        mysql = Mysql()
        sql = "UPDATE mer_stock SET price='{price}', hhcoin='{hhcoin}' \
            WHERE stock_id ='{stock_id}'".format(price=self.params['price'], \
            hhcoin=self.params['hhcoin'], stock_id=self.params['stock_id'])
        suc = mysql.update(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#计算笛卡尔积
class Mer_Itertools(View):

    def post(self, request):
        self._data_list = json.loads(request.POST.get('data_list'))
        new_list = []
        for item in itertools.product(*self._data_list):
            new_list.append(list(item))
        return HttpResponse(callJson(new_list))

# car = cartesian()
# car.add_data([1,2])
# car.add_data([3,4])
# car.add_data([5,6,7])
# car.add_data([8,9])
# car.build()
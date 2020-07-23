from django.urls import path
from merchant.views import login, wx_date, order, user


urlpatterns = [
    #--------------------------商户端相关接口---------------------------
    path('login/', login.Login.as_view()), #登陆
    path('up_user/', user.Up_User.as_view()), #更新用户头像昵称
    path('get_openid/', wx_date.Get_Openid.as_view()), #获取openid
    path('sel_order/', order.Sel_Orders.as_view()), #获取订单信息
    path('scan_qrcode/', order.Scan_Qrcode.as_view()), #扫一扫使用卷码
    path('scan_order/', order.Scan_Order.as_view()), #扫一扫查看订单
    path('order_numbs/', order.Order_Numbs.as_view()), #当天数量 金额
    path('sel_user/', user.Sel_User.as_view()),#查看店铺人员
    path('add_user/', user.Add_User.as_view()),#添加店铺人员
    path('del_user/', user.Del_User.as_view()),#删除店铺人员
    path('test/', user.Test.as_view()), #测试
]
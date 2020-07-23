# coding=utf-8

from django.urls import path
from shops.views import order, product, cart, user_info, \
    wx_data, turntable, server_time, banner, user_log, school, \
    wx_pay, index, merchant, rank, quiz, click_card, machine, test, \
    bargain, oneyuanpurchase, cash_out, star_sign, star_sign_h5, mer


urlpatterns = [
    # ______________________新版接口____________________________
    path('time', server_time.Server_Time.as_view()),   # 服务器当前时间
    path('machine', machine.Sel_Machine.as_view()),   # 查看机器
    path('banner', banner.Banner.as_view()),   # 获取banneer
    path('index', index.Index.as_view()),   # #首页大树（全员总投递量）

    path('cash_out/<str:handle>', cash_out.CashOut.as_view()), #余额提现微信
    path('cash_out/toWx', cash_out.BalanceToWx.as_view()), #提现到微信

    path('address/<str:handle>', user_info.Address.as_view()),   #地址
    path('address/default/<str:handle>', user_info.Default_address.as_view()),   #默认地址 

    path('merchant/<str:handle>', mer.Merchant.as_view()), #发现
    path('merchant/<str:handle>/<str:state>', mer.Merchant.as_view()), #发现购物车相关

    path('wxdate/<str:handle>', wx_data.WxData.as_view()),   #微信数据
    path('wxdate/getOpenid', wx_data.OpenView.as_view()),  # 获取openid
    path('wxdate/checkToken', wx_data.Check_Openid.as_view()), #检查登录态
    
    path('userlog/<str:handle>', user_log.UserLog.as_view()),  # 个人盒盒币记录
    path('userlog/<str:handle>/<str:state>', user_log.UserLog.as_view()),  # 个人盒盒币记录

    path('click_card/<str:handle>', click_card.Click_Card.as_view()),  # 打卡
    path('daily_quiz/<str:handle>', quiz.Daily_Quiz.as_view()),  # 每日一答
    path('product/<str:handle>', product.Product.as_view()),  # 商城商品
    path('order/<str:handle>', order.Orders.as_view()), #商城订单
    path('cart/<str:handle>', cart.Cart.as_view()),   # 购物车
    path('school/<str:handle>', school.School.as_view()),   #学校
    path('user/<str:handle>', user_info.User.as_view()),   #用户
    #_________________________微信支付——————————————————————————————————
    path('wx_callback', wx_pay.Wx_Callback.as_view()),  # 微信回调
    path('wx_pay', wx_pay.Wx_Pay.as_view()),  # 微信支付
    # ______________________排行榜____________________________
    path('rank', rank.Rank.as_view()),  # 排行榜
    path('last_rank', rank.Last_Rank.as_view()),  # 排行榜
    path('rank_ruler', rank.Rank_Ruler.as_view()),  # 排行榜规则
    #___________________________星座碎片_______________________________
    path('sel_mypath/', star_sign.SelMyPatch.as_view()),#查看我的碎片
    path('patch_log/', star_sign.SelPatchLog.as_view()),#查看我的碎片
    path('mission_path/', star_sign.MissionPatch.as_view()),#完成任务获取碎片
    path('mission_finish/', star_sign.Finish.as_view()),#完成集碎片
    path('luck_draw/', star_sign.Luck_Draw.as_view()),#小程序抽奖获取
    path('starry_market/', star_sign.StarryMarket.as_view()),#星空市场
    path('starry_data/', star_sign.StarryData.as_view()), #活动数据
    #——————————————————————————分享h5——————————————————————————————————
    path('autograph/', wx_data.AutoGraph.as_view()), ##获取网页签名
    path('h5_userinfo/', wx_data.SnsApiUserInfo.as_view()), #获取用户信息
    path('h5_luckydraw/', star_sign_h5.H5LuckyDraw.as_view()), #关于分享的操作
    path('share/', star_sign_h5.Share.as_view()), #关于分享的操作
    path('terro/', star_sign_h5.Test.as_view()), #测试用例
    #——————————————————————————TOKEN——————————————————————————————————
    path('prologin/', test.Test_Login.as_view()),
    path('getcode/', test.GetCode.as_view()),
    path('getToken/', test.GetToken.as_view())
    # _________________________抽奖________________________________
    # path('turntable/', turntable.Turntable.as_view()),  # 测试抽奖
    # path('reward_log/', turntable.Reward_Log.as_view()),  # 抽奖记录
    #———————————————————————砍价(已下线)——————————————————————————————
    # path('bargain_product/', bargain.Bargain_Product.as_view()), #砍价商品列表
    # path('bp_detail/', bargain.Bargain_Product_Detail.as_view()), #查看砍价商品详情
    # path('start_bargain/', bargain.Start_Bargain.as_view()), #发起砍价
    # path('bargain/', bargain.Bargain.as_view()), #帮砍价
    # path('sel_bgorder/', bargain.Sel_BgOrder.as_view()),  #购买记录
    # path('bplace_anorder/', bargain.Place_Anorder.as_view()), #购买（下单）
    # path('bargain_callback/', bargain.Wx_CallBack.as_view()), #支付回调
    # path('close_bargain/', bargain.Close_Bargain.as_view()), #删除订单继续砍价
    #—————————————————————一元购(已下线)————————————————————————————————
    # path('oneyuanpurchase/', oneyuanpurchase.OneYuanPurchase.as_view()), #下单
    # path('oyp_callback/', oneyuanpurchase.OneYuanPurchase_CallBack.as_view()), #支付回调
    # path('my_sapling/', oneyuanpurchase.My_Sapling.as_view()), #我的小树苗Sapling
    # path('winning_list/', oneyuanpurchase.Winning_list.as_view()), #中奖列表
    # path('ba_test/', oneyuanpurchase.Test.as_view()), #测试
    # path('three_oneyuan/', oneyuanpurchase.ThreeOneYuan.as_view()), #三块钱
    # path('toyp_callback/', oneyuanpurchase.ThreeOneYuan_CallBack.as_view()), #三块钱回调
]
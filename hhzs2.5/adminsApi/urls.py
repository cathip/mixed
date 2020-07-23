#utf-8

from django.urls import path
from adminsApi.views import Login, Adminer, store, school, message, \
    banner, qcloud, stock, product, proclass, turntable, prize, prize_class, \
    school, order, merchant, mer_product, rank, answer, information, \
    recurrence

urlpatterns = [
    #--------------------------腾讯云图片操作---------------------------
    path('test_qcloud/', qcloud.Tencent_Cos.as_view()), #图片操作
    #--------------------------登录接口---------------------------
    path('login/', Login.Login.as_view()), 
    path('store_login/', Login.Store_Login.as_view()),  #商户登录
    #--------------------------递推人员-------------------------
    path('add_recurrence/', recurrence.Add_Recurrence.as_view()),  #增加递推人员
    path('del_recurrence/', recurrence.Del_Recurrence.as_view()),  #删除递推人员
    path('edit_recurrence/', recurrence.Edit_Recurrence.as_view()),  #编辑递推人员
    path('sel_recurrence/', recurrence.Sel_Recurrence.as_view()),  #查找递推人员
    #-------------------------每日一答----------------------------
    path('add_answer/', answer.Add_Answer.as_view()),#增加题目
    path('del_answer/', answer.Del_Answer.as_view()),#删除题目
    path('sel_answer/', answer.Sel_Answer.as_view()),#查看题目
    path('edit_answer/', answer.Edit_Answer.as_view()),#更改题目
    path('sel_answer_detail/', answer.Sel_Answer_Detail.as_view()),#查看题目详情
    #-------------------------商户相关----------------------------
    path('add_merchant/', merchant.Add_Merchant.as_view()), #增加商户
    path('edit_merchant/', merchant.Edit_Merchant.as_view()), #编辑商户
    #path('del_merchant/', merchant.Del_Merchant.as_view()),#删除商户
    path('sel_merchant/', merchant.Sel_Merchant.as_view()),#查看商户
    path('add_meradmin/', merchant.Add_MerAdmin.as_view()),#增加商户账号
    path('del_meradmin/', merchant.Del_MerAdmin.as_view()),#删除商户账号
    path('sel_meradmin/', merchant.Sel_MerAdmin.as_view()),#查看商户账号
    path('edit_meradmin/', merchant.Edit_MerAdmin.as_view()),#编辑商户账号
    #-------------------------商户商城-----------------------------
    path('add_merproduct/', mer_product.Add_Mer_Product.as_view()),#增加商户商品
    path('del_merproduct/', mer_product.Del_Mer_Product.as_view()),#删除商户商品
    path('sel_merproduct/', mer_product.Sel_Mer_Product.as_view()),#查看单个商户商品
    path('all_merproduct/', mer_product.All_Mer_Product.as_view()),#查看全部商户商品
    path('edit_merproduct/', mer_product.Edit_Mer_Product.as_view()), #编辑商户库存的价格以及盒盒币
    path('del_merspec_detail/', mer_product.Del_Mer_Specdeatil.as_view()),#删除商品规格详情
    path('mer_itertools/', mer_product.Mer_Itertools.as_view()),#计算笛卡尔积
    #-----------------------排行榜----------------------------------
    path('sel_rank_reward/', rank.Sel_Rank_Reward.as_view()),#查看排行榜排名奖励 （0个人 1校园）
    path('edit_rank_reward/', rank.Edit_Rank_Reward.as_view()),#为排行榜增加奖励
    path('rank_ruler/', rank.Rank_Ruler.as_view()), #排行榜规则相关
    #------------------------商品分类-------------------------------
    path('add_proclass/', proclass.Addclass.as_view()), #增加分类
    path('edit_proclass/', proclass.Editclass.as_view()), #编辑分类
    path('del_proclass/', proclass.DelClass.as_view()), #删除分类
    path('get_proclass/', proclass.Getclass.as_view()), #获取子级或者父级分类（父级传0）
    path('get_proclass_list/', proclass.GetClassList.as_view()), #分类列表
    path('get_class_product/', proclass.GetClassProduct.as_view()), #获取分类下的上架商品
    #------------------------商品列表--------------------------------
    path('add_product/', product.Add_Product.as_view()), #新增商品
    path('del_product/', product.Del_Product.as_view()), #编辑商品
    path('edit_product/', product.Edit_Product.as_view()), #编辑商品
    path('sel_product/', product.Sel_Product.as_view()),  #查看所有商品列表展示商品(上下架可选)
    path('product_stock/', product.Product_Stock.as_view()), #查找商品对应的库存商品
    path('add_hotproduct/', product.Set_HotPorduct.as_view()), #添加商品为热门商品
    path('del_hotproduct/', product.Del_HotPorduct.as_view()), #删除热门商品
    #------------------------库存商品-------------------------------
    path('add_stock/', stock.Add_Stock.as_view()), #增加库存商品
    path('edit_stock/', stock.Edit_Stock.as_view()), #编辑库存商品
    path('del_stock/', stock.Del_Stock.as_view()), #删除库存商品
    path('upper_shelf/', stock.Upper_Shelf.as_view()), #上架库存商品（上架到商品列表）
    path('lower_shelf/', stock.Lower_Shelf.as_view()), #下架商品（同步商品列表）
    path('lower_stock/', stock.Lower_Stock.as_view()), #下架库存 
    path('test/', stock.Test.as_view()), #测试接口 杂七杂八
    #-----------------------订单接口---------------------------------
    path('sel_order/', order.Sel_Orders.as_view()), #查看订单
    path('sel_order_detail/', order.Sel_Order_Detail.as_view()), #查看订单详情
    path('store_turnover/', order.Sel_Store_Turnover.as_view()), #查看订单详情
    #path('cancel_order/', order.Cancel_Order.as_view()),#取消订单
    #---------------------自营商家查看订单----------------------------
    path('sel_order_flow/', order.Order_Flow.as_view()), #查看订单流水Order_Flow
    path('deliver_goods/', order.Deliver_goods.as_view()), #发货
    path('del_order/', order.Del_Order.as_view()), #删除订单
    path('sel_as_order/', order.As_Order.as_view()), #查看售后订单
    path('up_as_order/', order.Up_As_Order.as_view()), #处理售后订单
    #--------------------------管理员-------------------------------
    path('add_adminer/', Adminer.AddAdminer.as_view()),  # 增加管理员
    path('all_admin/', Adminer.AllAdminer.as_view()),   # 管理员列表
    path('del_adminer/', Adminer.DelAdminer.as_view()),  # 删除管理员
    path('edit_adminer/', Adminer.UpAdminer.as_view()),  # 编辑管理员
    path('get_power/', Adminer.Get_Power.as_view()),  # 校验权限
    #--------------------------店铺-------------------------------
    path('add_store/', store.AddStore.as_view()), # 增加店铺 POST
    path('del_store/', store.DelStore.as_view()), # 删除店铺 POST
    path('sel_store/', store.SelStore.as_view()), # 查询店铺 GET
    path('edit_store/', store.EditStore.as_view()), # 编辑店铺 POST
    path('store_product/', store.StoreProduct.as_view()), # 查看店铺的商品
    #----------------------banner--------------------------
    path('add_banner/', banner.Add_Banner.as_view()), #增加banner
    path('del_banner/', banner.Del_Banner.as_view()), #删除banner
    path('edit_banner/', banner.Edit_Banner.as_view()), #修改banner
    path('sel_banner/', banner.Sel_Banner.as_view()), #查询banner
    #--------------------------抽奖转盘--------------------------------
    path('sel_probability/', turntable.Sel_Probability.as_view()), #获取转盘概率 以及对应奖励编号
    path('edit_probability/', turntable.Edit_Probability.as_view()), #编辑转盘概率 以及对应奖励编号
    path('turntable_stock/', turntable.Turntable_Stock.as_view()), #自营商品奖励
    #外部商品奖励
    path('turntable_coupon/', turntable.Turntable_Coupon.as_view()), #卷码奖励
    #二维码（活动资格）
    path('turntable_phv/', turntable.Turntable_Phv.as_view()),#会员奖励 余额奖励 盒盒币奖励
    #谢谢惠顾
    path('reward_log/', turntable.Reward_Log.as_view()), #中奖记录Reward_Log
    path('award_prizes/', turntable.Award_Prizes.as_view()), #领奖
    #--------------------------奖品------------------------------------
    path('add_prize/', prize.Add_Prize.as_view()), #增加奖品
    path('del_prize/', prize.Del_Prize.as_view()), #删除奖品
    path('edit_prize/', prize.Edit_Prize.as_view()), #编辑奖品
    path('sel_prize/', prize.Sel_Prize.as_view()), #查看奖品
    #--------------------------奖品分类---------------------------------
    path('add_prizeclass/', prize_class.Add_Prizeclass.as_view()), #增加奖品分类
    path('del_prizeclass/', prize_class.Del_Prizeclass.as_view()), #删除奖品分类
    path('edit_prizeclass/', prize_class.Edit_Prizeclass.as_view()), #编辑奖品分类
    path('sel_prizeclass/', prize_class.Sel_Prizeclass.as_view()), #查看奖品分类
    path('sel_class_prize/', prize_class.Sel_Class_Prize.as_view()), #根据分类查看奖品
    path('sel_class_type/', prize_class.Sel_Class_Type.as_view()), #根据分类获取操作类型
    #--------------------------学校相关---------------------------
    path('sel_school_area/', school.Sel_School_Area.as_view()), #查看学校校区
    path('edit_school_area/', school.Edit_School_Area.as_view()),#编辑校区
    path('del_school_area/', school.Del_School_Area.as_view()),#删除校区
    path('add_school_area/', school.Add_School_Area.as_view()),#增加校区
    path('sel_school/', school.Sel_School.as_view()), #查看学校
    path('del_school/', school.Del_School.as_view()), #删除学校
    path('edit_school/', school.Edit_School.as_view()), #编辑学校
    path('add_school/', school.Add_School.as_view()), #增加学校
    path('sel_school_address/', school.Sel_School_Address.as_view()), #查看学校地址
    path('edit_school_address/', school.Edit_School_Address.as_view()), #编辑学校地址
    path('del_school_address/', school.Del_School_Address.as_view()), #删除学校地址
    path('add_school_address/', school.Add_School_Address.as_view()), #增加学校地址
    #------------------------资讯---------------------------------
    path('add_news/', information.Add_Details.as_view()), #增加资讯
    path('del_news/', information.Del_Details.as_view()), #删除资讯
    path('edit_news/', information.Edit_Details.as_view()), #编辑资讯
    path('sel_news/', information.Sel_Details.as_view()), #查看资讯
    #------------------------test--------------------------------
    path('up_files/', Login.Test_Files.as_view()), #文件上传
]
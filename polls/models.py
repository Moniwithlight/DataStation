from django.db import models
        
class User(models.Model):
    """用户"""
    no = models.AutoField(primary_key=True, verbose_name='编号')
    username = models.CharField(max_length=20, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='用户密码')
    name = models.CharField(max_length=30,unique=True, blank=True, verbose_name='姓名')

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'


class AD(models.Model):
    no = models.AutoField(primary_key=True,verbose_name='编号')
    start_date = models.DateField(verbose_name='开始日期')
    #end_date = models.DateField(verbose_name='结束日期')
    ad_group_name = models.CharField(max_length=100,verbose_name='广告组名称')
    currency = models.CharField(max_length=20,verbose_name='货币')
    ad_campaign = models.CharField(max_length=1000,verbose_name='广告活动')
    ad_group = models.CharField(max_length=100,verbose_name='广告组')
    launch = models.CharField(max_length=255,verbose_name='投放')
    matching_type = models.CharField(max_length=20,verbose_name='匹配类型')
    customer_search_terms = models.CharField(max_length=255,verbose_name='客户搜索词')
    quantity_display = models.FloatField(verbose_name='展示量')
    hits = models.IntegerField(verbose_name='点击量')
    ctr = models.FloatField(verbose_name='点击率')
    cr = models.FloatField(verbose_name='每次点击成本')
    cost = models.FloatField(verbose_name='花费')
    total_sells = models.FloatField(verbose_name='总销售额')
    acos = models.FloatField(verbose_name='销售成本比')
    roa = models.FloatField(verbose_name='投入产出比')
    total_orders = models.IntegerField(verbose_name='总订单数')
    total_sell_amount = models.IntegerField(verbose_name='总销售数量')
    conversition_rate = models.FloatField(verbose_name='转化率')
    sku_sell_amount = models.IntegerField(verbose_name='SKU销售量')
    un_sku_sell_amount = models.IntegerField(verbose_name='非SKU销售量')
    sku_sell = models.FloatField(verbose_name='SKU销售额')
    un_sku_sell = models.FloatField(verbose_name='非SKU销售额')
    #name = models.ForeignKey(to=User,to_field='name',on_delete=models.DO_NOTHING)
    user = models.CharField(max_length=100,verbose_name='姓名')

    class Meta:
        verbose_name = '广告产品数据集合'
        verbose_name_plural = '广告产品数据集合'

    def __str__(self):
        return self.name
    
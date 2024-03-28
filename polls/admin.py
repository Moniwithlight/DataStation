from django.contrib import admin

from polls.models import AD
from polls.models import User
# Register your models here.

# class ADModelAdmin(admin.ModelAdmin):
#     list_display = ('no','start_date','ad_group_name','currency','ad_campaign','ad_group','launch','matching_type','customer_search_terms','quantity_display','hits','ctr','cr','cost','total_sells','acos','roa','total_orders','total_sell_amount','conversition_rate','sku_sell_amount','un_sku_sell_amount','sku_sell','un_sku_sell')
# admin.site.register(AD,ADModelAdmin)

# class SubjectModelAdmin(admin.ModelAdmin):
#     list_display = ('no','name','intro','is_hot')
#     search_fields = ('name',)
#     ordering = ('no',)

# class TeacherModelAdmin(admin.ModelAdmin):
#     list_display = ('no','name','sex','birth','gcount','bcount','sno')
#     search_fields = ('name',)
#     ordering = ('no',)

# admin.site.register(Subject,SubjectModelAdmin)
# admin.site.register(Teacher,TeacherModelAdmin)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('no','username','password','name')
admin.site.register(User,UserModelAdmin)





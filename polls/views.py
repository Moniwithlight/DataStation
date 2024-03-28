from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from polls.models import AD,User
from polls.forms import RegisterForm,LoginForm
from pathlib import Path
import pandas as pd
import numpy as np
import pymysql
from pymysql.converters import escape_string
import json
import difflib  #用于模糊匹配   diffli.(x,words,n,cutoff)
import six
import datetime
try:
    from io import BytesIO as IO
except:
    from io import StringIO as IO



BASE_DIR = Path(__file__).resolve().parent.parent


def login(request):
    """用户登录"""
    hint = ''
    backurl = request.GET.get('backurl', '/')
    if request.method == 'POST':
        backurl = request.POST['backurl']
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.filter(
                username=username, password=password).first()
            if user:
                request.session['userid'] = user.no
                request.session['username'] = user.username
                request.session['name'] = user.name
                return redirect('/')
            else:
                hint = '用户名或密码错误'

        else:
            hint = '请输入有效的登录信息'
    return render(request, 'login.html', {'hint': hint, 'backurl': backurl})


def register(request):
    """用户注册"""
    hint = ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            hint = '注册成功，请登录!'
            return render(request, 'login.html', {'hint': hint})

        else:
            hint = '请输入有效的注册信息'

    return render(request, 'register.html', {'hint': hint})

def logout(request):
    """用户注销"""
    request.session.flush()
    return redirect('/')

def upload(request):
    return render(request,"upload.html")

def grade_upload(request):
    if request.session.get('userid'):
        if request.method == 'POST':
            f = request.FILES.get('my_file')
            excel_type = f.name.split('.')[-1]
            if excel_type in ['xlsx','xls']:
                try:
                    df = pd.read_excel(f)
                    #A
                    df1 = df[(df['点击率(CTR)']>=0.1) & (df['7天的转化率']>0.1)]
                    df2 = df[(df['点击率(CTR)']>=0.1) & (df['7天的转化率']<=0.1) & (df['7天的转化率']>=0)]
                    df3 = df[(df['点击率(CTR)']<0.1) & (df['点击率(CTR)']>=0) & (df['7天的转化率']>0.1)]
                    df4 = df[(df['点击率(CTR)']<0.1) & (df['点击率(CTR)']>=0) & (df['7天的转化率']<=0.1) & (df['7天的转化率']>=0)]
                    df5 = df.groupby(['客户搜索词'])['点击率(CTR)'].mean()
                    df6 = df.groupby(['客户搜索词'])['点击量'].sum()
                    df7 = df.groupby(['客户搜索词'])['7天总订单数(#)'].sum()
                    #filename = str(datetime.datetime.now().month)+str(datetime.datetime.now().day)+str(datetime.datetime.now().hour)+str(datetime.datetime.now().minute)+str(datetime.datetime.now().second)+'.xlsx'
                    filename = 'static'+'/'+'广告分级.xlsx'
                    excel_writer = pd.ExcelWriter(filename,mode='w',engine='openpyxl')
                    df1.to_excel(excel_writer,sheet_name='A')
                    df2.to_excel(excel_writer,sheet_name='B')
                    df3.to_excel(excel_writer,sheet_name='C')
                    df4.to_excel(excel_writer,sheet_name='D')
                    df5.to_excel(excel_writer,sheet_name='客户搜索词点击率平均值汇总')
                    df6.to_excel(excel_writer,sheet_name='客户搜索词点击量总和')
                    df7.to_excel(excel_writer,sheet_name='客户搜索词订单数总和')
                    
                    excel_writer.save()
                    excel_writer.close()

                    msg = "处理成功 点击下载！"
                    messages.success(request,msg)

                    return render(request,'download.html',{})
                    
                except:
                    msg = '处理错误！'
                    return render(request,'upload1.html',{'msg':msg})
            else:
                msg = '上传文件错误,必须是Excel文件，检查后缀为xlsx,或xls。'
                return render(request,'upload1.html',{'msg':msg})
        else:
            msg = 'not post mode'
            return render(request,'upload1.html',{'msg':msg})
    else:
        return HttpResponse('请先登录！！')


def excel_upload(request):
    if request.session.get('userid'):
        if request.method == 'POST':
            f = request.FILES.get('my_file')
            excel_type = f.name.split('.')[-1]
            if excel_type in ['xlsx','xls']:
                try:
                    df = pd.read_excel(f)
                    data_array = np.array(df)
                    data_list = data_array.tolist()

                    conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',password='123456',database='ad',charset='utf8mb4')
                    try:
                        i = 0
                        for i in range(len(data_list)):
                            #数据清洗
                            if pd.isna(data_list[i][18]):
                                data_list[i][18]= 0
                                #print(data_list[i])
                            if pd.isna(data_list[i][15]):
                                data_list[i][15]= 0
                                #print(data_list[i])
                            if pd.isna(data_list[i][14]):
                                data_list[i][14]= 100
                                #print(data_list[i])
                            if pd.isna(data_list[i][10]):
                                data_list[i][10]= 0
                                #print(data_list[i])
                            if pd.isna(data_list[i][11]):
                                data_list[i][11]= 0
                                #print(data_list[i])

                            with conn.cursor() as cursor:
                                sql='''insert into `polls_ad` (`start_date`,`ad_group_name`,`currency`,`ad_campaign`,`ad_group`,`launch`,`matching_type`,`customer_search_terms`,`quantity_display`,`hits`,`ctr`,`cr`,`cost`,`total_sells`,`acos`,`roa`,`total_orders`,`total_sell_amount`,`conversition_rate`,`sku_sell_amount`,`un_sku_sell_amount`,`sku_sell`,`un_sku_sell`,`user`) \
                                    value('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' \
                                        %(data_list[i][0],data_list[i][1],data_list[i][2],data_list[i][3],data_list[i][4],escape_string(data_list[i][5]),(data_list[i][6]),escape_string(data_list[i][7]),(data_list[i][8]),data_list[i][9],data_list[i][10],data_list[i][11],data_list[i][12],data_list[i][13],data_list[i][14],data_list[i][15],data_list[i][16],data_list[i][17],data_list[i][18],data_list[i][19],data_list[i][20],data_list[i][21],data_list[i][22],request.session['name'])
                                    
                                affected_rows = cursor.execute(sql)
                                if affected_rows == 1:
                                    print(f'写入第{i+1}行!')
                                conn.commit()
                                
                        msg = '写入完成！'
                        return render(request,'upload2.html',{'msg':msg})
                    except pymysql.MySQLError as err:
                        print(err)
                        conn.rollback()
                    finally:
                        conn.close()
                    
                    msg = '事务未完成！  请检查EXCEL文件 数据格式为：日期，广告组名称，货币......'
                    return render(request,'upload1.html',{'msg':msg})
                    
                except:
                    msg = '处理错误！'
                    return render(request,'upload1.html',{'msg':msg})
            else:
                msg = '上传文件错误,必须是Excel文件，检查后缀为xlsx,或xls。'
                return render(request,'upload1.html',{'msg':msg})
        else:
            msg = 'not post mode'
            return render(request,'upload1.html',{'msg':msg})
    else:
        return HttpResponse('请先登录！！')


D_MULTI_SELECT = {
    '广告组合名称':'ad_group_name',
    # '广告活动名称':'ad_campaign',
    # '广告组名称':'ad_group',
    # '投放':'launch',
    '客户搜索词':'customer_search_terms',
    # '点击率':'ctr',
    # 'acos':'acos',

}

def data_analysis(request):
    try:
        query = AD.objects.filter(user=request.session['name']).values()
        df1 = pd.DataFrame(query)

        mselect_dict = {}

        try:
            for k,v in D_MULTI_SELECT.items():   

                mselect_dict[k]= {}
                mselect_dict[k]['select'] = v
                mselect_dict[k]['options'] = list(df1[v].unique())

            context = {
                'mselect_dict':mselect_dict,
            }
            return render(request,'subjects.html',context)
        except:
            for k,v in D_MULTI_SELECT.items():   
                mselect_dict[k]= {}
                mselect_dict[k]['select'] = v
            context = {
                'mselect_dict':mselect_dict,
            }
            return render(request,'subjects.html',context)

    except:
        return render(request,'subjects.html',{})

def search(request,column,kw):  #便于在筛选框中实现键入搜索
    try:
        queryson = AD.objects.filter(user=request.session['name']).values()
        df2 = pd.DataFrame(queryson)
        a = df2[column].unique().tolist()

        search = difflib.get_close_matches(kw,a)
        result_list = []
        for element in search:
            option_dict = {
                'name':element,
                'value':element
            }
            result_list.append(option_dict)
        res = {
            'success':True,
            'result':result_list,
            'code':200,
        }
    except Exception as e:
        res = {
            'success':False,
            'errMsg': e,
            'code':0,
        }
    
    return HttpResponse(json.dumps(res,ensure_ascii=False),content_type="application/json charset=utf-8")

def sqlparse(context):
    pass

class NpEncoder(json.JSONEncoder):   ######!!!!  numpy 格式json化方法 ---> Object of type int64 is not JSON serializable
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

# @cache_page(60*60*24*3) # 缓存3天
def query(request):
    
    try:
        queryson1 = AD.objects.filter(user=request.session['name']).values()
        df = pd.DataFrame(queryson1)
        form_dict = dict(six.iterlists(request.GET))
        print(form_dict)

        data_total_amount = df.count()[0] #数据总数

        try:
            data_total_cost = '$'+str(round(df['cost'].sum(),2))
            data_total_sell = '$'+str(round(df['total_sells'].sum(),2))

            dimension_selected = form_dict['DIMENSION_select'][0]
            period_selected = form_dict['PERIOD_select'][0]
            grade_selected = form_dict['UNIT_select'][0]

            #  图标绘制数据后端准备-----------折柱图
            if 'customer_search_terms_select[]' in form_dict:
                customer_search_selected = form_dict['customer_search_terms_select[]'][0]
                df=df.sort_values('start_date')

                data_search_ctr = list(df[df['customer_search_terms']==customer_search_selected]['ctr'])
                data_search_cr = list(df[df['customer_search_terms']==customer_search_selected]['conversition_rate'])
                data_search_hits = list(df[df['customer_search_terms']==customer_search_selected]['hits'])
                data_re = list(df[df['customer_search_terms']==customer_search_selected]['start_date'])
                data_search_date = list(map(lambda x:x.strftime("%Y-%m-%d"),data_re))
                data_lenth = len(data_search_ctr)
            else:
                data_search_ctr = []
                data_search_cr = []
                data_search_hits = []
                data_search_date = []
                data_lenth = []

            # 南丁格尔玫瑰图  [{value:*,name:*},{...},...]
            try:
                nighting = df.sort_values('total_sells',ascending=False,inplace=False).head(8)
                asearch=nighting[['total_sells','customer_search_terms']]
                b=asearch.drop_duplicates(subset='customer_search_terms',keep='first',inplace=False)
                total_sells = b['total_sells'].tolist()
                csearh = b['customer_search_terms'].tolist()
                dict1 = {}
                dict2 = {}
                dict3 = {}
                dict4 = {}
                dict5 = {}
                print(total_sells)
                print(csearh)
                dict1['value']=total_sells[0]
                dict1['name']=csearh[0]

                dict2['value']=total_sells[1]
                dict2['name']=csearh[1]

                dict3['value']=total_sells[2]
                dict3['name']=csearh[2]

                dict4['value']=total_sells[3]
                dict4['name']=csearh[3]

                dict5['value']=total_sells[4]
                dict5['name']=csearh[4]

                nightingal_list = [dict1,dict2,dict3,dict4,dict5]
            except:
                nighting = df.sort_values('total_sells',ascending=False,inplace=False).head(8)
                asearch=nighting[['total_sells','customer_search_terms']]
                b=asearch.drop_duplicates(subset='customer_search_terms',keep='first',inplace=False)
                total_sells = b['total_sells'].tolist()
                csearh = b['customer_search_terms'].tolist()
                dict1 = {}
                print(total_sells)
                print(csearh)
                dict1['value']=total_sells[0]
                dict1['name']=csearh[0]

                nightingal_list = [dict1]

        #  时间维度筛选 
            print(dimension_selected,period_selected,grade_selected)
            now = datetime.datetime.now().date()  #当下时间


            if period_selected == 'short':
                delta = -14
                
                df['start_date'] = df['start_date'].sub(now)
                df['start_date'] = df.apply(lambda x:x['start_date'].days,axis=1)
                df = df[df['start_date']>=delta]

                if grade_selected == 'level_a':
                    df = df[(df['ctr']>=0.1) & (df['conversition_rate']>0.1)]   # 高点击 高转化
                if grade_selected == 'level_b':
                    df = df[(df['ctr']<0.1) & (df['ctr']>=0) & (df['conversition_rate']>0.1)]  # 低点击 高转化
                if grade_selected == 'level_c':
                    df = df[(df['ctr']>=0.1) & (df['conversition_rate']<=0.1) & (df['conversition_rate']>=0)]  #高点击 低转化
                if grade_selected == 'level_d':
                    df = df[(df['ctr']<0.1) & (df['ctr']>=0) & (df['conversition_rate']<=0.1) & (df['conversition_rate']>=0)]  #全低
                    



            if period_selected == 'medium':
                delta_right = -14
                delta_left = -60

                df['start_date'] = df['start_date'].sub(now)
                df['start_date'] = df.apply(lambda x:x['start_date'].days,axis=1)
                df = df[df['start_date']>delta_left & df['start_date']<delta_right]

                if grade_selected == 'level_a':
                    df = df[df['conversition_rate']>0.2]   
                if grade_selected == 'level_b':
                    df = df[df['conversition_rate']<=0.2]  
                if grade_selected == 'level_c':
                    df = df[df['conversition_rate']<=0.2]  
                if grade_selected == 'level_d':
                    df = df[df['conversition_rate']<=0.2]  

            if period_selected == 'long':
                delta_l = -60

                df['start_date'] = df['start_date'].sub(now)
                df['start_date'] = df.apply(lambda x:x['start_date'].days,axis=1)
                df = df[df['start_date']<delta_l]

                if grade_selected == 'level_a':
                    df =df[df['acos']<=0.6]
                if grade_selected == 'level_b':
                    df = df[df['acos']>0.6]  
                if grade_selected == 'level_c':
                    df = df[df['acos']>0.6]
                if grade_selected == 'level_d':
                    df = df[df['acos']>0.6]


            df.columns = ['编号','开始日期','广告组名称','货币','广告活动','广告组','投放','匹配类型','客户搜索词','展示量','点击量','点击率','每次点击成本','花费','总销售额','acos','投入产出比','总订单数','总销售数量','转化率','SKU销售量','非SKU销售量','SKU销售额','非SKU销售额','姓名']

            if 'ad_group_name_select[]' in form_dict:
                ad_group_select = form_dict['ad_group_name_select[]'][0]
                df = df[df['广告组名称']==ad_group_select]

            df1 = df.groupby(['客户搜索词','投放'],as_index=False).sum()

            df1 = df.groupby(['客户搜索词']).first()
            column = ['投放','客户搜索词','广告组名称','展示量','点击量','点击率','转化率','总订单数','acos','花费']
            table = pd.DataFrame(df1,columns=column)

            context = {
                'data_total_amount':data_total_amount,
                'data_total_cost':data_total_cost,
                'data_total_sell':data_total_sell,
                'data_search_ctr':data_search_ctr,
                'data_search_cr':data_search_cr,
                'data_search_hits':data_search_hits,
                'data_search_date':data_search_date,
                'data_lenth':data_lenth,
                'ptable':table.to_html(classes='ui selectable celled table', table_id='ptable'),
                'nightingal':nightingal_list,
                
            
            }

            return HttpResponse(json.dumps(context, ensure_ascii=False,cls=NpEncoder), content_type="application/json charset=utf-8") # 返回结果必须是json格式
        except:
            context = {
                'data_total_amount':data_total_amount,
            }
            return HttpResponse(json.dumps(context, ensure_ascii=False,cls=NpEncoder), content_type="application/json charset=utf-8")
    except:
        return HttpResponse('请登录')

def export(request):
    
    queryson1 = AD.objects.filter(user=request.session['name']).values()
    df = pd.DataFrame(queryson1)
    form_dict = dict(six.iterlists(request.GET))
    print(form_dict)
    


    dimension_selected = form_dict['DIMENSION_select'][0]
    period_selected = form_dict['PERIOD_select'][0]
    grade_selected = form_dict['UNIT_select'][0]

        


    #  时间维度筛选 
    print(dimension_selected,period_selected,grade_selected)
    now = datetime.datetime.now().date()  #当下时间


    if period_selected == 'short':
        delta = -14
        
        df['start_date'] = df['start_date'].sub(now)
        df['start_date'] = df.apply(lambda x:x['start_date'].days,axis=1)
        df = df[df['start_date']>=delta]

        if grade_selected == 'level_a':
            df = df[(df['ctr']>=0.1) & (df['conversition_rate']>0.1)]   # 高点击 高转化
        if grade_selected == 'level_b':
            df = df[(df['ctr']<0.1) & (df['ctr']>=0) & (df['conversition_rate']>0.1)]  # 低点击 高转化
        if grade_selected == 'level_c':
            df = df[(df['ctr']>=0.1) & (df['conversition_rate']<=0.1) & (df['conversition_rate']>=0)]  #高点击 低转化
        if grade_selected == 'level_d':
            df = df[(df['ctr']<0.1) & (df['ctr']>=0) & (df['conversition_rate']<=0.1) & (df['conversition_rate']>=0)]  #全低
            



    if period_selected == 'medium':
        delta_right = -14
        delta_left = -60

        df['start_date'] = df['start_date'].sub(now)
        df['start_date'] = df.apply(lambda x:x['start_date'].days,axis=1)
        df = df[df['start_date']>delta_left & df['start_date']<delta_right]

        if grade_selected == 'level_a':
            df = df[df['conversition_rate']>0.2]   
        if grade_selected == 'level_b':
            df = df[df['conversition_rate']<=0.2]  
        if grade_selected == 'level_c':
            df = df[df['conversition_rate']<=0.2]  
        if grade_selected == 'level_d':
            df = df[df['conversition_rate']<=0.2]  

    if period_selected == 'long':
        delta_l = -60

        df['start_date'] = df['start_date'].sub(now)
        df['start_date'] = df.apply(lambda x:x['start_date'].days,axis=1)
        df = df[df['start_date']<delta_l]

        if grade_selected == 'level_a':
            df =df[df['acos']<=0.6]
        if grade_selected == 'level_b':
            df = df[df['acos']>0.6]  
        if grade_selected == 'level_c':
            df = df[df['acos']>0.6]
        if grade_selected == 'level_d':
            df = df[df['acos']>0.6]

    df.columns = ['编号','开始日期','广告组名称','货币','广告活动','广告组','投放','匹配类型','客户搜索词','展示量','点击量','点击率','每次点击成本','花费','总销售额','acos','投入产出比','总订单数','总销售数量','转化率','SKU销售量','非SKU销售量','SKU销售额','非SKU销售额','姓名']

    column = ['投放','客户搜索词','广告组名称','展示量','点击量','点击率','转化率','总订单数','acos','花费']
    table = pd.DataFrame(df,columns=column)
    excel_file = IO()
    excel_writer = pd.ExcelWriter(excel_file,mode='w',engine='openpyxl')
    table.to_excel(excel_writer, 'data', index=True)
    excel_writer.save()
    excel_writer.close()

    excel_file.seek(0)

    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # 设置文件名
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 当前精确时间不会重复，适合用来命名默认导出文件
    response['Content-Disposition'] = 'attachment; filename=' + now + '.xlsx'
    return response
    

def help(request):
    return render(request,'help.html',{})


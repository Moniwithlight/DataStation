"""vote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from polls import views

urlpatterns = [
    path('login/',views.login),
    path('admin/', admin.site.urls),
    path('logout/',views.logout),
    path('register/',views.register),
    path('upload/',views.upload),
    path('upload1/',views.excel_upload),
    path('',views.data_analysis,name='orgin'),
    path(r'search/<str:column>/<str:kw>',views.search,name='search'),
    path(r'query/',views.query,name='query'),
    path('upload2/',views.grade_upload),
    path('export/',views.export,name='export'),
    path('help/',views.help),
    
]



from django.urls import re_path, include
from application import views 

urlpatterns = [
    re_path(r'^mainpage$', views.pageproduct),
    re_path(r'^product$', views.product),
    # path('addhome',views.addHome),
]
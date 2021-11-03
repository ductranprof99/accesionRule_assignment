from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from application import utils
from django.http.response import JsonResponse
# Create your views here.
        
@api_view(['GET','POST'])
def addHome(request):
    """
    this thing for test add data
    """
    if request.method == 'GET':
        pass
        return  JsonResponse({'a':'a'}, safe=False,  status=status.HTTP_202_ACCEPTED)
from django.shortcuts import render
from requests.api import head
from rest_framework.decorators import api_view
from rest_framework import status
from application import utils
import requests
from bs4 import BeautifulSoup
from django.http.response import JsonResponse
# Create your views here.
        
@api_view(['GET','POST'])
def pageproduct(request):
    """
    this thing for test add data
    """
    if request.method == 'GET':
        page = request.GET.get('page')
        order = None
        direction = None
        order_response = request.data['order']
        if order_response != None:
            if order_response == 'gia tu cao xuong thap':
                order = 'price'
                direction = -1
            elif order_response == 'gia tu thap den cao':
                order = 'price'
                direction = 1
            elif order_response == 'xep hang giam dan':
                order = 'rating_average'
                direction = -1
            elif order_response == 'xep hang tang dan':
                order = 'rating_average'
                direction = 1
            
        if page != None and int(page)< 0:
            return  JsonResponse({}, safe=False,  status=status.HTTP_404_NOT_FOUND)
        listProdPerPage = utils.showProduct(0 if not page else int(page),order,direction)
        return  JsonResponse(listProdPerPage, safe=False,  status=status.HTTP_202_ACCEPTED)

@api_view(['GET','POST'])
def product(request):
    header = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
           'referer': None}
    if request.method == 'POST':
        # add to cart or something
        pass
    elif request.method == 'GET':
        # for get request
        # product_id = str(request.data['id'])
        product_id = '10409803'
        url_id = 'https://tiki.vn/api/v2/products/'+product_id
        header['referer'] = url_id
        product_info = requests.get(url_id,headers=header).json()
        soup = BeautifulSoup(product_info['description'])
        result = utils.showProductByID(product_id)
        result['description'] = soup.get_text('\n')
        return JsonResponse(result, safe=False,  status=status.HTTP_202_ACCEPTED)
        
    pass

@api_view(['GET','POST']) 
def cart(request):
    pass

def user(request):
    pass
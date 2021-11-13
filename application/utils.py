from django.core.mail import EmailMessage
from pymongo import MongoClient
import os
from json import dumps,loads
import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()
client = MongoClient(os.getenv('DATABASE_URL'))

db = client['smolARM']
# db.informations.update({},{'$rename':{'productset_group_name':'categories'}},multi=True,upsert=False)



def showProduct(N:int=0,order_response:str=None):
    direction = 1
    order_by = 'id'
    if order_response != None:
        if order_response == 'gia_tu_cao_xuong_thap':
            order_by = 'price'
            direction = -1
        elif order_response == 'gia_tu_thap_den_cao':
            order_by = 'price'
            direction = 1
        elif order_response == 'xep_hang_giam_dan':
            order_by = 'rating_average'
            direction = -1
        elif order_response == 'xep_hang_tang_dan':
            order_by = 'rating_average'
            direction = 1
    product_collection = db.products
    mydoc = product_collection.find({},{'_id':0,'price':1,'name':1,'id':1,'thumbnail_url':1,'rating_average':1})
    if order_response:
        mydoc= mydoc.sort(order_by,direction)
    return list(mydoc)[N*10:N*10+10:1]
    
def showProductByID(id):
    product_collection = db.products
    result = product_collection.aggregate(pipeline=[
        {'$match':{'id':int(id)}},
        {'$project':
            {
            '_id':0,
            'price':1,
            'original_price':1,
            'discount':1,
            'name':1,
            'id':1,
            'thumbnail_url':1,
            'rating_average':1
            }
        },
        {'$limit':1},
        {'$lookup':  {
            'from': "informations",
            'as': "information",
            'let': { "product_id": "$id" },
            'pipeline': [
                    { '$match': { 
                        '$expr': { '$eq': ["$$product_id", "$id"] },
                      } 
                    },
                    {'$limit':1},
                    {'$project':{
                        '_id':0,
                        'categories':1,
                        'review_count':1,
                        'images':1,
                        'is_fresh':1
                        }
                    }
                ]
            }
        }
        ]) 
    return list(result)[0]

def create_cart(user_email:str=None,user_id:int=None):
    users = db.application_user
    if not user_id:
        user_id = users.find_one({'email':user_email})['_id']
    cart_collection = db.cart
    cart_collection.insert_one({'user_email':user_id,'products':[], 'total_price':0,'categories':[]})

def update_cart(user_id:int,product_id:int,quantity:int):
    cart_collection = db.cart
    cart = cart_collection.find_one({'user_email':user_id})
    
    if cart == None:
        create_cart(user_id=user_id)
        cart = cart_collection.find_one({'user_email':user_id})
    products = cart['products']
    if quantity == 0:
        for i in range(0,len(products)):
            if products[i]['id'] == product_id:
                products.pop(i)
                break
    else:
        found = False
        for i in range(0,len(products)):
            if products[i]['id'] == product_id:
                products[i]['quantity'] = quantity
                found = True
                break
        if not found:
            products.append({'id':product_id,'quantity':quantity})
    total_price = 0
    categories = []
    for i in range(0,len(products)):
        x = get_price_and_category_product(products[i]['id'])
        total_price += products[i]['quantity'] * x[0]
        categories.append(x[1])
    cart_collection.update_one({'user_email':user_id},{'$set':{'products':products,'total_price':total_price,'categories':categories}})
    
def update_cart_products_list(user_email:str,products:list):
    users = db.application_user
    user_id = users.find_one({'email':user_email})['_id']
    cart_collection = db.cart
    total_price = 0
    categories = []
    for i in range(0,len(products)):
        x = get_price_and_category_product(products[i]['id'])
        total_price += products[i]['quantity'] * x[0]
        categories.append(x[1])
    cart_collection.update_one({'user_email':user_id},{'$set':{'products':products,'total_price':total_price,'categories':categories}}) 

def get_price_and_category_product(product_id):
    product_collection = db.products
    mydoc = product_collection.find({'id':product_id},{'_id':0,'price':1})
    category_collection = db.informations
    product_category = category_collection.find_one({'id':product_id},{'_id':0,'categories':1})
    return list(mydoc)[0]['price'],product_category['categories']
    
def update_rating(product_id,rating):
    product_collection = db.products
    mydoc = product_collection.find({'id':product_id},{'_id':0,'rating_average':1})
    point = list(mydoc)[0]['rating_average']
    inforamtion_collection = db.informations
    review_count = inforamtion_collection.find_one({'id':product_id},{'_id':0,'review_count':1})['review_count']
    avegare_point = (float)((int)(point * review_count + rating/ (review_count + 1))*2)/2
    inforamtion_collection.update_one({'id':product_id},{'$set':{'review_count':review_count+1}})
    product_collection.update_one({'id':product_id},{'$set':{'rating_average':avegare_point}})

def find_product_same_category(product_id):
    category_collection = db.informations
    product_category = category_collection.find_one({'id':product_id},{'_id':0,'categories':1})
    categories = product_category['categories']
    mydoc = category_collection.find({'categories':{'$in':categories}},{'_id':0,'id':1})
    return list(db.products.find({'id':{'$in':[x['id'] for x in mydoc]}},{'_id':0,'price':1,'name':1,'id':1,'thumbnail_url':1,'rating_average':1}))



def inspectError():
    for i in range(0,10):
        print('\n')
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    for i in range(0,10):
        print('\n')
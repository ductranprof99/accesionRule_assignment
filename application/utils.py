import datetime
from logging import captureWarnings
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
    mydoc = product_collection.find({},{'_id':0,'price':1,'name':1,'id':1,'thumbnail_url':1,'rating_average':1,'original_price':1})
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

def buy_products(user_id):
    cart_collection = db.cart
    time = datetime.datetime.now()
    date = time.strftime("%d-%m-%Y")
    time = time.strftime("%H:%M:%S")
    cart = cart_collection.find_one({'user_id':user_id})
    cart_collection.delete_one({'user_id':user_id})
    create_cart(user_id=user_id)
    transaction_insert_data = {'date':date,'time':time,'categories':cart['categories'],'total_price':cart['total_price']}
    db.transactions.insert_one(transaction_insert_data)



def create_cart(user_email:str=None,user_id:int=None):
    users = db.application_user
    if not user_id:
        user_id = users.find_one({'email':user_email})['id']
    cart_collection = db.cart
    cart_collection.insert_one({'user_id':user_id,'products':[], 'total_price':0,'categories':[]})

def update_cart_with_requst(request:dict):
    user_id = request['user_id']
    cart_collection = db.cart
    cart = cart_collection.find_one({'user_id':user_id})
    if cart == None:
        create_cart(user_id=user_id)
        cart = cart_collection.find_one({'user_id':user_id})
    cart_collection.update_one({'user_id':user_id},{'$set':{'products':cart['products'],'total_price':cart['total_price'],'categories':cart['categories']}})
    
    
def update_cart(user_id:int,product_id:int,quantity:int):
    cart_collection = db.cart
    cart = cart_collection.find_one({'user_id':user_id})
    if cart == None:
        create_cart(user_id=user_id)
        cart = cart_collection.find_one({'user_id':user_id})
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
        if x[1][-1] not in categories:
            categories.append(x[1][-1])
    cart_collection.update_one({'user_id':user_id},{'$set':{'products':products,'total_price':total_price,'categories':categories}})
    
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
    cart_collection.update_one({'user_id':user_id},{'$set':{'products':products,'total_price':total_price,'categories':categories}}) 

def get_price_and_category_product(product_id):
    product_collection = db.products
    mydoc = product_collection.find({'id':product_id},{'_id':0,'price':1})
    category_collection = db.informations
    product_category = category_collection.find_one({'id':product_id},{'_id':0,'categories':1})
    return list(mydoc)[0]['price'],product_category['categories']
    
def update_rating(user_id,product_id,rating):
    product_collection = db.products
    mydoc = product_collection.find({'id':product_id},{'_id':0,'rating_average':1})
    point = list(mydoc)[0]['rating_average']
    inforamtion_collection = db.informations
    review_count = inforamtion_collection.find_one({'id':product_id},{'_id':0,'review_count':1})['review_count']
    old_point = history_rating_search(user_id,product_id)
    if old_point != None:
        rating = rating - old_point
        avegare_point = (float)((int)(point * review_count + rating/ (review_count))*2)/2
    else:
        update_history_rating(user_id,product_id,rating)
        avegare_point = (float)((int)(point * review_count + rating)/ (review_count + 1))*2/2
    inforamtion_collection.update_one({'id':product_id},{'$set':{'review_count':review_count+1}})
    product_collection.update_one({'id':product_id},{'$set':{'rating_average':avegare_point}})

def history_rating_search(user_id:int,product_id:int):
    history_collection = db.history_rating
    user = history_collection.find_one({'user_id':user_id})
    if user == None:
        history_collection.insert_one({'user_id':user_id,'products':{}})
        return None
    if str(product_id) in user['products']:
        return user['products'][product_id]
    return None

def update_history_rating(user_id:int,product_id:int,rating:int):
    history_collection = db.history_rating
    history_collection.update_one({'user_id':user_id},{'$set':{'products':{str(product_id):rating}}})

def find_product_same_category(product_id):
    category_collection = db.informations
    product_category = category_collection.find_one({'id':product_id},{'_id':0,'categories':1})
    categories = product_category['categories']
    mydoc = category_collection.find({'categories':{'$in':categories}},{'_id':0,'id':1})
    return list(db.products.find({'id':{'$in':[x['id'] for x in mydoc]}},{'_id':0,'price':1,'name':1,'id':1,'thumbnail_url':1,'rating_average':1}).limit(20))

def get_cart(user_id):
    cart_collection = db.cart
    cart = cart_collection.find_one({'user_id':user_id},{'_id':0})
    if cart == None:
        create_cart(user_id=user_id)
        cart = cart_collection.find_one({'user_id':user_id},{'_id':0})
    return cart

def recommend_product(user_id):
    list_categories = get_recommended_product(user_id)
    if list_categories == None:
        return []
    result = []
    # from functools import reduce
    # result = reduce(get_product_by_categories,list_categories,result)
    for i in list_categories:
        result += get_product_by_categories(i)
    return result[:20]

def get_product_by_categories(categories:list):
    mydoc = db.informations.find({'categories':{'$in':categories}},{'_id':0,'id':1})
    return list(db.products.find({'id':{'$in':[x['id'] for x in mydoc]}},{'_id':0,'price':1,'name':1,'id':1,'thumbnail_url':1,'rating_average':1}).limit(20))

def get_recommended_product(user_id) -> list[list[str]]: 
    rules = db.rules
    rules_set_current = rules.find_one({},{'_id':0})
    cart = get_cart(user_id)
    categories = cart['categories']
    if len(categories) == None:
        return None
    antecedents = rules_set_current['antecedents']
    consequents = rules_set_current['consequents']
    list_key = compare_category_with_antecedents(categories,antecedents)
    return [consequents[x] for x in list_key if x in list_key]
    


def compare_category_with_antecedents(categories,antecedents):
    result = []
    for antecedent in antecedents:
        matches = len(set(categories).intersection(antecedents[antecedent]))
        if matches == 0:
            continue
        else:
            if matches/len(antecedents[antecedent]) > 0.3:
                # neu nhu ti le trung nhau lon hon 30% thi them vao list
                result.append(antecedent)
    return result

def inspectError():
    for i in range(0,10):
        print('\n')
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    for i in range(0,10):
        print('\n')
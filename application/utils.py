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
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
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
    
def inspectError():
    for i in range(0,10):
        print('\n')
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    for i in range(0,10):
        print('\n')
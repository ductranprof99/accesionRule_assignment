import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from pymongo import MongoClient
import os,json

client = MongoClient(os.getenv('DATABASE_URL'))
db = client['smolARM']

def read_mongo():
    """ Read from Mongo and Store into DataFrame """

    
    cursor = db['transactions'].find({},{'_id':0,'categories':1})
    list_doc = list(cursor)
    result = []
    for doc in list_doc:
        result.append(doc['categories'])
    return result

def main():
    # Read the data from the csv file
    
    transaction_list = read_mongo()

    # Create a transaction encoder
    te = TransactionEncoder()
    # Encode the dataframe
    te_ary = te.fit(transaction_list).transform(transaction_list)

    # # Convert the encoded dataframe to a dataframe
    df_te = pd.DataFrame(te_ary, columns=te.columns_)

    # Create the apriori model
    apriori_model = apriori(df_te, min_support=0.1, use_colnames=True)

    # Create the association rules
    association_rules_model = association_rules(apriori_model, metric='lift', min_threshold=1)

    # Print the results
    try:
        db.rules.remove({})
    except:
        pass
    db.rules.insert(json.loads(association_rules_model.to_json()))
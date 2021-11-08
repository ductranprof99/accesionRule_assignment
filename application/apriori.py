from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import association_rules, apriori
import pandas as pd
df = None
# data frame load from transaction collection
# transaction collection will have the form [Date, Atime, Transaction, Item, Year, Month, Day]

transaction_list = []
for i in df['Transaction']:
    tlist = list(set(df[df['Transaction']==i]['Item']))
    if len(tlist) > 0:
        transaction_list.append(tlist)
print(len(transaction_list))
te = TransactionEncoder()
te_ary = te.fit(transaction_list).transform(transaction_list)
df2 = pd.DataFrame(te_ary, columns=te.columns_)

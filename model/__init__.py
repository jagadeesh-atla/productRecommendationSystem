import pandas
import ast

import sys
sys.path.append("..")

from utils.generate_data import usersGenerated, productCategories, productsGenerated, interactionsGenerated

# users, userIds = usersGenerated
# products, productIds = productsGenerated
# interactions = interactionsGenerated

# users = pandas.DataFrame(users)
# products = pandas.DataFrame(products)
# interactions = pandas.DataFrame(interactions)

users = pandas.read_csv('data/users.csv').sample(frac=1, random_state=1024)
users.reset_index(drop=True, inplace=True)
users['preferences'] = users['preferences'].apply(ast.literal_eval)

# print(users.head())
# exit()

products = pandas.read_csv('data/products.csv').sample(frac=1, random_state=1024)
products.reset_index(drop=True, inplace=True)

interactions = pandas.read_csv('data/interactions.csv').sample(frac=1, random_state=1024)
interactions.reset_index(drop=True, inplace=True)

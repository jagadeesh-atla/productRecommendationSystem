# import pandas
from .users import users
from .products import products, category
from .interactions import interactions

usersGenerated = users(1000)
productsGenerated = products(10000)

interactionsGenerated = interactions(
    usersGenerated[1], productsGenerated[1]
    )

productCategories = category

# usersDf = pandas.DataFrame(usersGenerated[0])
# productsDf = pandas.DataFrame(productsGenerated[0])
# interactionsDf = pandas.DataFrame(interactionsGenerated)

# usersDf.to_csv("./data/inputs/users.csv", index=False)
# productsDf.to_csv("./data/inputs/products.csv", index=False)
# interactionsDf.to_csv("./data/inputs/interactions.csv", index=False)

# print('Data Generated at /data/inputs')

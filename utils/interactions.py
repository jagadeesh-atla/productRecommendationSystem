import random

def interactions(users, products):
    interactions = []

    for user in users:
        for _ in range(random.randint(5, 20)):
            interactions.append({
                'userId': user,
                'productId': random.choice(products),
                'score': random.randint(2, 5)
            })

    return interactions

if __name__ == '__main__':
    from products import products
    from users import users
    
    userIds = users(5)[1]
    productIds = products(5)[1]

    print(interactions(userIds, productIds))

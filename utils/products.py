from faker import Faker
from .uniqueNums import generateNums
import random

fake = Faker()
Faker.seed(1024)
random.seed(1024)

category = ['automotive', 'electronics',
            'sports', 'beauty', 'health',
            'home decor', 'clothing', 'food',
            'pets', 'books', 'toys']

def products(n=10000):
    products = []

    ids = generateNums(n, digits=7)
    random.shuffle(ids)

    names = [
        fake.word() for _ in range(n)
    ]

    for id, name in zip(ids, names):
        products.append({
            'productId': id,
            'productName': name,
            'category': random.choice(category),
            'description': fake.paragraph(nb_sentences=4),
            'rating': random.randint(1, 5),
            'popularity': random.randint(60, 100),
            'price': random.randint(100, 1000)
        })
    
    return products, ids

if __name__ == '__main__':
    print(products(5))

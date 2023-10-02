import random
from faker import Faker
from .uniqueNums import generateNums
from .products import category

fake = Faker()
Faker.seed(1024)
random.seed(1024)

def users(n=1000):
    users = []

    ids = generateNums(n, digits=10)
    random.shuffle(ids)

    names = [
        fake.unique.name() for _ in range(n)
    ]

    for id, name in zip(ids, names):
        users.append({
            'userId': id,
            'userName': name,
            'password': fake.word(),
            'preferences': random.sample(
            category, random.randint(1, 3)
            )
        })

    return users, ids

if __name__ == '__main__':
    print(users(5))
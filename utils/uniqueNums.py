import random

random.seed(1024)

def generateNums(n, digits=7):
    nums = set()
    while len(nums) < n:
        nums.add(
            random.randint(10 ** digits,
                           10 ** (digits + 1) -1)
        )
    return list(nums)

if __name__ == '__main__':
    print(generateNums(5, digits=3))
import random


def gen_result():
    x = 10
    y = 80
    res = []
    print('_' * y)
    for i in range(x):
        for j in range(y):
            if random.random() > 0.015:
                res += ['_']
                print(' ', end='')
            else:
                c = random.choice('.*\'`,o')
                res += [c]
                print(c, end='')
        print()
    print('_' * y)
    return res


gen_result()

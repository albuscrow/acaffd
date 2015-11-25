print('hello world')
n = 6
for i in range(n + 1):
    for j in range(i + 1):
        u = (n - i) / n
        v = (i - j) / n
        w = 1 - u - v
        print('{%f, %f, %f},'%(u, v, w))
    print()

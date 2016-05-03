import numpy as np

a = np.array([
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, -0.8333333333333334, 3.0, 0.0, -1.5, 0.0, 0.3333333333333333, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, -0.8333333333333334, 0.0, 3.0, 0.0, -1.5, 0.0, 0.0, 0.0, 0.3333333333333333,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.3333333333333333, -1.5, 0.0, 3.0, 0.0, -0.8333333333333334, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.4390243902439024, 0.0, 0.0, 0.6585365853658537, 0.6585365853658537, 0.0, 0.0,
    0.6585365853658537, 0.8780487804878049, 0.6585365853658537, 0.0, 0.0, 0.4390243902439024, 0.6585365853658537,
    0.6585365853658537, 0.4390243902439024, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2784552845528455,
    -0.9969512195121951, -0.9969512195121951, -0.9969512195121951, -0.9969512195121951, 0.2784552845528455,
    -0.9969512195121951, -0.9969512195121951, 0.2784552845528455,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.3333333333333333, 0.0, -1.5, 0.0, 3.0, 0.0, 0.0, 0.0, -0.8333333333333334,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.8333333333333334, 3.0, -1.5, 0.3333333333333333,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3333333333333333, -1.5, 3.0, -0.8333333333333334,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]).reshape((10, 37))
# for i in a:
#     print(i)

aux = [0, 3, 5, 10, 14, 21, 23, 25, 27]
for i in range(9):
    a[:, aux[i]] += a[:, 28 + i]

# for j in range(28):
#     print('%16.7f' % j, end=', ')

aux2 = []
for i in range(28):
    if all(a[:, i] == 0):
        aux2.append(i)
print(aux2)

for i, aa in enumerate(a):
    for jj, j in enumerate(aa[:28]):
        if jj in aux2:
            continue
        print('%16.7f' % j, end=', ')
    print()
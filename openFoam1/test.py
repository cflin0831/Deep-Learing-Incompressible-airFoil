import numpy as np
import os

a0 = os.listdir('./data1/')
a0 = a0[0]
a1 = './data1/' + a0
a = np.load(a1)
file=f'{a0.split(".npy")[0]}.dat'

with open('newData/newpoint', 'wt') as Of:
    for i in range(len(a)):
        line = str(a[i][0])
        line1 = str(a[i][1])
        Of.write(line + ' ' + line1 +'\n')
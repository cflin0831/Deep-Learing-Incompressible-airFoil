import numpy as np
import os

with open('0/ICnBC', 'rt') as If:
    with open('0/velo', 'wt') as Of:
        for i in If:
            if i[0] == '/':
                continue
            elif i[0] == '#':
                continue
            elif i [0] == 'P':
                continue
            else:
                i = str(i)
                i = i.replace('Vx', '')
                i = i.replace('Vy', '')
                i = i.replace(';', '')
                i = i.replace(' ', '')
                Of.write(i + '\n')

a = np.loadtxt('0/velo')
print(a[0])
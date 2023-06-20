import numpy as np
import os

# a0 = os.listdir('./data1/')
# a0 = a0[0]
# a1 = './data1/' + a0
# a = np.load(a1)
# file=f'{a0.split(".npy")[0]}.dat'

# with open('newData/newpoint', 'wt') as Of:
#     for i in range(len(a)):
#         line = str(a[i][0])
#         line1 = str(a[i][1])
#         Of.write(line + ' ' + line1 +'\n')

a0 = os.listdir('postProcessing/newCloud')
a1 = os.listdir('postProcessing/boundaryCloud')
b = np.loadtxt("numberdata/number1")
b2 = np.loadtxt("numberdata/numberf")
print(str(int(b2)))
# print(int(max(b)))

b1 = int((max(b)))
# print(b1)
# print(a0[0])
# print(a0[10] == str(702))
for i in range(len(a0)):
    if a0[i] != str((int(b2))):
        # print(a0[i])
        os.system(f'rm -r postProcessing/newCloud/{a0[i]}')
    else:
        continue

for n in range(len(a1)):
    if a1[n] != str(b1):
        # print(a0[i])
        os.system(f'rm -r postProcessing/boundaryCloud/{a1[n]}')
    else:
        continue
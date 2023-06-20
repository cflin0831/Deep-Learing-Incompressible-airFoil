import numpy

a=numpy.load('goe770.npy')
# a=numpy.append(a[0])
# print(a)
# print(a[0])
list=list(a)
# xlist=numpy.split(list(a), 2, 1)
print(len(list))

path = 'internalCloudfoam1'

with open(f'{path}', 'a') as of:
    of.write('pts\n')
    of.write('(\n')
    for i in range(len(list)):
        xlist=list[i][0]
        ylist=list[i][1]
    # print(xlist)
    
        of.write(f'({xlist}  {ylist}  0.5)\n')
        # of.write(f'{list[0][0]}  {list[0][1]}')
    of.write(');\n')

# print(list)


import os
import csv
import numpy as np
import matplotlib.pyplot as plt
# from collections import Counter
# from scipy.interpolate import interpid


def interpolate_point(x_list1, y_list1, x):
    """
    Interpolate a point from a set of points given its x-coordinate.

    Args:
    x_list1 (list): A list of x-coordinates.
    y_list1 (list): A list of y-coordinates.
    x (float): The x-coordinate of the point to be interpolated.

    Returns:
    float: The y-coordinate of the interpolated point.
    """
    n = len(x_list1)
    if x < x_list1[0] or x > x_list1[-1]:
        x_list1[0] = y_list1[0]
        x_list1[-1] = y_list1[-1]
        # raise ValueError("x-coordinate is out of range")
    for i in range(n-1):
        if x >= x_list1[i] and x <= x_list1[i+1]:
            y = linear_interpolation(x_list1[i], y_list1[i], x_list1[i+1], y_list1[i+1], x)
            return y

def linear_interpolation(x1, y1, x2, y2, x):
    """
    Perform linear interpolation between two points.

    Args:
    x1 (float): The x-coordinate of the first point.
    y1 (float): The y-coordinate of the first point.
    x2 (float): The x-coordinate of the second point.
    y2 (float): The y-coordinate of the second point.
    x (float): The x-coordinate of the point to be interpolated.

    Returns:
    float: The y-coordinate of the interpolated point.
    """
    y = y1 + (y2-y1)/(x2-x1)*(x-x1)
    return y

x_list1 = np.loadtxt('all_temp/posi_y/shear_posix')
y_list1 = np.loadtxt('all_temp/posi_y/shear_posis')
x_list2 = np.loadtxt('all_temp/neg_y/shear_negx')
y_list2 = np.loadtxt('all_temp/neg_y/shear_negs')
velo = np.loadtxt('0/velo')
# print(velo)


y_list1 = y_list1/((velo[0]**2 + velo[1]**2)*0.5)
y_list2 = y_list2/((velo[0]**2 + velo[1]**2)*0.5)


xp = np.arange(0.005, 0.1, 0.005)
xp1 = np.arange(0.1, 0.99, 0.03)
# print(xp1)
# print(len(x))


xn = np.arange(0.005, 0.1, 0.005)
xn1 = np.arange(0.1, 0.99, 0.03)
# print(x[0])
# print(x)

with open('all_temp/final/shearposi', 'wt') as Of:
    Of.write('0' + ' ' + '0'+ '\n')
    for i in range(len(xp)):
        line = str(round(xp[i], 5))
        y = interpolate_point(x_list1, y_list1, xp[i])
        line1 = str(round(y,5))
        Of.write(line + ' '+ line1 +'\n')

    for i1 in range(len(xp1)):
        line = str(round(xp1[i1], 5))
        y = interpolate_point(x_list1, y_list1, xp1[i1])
        line1 = str(round(y,5))
        Of.write(line + ' '+ line1 +'\n')
    
    linex0 = str(1)
    liney0 = str(round(y_list1[-1], 5))
    Of.write(linex0 + ' '+ liney0 + '\n')


t = np.loadtxt('all_temp/final/shearposi')
# print(t[1][1])
with open('all_temp/final/shearposi1', 'wt') as Of:
    for i in range(len(t)):
        line = str(t[i][0])
        Of.write(line + '\n')

with open('all_temp/final/shearposi2', 'wt') as Of:
    t1 = np.loadtxt('all_temp/final/shearposi1')
    t1 = sorted(t1, reverse=True)
    for i in range(len(t1)):
        line = str(t1[i])
        Of.write(line + '\n')

with open('all_temp/final/shearposif', 'wt') as Of:
    t2 = np.loadtxt('all_temp/final/shearposi2')
    t = np.loadtxt('all_temp/final/shearposi')
    c1=np.split(t, 2, 1)
    s = np.zeros((len(t2), 1))
    xc1 = c1[0]
    xc2 = c1[1]
    for i in range(len(t2)):
        if t2[i] in xc1:
            result0 = np.where(xc1==t2[i])
            s[i] = xc2[result0]
            line = str(t2[i])
            line2 = str(s[i])
            line2 = line2.replace("[", "")
            line2 = line2.replace("]", "")
            Of.write(line + ' ' + line2 + '\n')



with open('all_temp/final/shearneg', 'wt') as Of:
    for i in range(len(xn)):
        # linex0 = str(x_list1[0])
        # liney0 = str(y_list1[0])
        # Of.write(linex0 + ' ' + liney0)
        line = str(round(xn[i], 5))
        y1 = interpolate_point(x_list2, y_list2, xn[i])
        line1 = str(round(y1, 5))
        Of.write(line + ' '+ line1 +'\n')

    for i2 in range(len(xn1)):
        line = str(round(xn1[i2], 5))
        y1 = interpolate_point(x_list2, y_list2, xn1[i2])
        line1 = str(round(y1, 5))
        Of.write(line + ' '+ line1 +'\n')

    linex0 = str(1)
    liney0 = str(round(y_list2[-1], 5))
    Of.write(linex0 + ' '+ liney0)


with open('all_temp/final/shearfinal', 'wt') as Of:
    f1 = np.loadtxt('all_temp/final/shearposif')
    f2 = np.loadtxt('all_temp/final/shearneg')
    for i in range(len(f1)):
        line = str(f1[i])
        line = line.replace("[", "")
        line = line.replace("]", "")
        Of.write(line + '\n')

with open('all_temp/final/shearfinal', 'a') as Of:
    f2 = np.loadtxt('all_temp/final/shearneg')
    for i in range(len(f2)):
        line = str(f2[i])
        line = line.replace("[", "")
        line = line.replace("]", "")
        Of.write(line + '\n')

k = np.loadtxt('all_temp/final/shearfinal')
print(len(k))


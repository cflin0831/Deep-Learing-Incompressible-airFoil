################
# Write out what a file represents
# 'boundary_temp' :  mean number of 'nface' of each boundary
# 'face_temp' : mean number of points in each 'face'
# 'face_temp1' : mean number of points in the 'face' of aerofoil
# 'points_temp' : mean all 'point' coordinate(xyz director)
# 'points_temp2' : mean all 'point' coordinate(xyz director) of the 'faces' of aerofoil 
################
import numpy as np
import matplotlib.pyplot as plt
import os

# check number of faces on pathes named aerofoil
with open("constant/polyMesh/boundary", "rt") as If:
    # write a data to show it
    with open("all_temp/boundary_temp", "wt" ) as Of:
        # Delete text except nface
        for line in If:
            if line[0] != " " :
                continue
            else:
                line = line.replace("    ", "")
                line = line.replace("version 2.0;", "")
                line = line.replace("format  ascii;", "")
                line = line.replace("class   polyBoundaryMesh;", "")
                line = line.replace("{", "")
                line = line.replace("}", "")
                if line[0] != "n":
                    continue
                else:
                    # write down the number after nface
                    line = line.replace("nFaces  ", "")
                    line = line.replace(";", "")
                    Of.write(line)

# Write down the node numbers of all bounding mesh elements
with open('constant/polyMesh/faces', "rt") as If:
    with open('all_temp/face_temp', 'wt') as Of:
        for line in If:
            if line[0] == "4":
                line = line.replace("4(", "")
                line = line.replace(")", "")
                Of.write(line)
            else:
                continue

# Find the node numbers that represent the individual unit elements of aerofoil
with open('all_temp/face_temp', "rt") as If:
    with open('all_temp/face_temp1', 'wt') as Of:
        a0 = np.loadtxt('all_temp/boundary_temp')   
        # Because in GMSH, aerofoil is defined as the last boundary, so take the last value of the previous file, which is the number of nfaces of aerofoil
        a0 = int(a0[-1])
        a1 = np.loadtxt('all_temp/face_temp', skiprows=1)
        # The original file is the same as all borders, this step is to take the last border aerofoil
        a2 = a1[(len(a1)-a0): len(a1)]
        for i in range(len(a2)):
            list = [int(a2[i][0]), int(a2[i][1]), int(a2[i][2]), int(a2[i][3])]
            line = str(list)
            line = line.replace("[", "")
            line = line.replace("]", "")
            line = line.replace(",", "")
            Of.write(line +"\n")

# write down all of the 'point' coordinate(xyz director)
with open('constant/polyMesh/points', 'rt') as If:
    with open('all_temp/points_temp', 'wt') as Of:
        for line in If:
            if line[0] != "(" :
                continue
            else:
                line = line.replace("(", "")
                line = line.replace(")", "")
                Of.write(line)

# write down all of the 'point' coordinate(xyz director) of the 'faces' of aerofoil
with open('all_temp/points_temp2', 'wt') as Of:
    a3 = np.loadtxt('all_temp/points_temp')
    a4 = np.loadtxt('all_temp/face_temp1')
    print(a4[0][0], a4[0][1])
    for i in range(len(a4)):
        Of.write(str(a3[int(a4[i][0])][0]) + " " + str(a3[int(a4[i][1])][0]) + ' ' + str(a3[int(a4[i][0])][1]) + " " + str(a3[int(a4[i][1])][1]) + '\n')
            
# write down all  of wallShearStress 
with open('900/wallShearStress', 'rt') as If:
    with open('all_temp/shear', 'wt') as Of:
        for line in If:
            if line[0] != "(" :
                continue
            else:
                line = line.replace("(" , "")
                line = line.replace(")", "")
                Of.write(line)

# write down all of wallShearStress value
with open('all_temp/shear_mag', 'wt') as Of:
    a5 = np.loadtxt('all_temp/shear')
    for i in range(len(a5)):
        # if a5[i][1] > 0 :
        line = ((a5[i][0])**2+(a5[i][1])**2)**(1/2)
        line = str(line)
        # else :
        #     line = 0
        #     line = str(line)
            # if a5[i][1] > a5[i][0] : 
            #     line = ((a5[i][0])**2 - (a5[i][1])**2)**(1/2)
            #     line = str(line)
            # else : 
            #     line = (((a5[i][1])**2 - (a5[i][0])**2))**(1/2)
            #     line = str(line)
        Of.write(line + "\n")

# take the value of wallShearStress and all aerofoil element faces 'point' coordinate(xyz director) together
with open('all_temp/shearList', 'wt') as Of:
    a6 = np.loadtxt('all_temp/shear_mag')
    a7 = np.loadtxt('all_temp/points_temp2')
    for i in range(len(a6)):
        list = [a7[i][0], a7[i][1], a7[i][2], a7[i][3], a6[i]]
        line = str(list)
        line = line.replace("[", "")
        line = line.replace("]", "")
        line = line.replace(",", "")
        Of.write(line + "\n")

# write the topper surface element of aerofoil
with open('all_temp/posi_y/shear_posi', 'wt') as Of:
    a8 = np.loadtxt('all_temp/shearList')
    # print(a8[0][1])
    for i in range(len(a8)):
        if a8[i][0] == a8[i][1]:
            continue
        else:
            if a8[i][3] >=  0 :
                list = [round(a8[i][0], 5), round(a8[i][1], 5), round(a8[i][2], 5), round(a8[i][3], 5), a8[i][4], 5]
            # print(list[0])
                line = str(list)
                line = line.replace("[", "")
                line = line.replace("]", "")
                line = line.replace(",", "")
                Of.write(line + '\n')

# write the x dir and value of wallShearStress in the same data
with open('all_temp/posi_y/shear_posi1', 'wt') as Of:
    a9 = np.loadtxt('all_temp/posi_y/shear_posi')
    for i in range(len(a9)):
        line = str(a9[i][0])
        line1 = str(a9[i][1])
        line2 = str(a9[i][4])
        line = line.replace("[", "")
        line = line.replace("]", "")
        line = line.replace(",", "")
        Of.write(line + ' ' + line1 + ' ' + line2 +'\n')

# write the x1 dir in this data only
with open('all_temp/posi_y/shear_posi2', 'wt') as Of:
    a9 = np.loadtxt('all_temp/posi_y/shear_posi')
    for i in range(len(a9)):
        # if a9[i][0] == a9[i][1]:
        #     continue
        # else:
        line = str(a9[i][0])
        line = line.replace("[", "")
        line = line.replace("]", "")
        line = line.replace(",", "")
        Of.write(line + '\n')

# Arrange the values ​​of the x coordinates from small to large
with open('all_temp/posi_y/shear_posi3', 'wt') as Of:
    b1 = np.loadtxt('all_temp/posi_y/shear_posi2')
    b1 = sorted(b1)
    for i in range(len(b1)):
        line = b1[i]
        line = str(line)
        Of.write(line + "\n")

# Find the value of wallShearStress corresponding to the x-coordinate
with open('all_temp/posi_y/shear_posif', 'wt') as Of:
    b2 = np.loadtxt('all_temp/posi_y/shear_posi1')
    b3 = np.loadtxt('all_temp/posi_y/shear_posi3')
    c1=np.split(b2, 3, 1)
    xc0=np.zeros((len(b3), 1)) 
    ss1=np.zeros((len(b3), 1))
    xc1 = c1[0]
    xc2 = c1[1]
    xc3 = c1[2]
    for i in range(len(b3)):
        if b3[i] in xc1:
            result0 = np.where(xc1==b3[i])
            xc0[i] = xc2[result0]
            result = np.where(xc1==b3[i])
            ss1[i] = xc3[result0]
            line = str(b3[i])
            line2 = str(xc0[i])
            line2 = line2.replace("[", "")
            line2 = line2.replace("]", "")
            line3 = str(ss1[i])
            line3 = line3.replace("[", "")
            line3 = line3.replace("]", "")
            Of.write(line+ ' ' + line2 + ' ' + line3 + '\n')

with open('all_temp/posi_y/shear_posis', 'wt') as Of:
    p1 = np.loadtxt('all_temp/posi_y/shear_posif')
    for i in range(len(p1)):
        line = str(p1[i][2])
        Of.write(line + '\n')

with open('all_temp/posi_y/shear_posix', 'wt') as Of:
    p1 = np.loadtxt('all_temp/posi_y/shear_posif')
    for i in range(len(p1)):
        list = [round((p1[i][0] + p1[i][1])*0.5, 5)]
        # print(list[0])
        line = str(list)
        line = line.replace("[", "")
        line = line.replace("]", "")
        Of.write(line + '\n')


with open('all_temp/neg_y/shear_neg', 'wt') as Of:
    a8 = np.loadtxt('all_temp/shearList')
    # print(a8[0][1])
    for i in range(len(a8)):
        if a8[i][3] <=  0 :
            list = [round(a8[i][0], 5), round(a8[i][1], 5), round(a8[i][2], 5), round(a8[i][3], 5), a8[i][4], 5]
            # print(list[0])
            line = str(list)
            line = line.replace("[", "")
            line = line.replace("]", "")
            line = line.replace(",", "")
            Of.write(line + '\n')


with open('all_temp/neg_y/shear_neg1', 'wt') as Of:
    n2 = np.loadtxt('all_temp/neg_y/shear_neg')
    for i in range(len(n2)):
        if n2[i][0] == n2[i][1]:
            continue
        else:
            line = str(n2[i][0])
            line1 = str(n2[i][1])
            line2 = str(n2[i][4])
            line = line.replace("[", "")
            line = line.replace("]", "")
            line = line.replace(",", "")
            Of.write(line + ' ' + line1 + ' ' + line2 +'\n')


with open('all_temp/neg_y/shear_neg2', 'wt') as Of:
    n3 = np.loadtxt('all_temp/neg_y/shear_neg1')
    for i in range(len(n3)):
        line = str(n3[i][0])
        line = line.replace("[", "")
        line = line.replace("]", "")
        line = line.replace(",", "")
        Of.write(line + '\n')

with open('all_temp/neg_y/shear_neg3', 'wt') as Of:
    n4 = np.loadtxt('all_temp/neg_y/shear_neg2')
    n4 = sorted(n4)
    for i in range(len(n4)):
        line = n4[i]
        line = str(line)
        Of.write(line + "\n")


with open('all_temp/neg_y/shear_negx', 'wt') as Of:
    n8 = np.loadtxt('all_temp/neg_y/shear_neg1')
    for i in range(len(n8)):
        list = [round((n8[i][0] + n8[i][1])*0.5, 5)]
        # print(list[0])
        line = str(list)
        line = line.replace("[", "")
        line = line.replace("]", "")
        Of.write(line + '\n')


with open('all_temp/neg_y/shear_negf', 'wt') as Of:
    n5 = np.loadtxt('all_temp/neg_y/shear_neg1')
    n6 = np.loadtxt('all_temp/neg_y/shear_neg3')
    n9 = np.loadtxt('all_temp/neg_y/shear_negx')
    c1=np.split(n5, 3, 1)
    xc0=np.zeros((len(n6), 1)) 
    ss1=np.zeros((len(n6), 1))
    xc1 = c1[0]
    xc2 = c1[1]
    xc3 = c1[2]
    for i in range(len(n6)):
        if n6[i] in xc1:
            result0 = np.where(xc1==n6[i])
            xc0[i] = xc2[result0]
            result = np.where(xc1==n6[i])
            ss1[i] = xc3[result0]
            line = str(n9[i])
            line2 = str(xc0[i])
            line2 = line2.replace("[", "")
            line2 = line2.replace("]", "")
            line3 = str(ss1[i])
            line3 = line3.replace("[", "")
            line3 = line3.replace("]", "")
            Of.write(line+ ' ' + line2 + ' ' + line3 + '\n')

    
with open('all_temp/neg_y/shear_negs', 'wt') as Of:
    n2 = np.loadtxt('all_temp/neg_y/shear_neg')
    n7 = np.loadtxt('all_temp/neg_y/shear_negf')
    for i in range(len(n7)):
        line = str(n7[i][2])
        Of.write(line + '\n')

################
#
# Deep Flow Prediction - N. Thuerey, K. Weissenov, H. Mehrotra, N. Mainali, L. Prantl, X. Hu (TUM)
#
# Generate training data via OpenFOAM
#
# https://github.com/thunil/Deep-Flow-Prediction/blob/master/data/dataGen.py
#
################

import os, math, uuid, sys, random, time
import numpy as np
import utils
import multiprocessing as mp

samples     = 30       # no. of datasets to product
freestream_angle = math.pi / 18.        # angle
# freestream_angle = 10
Mach_number_factor_low = 0.05
Mach_number_factor_high = 0.2   # mach number factor
cpu_to_use = 32 

airfoil_database = "./airfoil_database/"    # the database we used (we choose only one this time)
output_dir = "./training1/"                  # output name of database

utils.makeDirs([output_dir])

files = os.listdir("./airfoil_database/")
files.sort()
if len(files)==0:
    print("error - no airfoils found in %s" % airfoil_database)
    exit(1)

seed = random.randint(0, 2**32 - 1)
np.random.seed(seed)
print("Seed: {}".format(seed))

def newPoint():   
    # os.system is like a string entered in the terminal
    os.system('python3 splineFinal.py')
    os.system('python3 test.py')
    os.system('rm -r data0')
    os.system('rm -r data1')
    a = os.listdir('./newData/')
    a1 = a[0]
    a2 = './newData/' + a1
    a3 = np.loadtxt(a2)
    output1 = ""
    for n in range(a3.shape[0]):
        output1 += "( {}  {}  0.005)\n".format(a3[n][0], a3[n][1])
    
    # Find these internalCloud points, which may be used later in surface pressure or shear stress
    with open('system/internalCloudFoam_temp', "rt") as inFile:
        with open("system/internalCloud0", "wt") as outFile:
            for line in inFile:
                    line = line.replace("points","{}".format(output1))
                    outFile.write(line)

    return(0)

def genMesh(airfoilFile):
    ar = np.loadtxt(airfoilFile, skiprows=1)

    # There are two different shapes of airfoils, with different mesh making methods
    if ar[0][1]-ar[-1][1] != 0:
        if np.max(np.abs(ar[0]-ar[(ar.shape[0]-2)]))<1e-6:
            ar = ar[:-1]

        output = ""
        pointIndex = 1000
        for n in range(ar.shape[0]):
            output += "Point({}) = {{ {}, {}, 0.000000, 0.0025}};\n". format(pointIndex, ar[n][0], ar[n][1])
            pointIndex += 1

        with open("airfoil_template.geo", "rt") as inFile:
            with open("airfoil.geo", "wt") as outFile:
                for line in inFile:
                    line = line.replace("POINTS", "{}".format(output))
                    line = line.replace("LAST_POINT_INDEX", "{}".format(pointIndex-1))
                    line = line.replace("final", "{}".format(pointIndex-2))
                    outFile.write(line)

    else:
        if np.max(np.abs(ar[0]-ar[(ar.shape[0]-2)]))<1e-6:
            ar = ar[:-1]

        output = ""
        pointIndex = 1000
        for n in range(ar.shape[0]):
            output += "Point({}) = {{ {}, {}, 0.000000, 0.0025}};\n". format(pointIndex, ar[n][0], ar[n][1])
            pointIndex += 1

        with open("airfoil_template1.geo", "rt") as inFile:
            with open("airfoil.geo", "wt") as outFile:
                for line in inFile:
                    line = line.replace("POINTS", "{}".format(output))
                    line = line.replace("LAST_POINT_INDEX", "{}".format(pointIndex-1))
                    line = line.replace("final", "{}".format(pointIndex-2))
                    outFile.write(line)

    # Convert the built .geo file to .msh file
    if os.system( "gmsh airfoil.geo -3 -format msh2 airfoil.msh > /dev/null" ) != 0:   # if it error during mesh creation, /dev/null(導向垃圾桶) it==0(correct)
        print("error during mesh creation!")
        return(-1)
    
    # Convert the .msh file to the polyMesh folder to be used
    if os.system("gmshToFoam airfoil.msh > /dev/null")!=0:
        print("error during coversion to OpenFoam mesh")
        return(-1)

    # Change patch to match empty and wall
    with open("constant/polyMesh/boundary", "rt") as iF:
        with open("constant/polyMesh/boundaryTemp", "wt") as oF:
            inArea = False
            inAerofoil = False
            for line in iF:
                if "front" in line or "back" in line:
                    inArea = True
                elif "aerofoil" in line:
                    inAerofoil = True
                elif inArea and "type" in line:
                    line = line.replace("patch", "empty")
                    inArea = False
                elif inAerofoil and "type" in line:
                    line = line.replace("patch", "wall")
                    inAerofoil = False
                oF.write(line)
    os.rename("constant/polyMesh/boundaryTemp", "constant/polyMesh/boundary")
    return(0)


def runSim(freestreamX, freestreamY, pressure=1e5):
    # This list contains Ux, Uy and P 
    list = [f'Vx     {freestreamX: .2f};', f'Vy           {freestreamY:.2f};',  f'Pressure     {pressure};' ]

    # in data 'ICnBC' contaons Ux,Uy and P
    with open("0/ICnBC", "wt") as oF:
        oF.write('//Initial and boundary conditions for flow field\n')
        for i in range(len(list)):
            oF.write(list[i]+'\n')
        oF.write('#inputMode merge\n')
    status = os.system("./Allclean && simpleFoam > foam.log")
    return status

# This step is mainly to discharge the folders written by all the steps
def find(id):
    a = os.listdir(f'./{id}/') 

    # Just write the folders related to the number of time steps, and don’t read the rest of the python files
    with open(f'{id}/numberdata/number', 'wt') as Of:
        for i in range(len(a)):
            if len(a[i]) > 4:
                continue
            else:
                line = str(a[i])
                Of.write(line + '\n')

    with open(f'{id}/numberdata/number1', 'wt') as outFile:
        b = np.loadtxt(f'{id}/numberdata/number')
        b1 = sorted(b)
        for i in range(len(b)):
            line1 = str(b1[i])
            outFile.write(line1 + '\n')

    with open(f'{id}/numberdata/numberf', 'wt') as OutFile:
        c = np.loadtxt(f'{id}/numberdata/number1')
        if c[-1] % 100 == 0:
            line2 = str(int(c[-1]))
        else:
            line2 = str(int(c[-2]))
        OutFile.write(line2)

    return(0)

# This step is mainly to find the shear force value  by the surface grid 
def wallShear():
    status = os.system("python3 shear.py")
    return status

def tidy():
    status = os.system("python3 tidy.py")
    return status

# Convert the shear force value to dimensionless Cf
def Cf():
    status = os.system('python3 velocity.py')
    return status

# The Cf value of the branch surface grid will be calculated and interpolated to the 101 wing surface coordinate points input in the database
def shearInterpolation():
    status = os.system("python3 interpolation.py")
    return status

def outputProcessing(basename, freestreamX, freestreamY, cpu_id, dataDir=output_dir, res=256):
    print('*** in op ****')
    print(os.getcwd())
    paths_pCoe=os.listdir(f'{cpu_id}/postProcessing/boundaryCloud')
    paths_ptfile =os.listdir(f'{cpu_id}/postProcessing/newCloud')
    paths_Ufile =os.listdir(f'{cpu_id}/postProcessing/newCloud')

    f_pCoe = paths_pCoe[0]
    f_ptfile = paths_ptfile[0]
    f_Ufile = paths_Ufile[0]


    pCoe = f'{cpu_id}/postProcessing/boundaryCloud/'+ f_pCoe + '/cloud_p.xy'
    ptfile = f'{cpu_id}/postProcessing/newCloud/'+ f_ptfile + '/cloud_p.xy'
    Ufile = f'{cpu_id}/postProcessing/newCloud/' + f_Ufile + '/cloud_U.xy'
    LnD = f'{cpu_id}/postProcessing/forceCoeffs_airfoil/0/forceCoeffs.dat'
    input_point = f'{cpu_id}/newData/newpoint'
    shear = f'{cpu_id}/all_temp/final/shearfinal'

    print(os.path.isfile(ptfile))

    pCoe = np.loadtxt(pCoe)
    ptfile = np.loadtxt(ptfile)
    Ufile = np.loadtxt(Ufile)
    LnD = np.loadtxt(LnD)
    inPoint = np.loadtxt(input_point)
    shear_load = np.loadtxt(shear)

    pCoel = len(pCoe)

    mapOutput1 = np.zeros((6, res, res))
    mapInput2 = np.zeros((1, 103, 1))
    mapOutput2 = np.zeros((2, 101, 1))
    mapOutput3 = np.zeros((1, 2, 1))

    curIndex1 = 0
    curIndex2 = 0
    curIndex3 = 0
    curIndex4 = 0

    for x in range(res):
        for y in range(res):
            xf = (((x/(res-1))-0.5)*2)+0.5
            yf = (((y/(res-1))-0.5)*2)
            if abs(ptfile[curIndex1][0] - xf)<1e-5 and abs(ptfile[curIndex1][1] - yf)<1e-5:
               mapOutput1[0][x][y] = freestreamX
               mapOutput1[1][x][y] = freestreamY
               mapOutput1[2][x][y] = 0
               mapOutput1[3][x][y] = ptfile[curIndex1][3]
               mapOutput1[4][x][y] = Ufile[curIndex1][3]
               mapOutput1[5][x][y] = Ufile[curIndex1][4]
               curIndex1 += 1 
            else:
                mapOutput1[2][x][y] = 1.0

    for x2 in range(len(inPoint)):
        mapInput2[0][x2] = inPoint[curIndex2][1]
        mapInput2[0][-2] = freestreamX
        mapInput2[0][-1] = freestreamY
        curIndex2 += 1



    for x3 in range(pCoel):
        mapOutput2[0][x3] = pCoe[curIndex3][3]
        mapOutput2[1][x3] = shear_load[curIndex3][1]
        curIndex3 += 1

    

    
    mapOutput3[0][0] = LnD[-1][2]
    mapOutput3[0][1] = LnD[-1][3]



    fileName = dataDir + '%s_%d_%d' %(basename, int(freestreamX*100), int(freestreamY*100))
    print("\tsaving in " + fileName + ".npz")
    np.savez_compressed(fileName, mapOutput1, input = mapInput2, CpACf = mapOutput2, LnD = mapOutput3)


    ############################

    # np.savez_compressed(fileName, map1 = mapOutput1, map2 = mapOutput2, map3 = mapOutput3 )

    ############################

def full_process(airfoil, freestreamX, freestreamY,  pressure) -> int:
    id = os.getpid()
    if not os.path.exists(f'{id}'):
        # Name the basic file originally named openFoam as the id of the selected input data
        os.system(f'cp -r openFoam {id}')    
        
        # Write the airfoil shape data in a folder named data0
        os.system(f'cp -r ./airfoil_database/{airfoil} {id}/data0 ')

    basename = os.path.splitext( os.path.basename(airfoil))

    # Concept similar to syntax cd id
    os.chdir(f'{id}')

    # look at 'def newPoint' If there is an error in this step, print, tell me, and 'cd ..' back to external environment
    if newPoint() !=0:
        print('\tnewPoint failed')
        os.chdir('..')
        return(-1)
    
    # look at 'def genMesh' If there is an error in this step, print, tell me, and 'cd ..' back to external environment
    if genMesh("../" + airfoil_database + airfoil) !=0:
        print('\tmesh generation failed, aborting')
        os.chdir("..")
        return(-1)
    
    # look at 'def runSim'
    status = runSim(freestreamX, freestreamY,  pressure)
    os.chdir("..")

    # look at 'def find' if there is an error in this step, print, tell me, and 'cd ..' back to external environment
    if find(id) != 0:
        print('\tcan not find the final folder')
        os.chdir('..')
        return(-1)
    
    os.chdir(f'{id}')

    # look at 'def wallShear' if there is an error in this step, print, tell me, and 'cd ..' back to external environment
    if wallShear() != 0:
        print('\tcan not find wallShearStress')

    # look at 'def tidy' if there is an error in this step, print, tell me
    if tidy() != 0:
        print('\tcan not tidy the data of internalCloud and boundaryCloud')

    # look at 'def Cf' if there is an error in this step, print, tell me
    if Cf() != 0:
        print('\tcan not turn the wallShearStress to Cf')
        
    # look at 'def Cf' if there is an error in this step, print, tell me
    if shearInterpolation() != 0:
        print('\tcan not interpolation the wallshearstress')

    os.chdir('..')

    print(status)
    if status == 0:
        outputProcessing(basename, freestreamX, freestreamY, id, dataDir=output_dir, res=256)
        print(f'\tCase {freestreamX: .2f}, {freestreamY: .2f} done')

    return id

# id is simply the ID of this set of databases
ids = []
def log_id(id):
    if id == -1 : return
    if id not in ids:
        ids.append(id)

def main():
    pool = mp.Pool(cpu_to_use)
    pool = mp.Pool(samples)
    startTime = time.time()
    for n in range(samples):
        # Use random in python to randomly select the shape of the wing, 'files' mean total data in floder named 'airfoil_database' 
        fileNumber = np.random.randint(0, len(files))

        # Create a name called airfoil, which is defined as the file name of the selected airfoil
        airfoil = files[fileNumber]
        print("\tusing {}" .format((files[fileNumber])))

        # define freestream pressure, temperature, and use the Mach number to calculate freestream velocity
        pressure = 1e5
        temperature = 300
        a = math.sqrt(1.4*287*temperature)

        M = np.random.uniform(Mach_number_factor_low, Mach_number_factor_high)

        angle = np.random.uniform(-freestream_angle, freestream_angle)

        freestreamX = math.cos(angle) * M * a
        freestreamY = -math.sin(angle) * M * a
        print(f'\tUsing Mach number {M:.2f} angle {angle*180/math.pi:.2f}')
        print(f'\tResulting freestream vel x,y: {freestreamX:.2f}, {freestreamY:.2f}')

        # look at line of 'def full_process'
        pool.apply_async(full_process, args=(airfoil, freestreamX, freestreamY, pressure,), callback=log_id)
        with open('setLog', 'a') as of:
            of.write(f'{n:d}\t|{airfoil.split(".")[0]}\t|{M:.2f}\t|{angle*180/math.pi:.2f}\n')

    pool.close()
    pool.join()
    totalTime = (time.time() - startTime)/60
    print(f'Final time elapsed: {totalTime:.2f} minutes')
    print(ids)

if __name__ == '__main__':
    main()

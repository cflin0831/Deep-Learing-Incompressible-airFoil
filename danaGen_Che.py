

import os, math, uuid, sys, random, time
import numpy as np
import utils
import multiprocessing as mp

samples     = 5             # no. of datasets to product
freestream_angle = 0        # angle
Mach_number_factor_low = 0.22
Mach_number_factor_high = 0.25   # mach number factor
cpu_to_use = 20 

airfoil_database = "./0015database/"    # the database we used (we choose only one this time)
output_dir = "./0015/"                  # output name of database

utils.makeDirs([output_dir])

files = os.listdir("./0015database/")
airfoilFile = './0015database/'+ files[0]
# file1 = f'{files[0].split(".dat")[0]}.geo'
files.sort()
if len(files)==0:
    print("error - no airfoils found in %s" % airfoil_database)
    exit(1)

seed = random.randint(0, 2**32 - 1)
np.random.seed(seed)
print("Seed: {}".format(seed))

def genMesh(airfoilFile):
    ar = np.loadtxt(airfoilFile)
    if np.max(np.abs(ar[0]-ar[(ar.shape[0]-1)]))==0.02:
        ar = ar[:-1]
    output = ""
    pointIndex = 1000
    for n in range(ar.shape[0]):
        output += "Point({}) = {{ {}, {}, 0.000000, 0.005}};\n". format(pointIndex, ar[n][0], ar[n][1])
        pointIndex += 1

    with open("airfoil_template.geo", "rt") as inFile:
        with open("airfoil.geo", "wt") as outFile:
            for line in inFile:
                line = line.replace("POINTS", "{}".format(output))
                line = line.replace("LAST_POINT_INDEX", "{}".format(pointIndex-1))
                outFile.write(line)
            
    # os.chdir('openFoam')
    if os.system( "gmsh airfoil.geo -3 -format msh2 airfoil.msh > /dev/null" ) != 0:   # if it error during mesh creation, /dev/null(導向垃圾桶) it==0(correct)
        print("error during mesh creation!")
        return(-1)

    if os.system("gmshToFoam airfoil.msh > /dev/null")!=0:
        print("error during coversion to OpenFoam mesh")
        return(-1)

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
    # genMesh(airfoilFile)
    return(0)
# genMesh(airfoilFile)

def runSim(freestreamX, freestreamY, pressure=1e5):
    list = [f'Vx     {freestreamX: .2f};', f'Vy           {freestreamY:.2f};',  f'Pressure     {pressure};' ]
    with open("0/ICnBC", "wt") as oF:
        oF.write('//Initial and boundary conditions for flow field\n')
        for i in range(len(list)):
            oF.write(list[i]+'\n')
        oF.write('#inputMode merge\n')
    # os.chdir('openFoam')
    status = os.system("./Allclean && simpleFoam > foam.log")
    return status  

def outputProcessing(basename, freestreamX, freestreamY, cpu_id, dataDir=output_dir, res=128):
    paths_pCoe=os.listdir(f'{cpu_id}/postProcessing/boundaryCloud')
    paths_ptfile =os.listdir(f'{cpu_id}/postProcessing/internalCloud')
    paths_Ufile =os.listdir(f'{cpu_id}/postProcessing/internalCloud')

    f_pCoe = paths_pCoe[-1]
    f_ptfile = paths_ptfile[-1]
    f_Ufile = paths_Ufile[-1]

    # print(os.getcwd())

    pCoe = f'{cpu_id}/postProcessing/boundaryCloud/'+ f_pCoe + '/cloud_p.xy'
    ptfile = f'{cpu_id}/postProcessing/internalCloud/'+ f_ptfile + '/cloud_p.xy'
    Ufile = f'{cpu_id}/postProcessing/internalCloud/' + f_Ufile + '/cloud_U.xy'
    LnD = f'{cpu_id}/postProcessing/forceCoeffs_airfoil/0/forceCoeffs.dat'
    
    print(os.path.isfile(ptfile))

    pCoe = np.loadtxt(pCoe)
    temp = np.loadtxt(ptfile)
    ptfile = np.loadtxt(ptfile)
    Ufile = np.loadtxt(Ufile)
    LnD = np.loadtxt(LnD)

    # print(temp)

    LnDl = len(LnD)
    pCoel = len(pCoe)

    mapOutput1 = np.zeros((6, res, res))
    mapOutput2 = np.zeros((4, LnDl, 1 ))
    mapOutput3 = np.zeros((3, pCoel, 1))

    curIndex1 = 0
    curIndex2 = 0
    curIndex3 = 0

    for y in range(res):
        for x in range(res):
            xf = (((x/res)-0.5)*2)+0.5
            yf = (((y/res)-0.5)*2)
            if abs(ptfile[curIndex1][0] - xf)<1e-4 and abs(ptfile[curIndex1][1] - yf)<1e-4:
               mapOutput1[0][x][y] = freestreamX
               mapOutput1[1][x][y] = freestreamY
               mapOutput1[2][x][y] < 1.0
               mapOutput1[3][x][y] = ptfile[curIndex1][3]
               mapOutput1[4][x][y] = Ufile[curIndex1][3]
               mapOutput1[5][x][y] = Ufile[curIndex1][4]
               curIndex1 += 1 
            else:
                mapOutput1[2][x][y] > 1.0

    for x2 in range(LnDl):
        mapOutput2[0][x2] = freestreamX
        mapOutput2[1][x2] = freestreamY
        mapOutput2[2][x2] = LnD[curIndex2][2]
        mapOutput2[3][x2] = LnD[curIndex2][3]
        curIndex2 += 1

    for x3 in range(pCoel):
        mapOutput3[0][x3] = freestreamX
        mapOutput3[1][x3] = freestreamY
        mapOutput3[2][x3] = pCoe[curIndex3][3]
        curIndex3 += 1

    fileName = dataDir + '%s_%d_%d' %(basename, int(freestreamX*100), int(freestreamY*100))
    print("\tsaving in " + fileName + ".npz")
    np.savez_compressed(fileName, mapOutput1, mapOutput2, mapOutput3 )

    ############################

    # np.savez_compressed(fileName, map1 = mapOutput1, map2 = mapOutput2, map3 = mapOutput3 )

    ############################

def full_process(airfoil, freestreamX, freestreamY,  pressure) -> int:
    id = os.getpid()
    if not os.path.exists(f'{id}'):
        os.system(f'cp -r openFoam {id}')

    basename = os.path.splitext( os.path.basename(airfoil))

    os.chdir(f'{id}')
    
    if genMesh("../" + airfoil_database + airfoil) !=0:
        print('\tmesh generation failed, aborting')
        os.chdir("..")
        return(-1)

    status = runSim(freestreamX, freestreamY,  pressure)
    os.chdir("..")
    if status == 0:
        outputProcessing(basename, freestreamX, freestreamY, id, dataDir=output_dir, res=128)
        print(f'\tCase {freestreamX,: .2f}, {freestreamY,: .2f} done')

    return id

ids = []
def log_id(id):
    if id == -1 : return
    if id not in ids:
        ids.append(id)

def main():
    pool = mp.Pool(cpu_to_use)
    startTime = time.time()
    for n in range(samples):

        fileNumber = np.random.randint(0, len(files))
        airfoil = files[fileNumber]
        print("\tusing {}" .format((files[fileNumber])))

        pressure = 1e5
        temperature = 300
        a = math.sqrt(1.4*287*temperature)

        M = np.random.uniform(Mach_number_factor_low, Mach_number_factor_high)

        angle = np.random.uniform(-freestream_angle, freestream_angle)
        freestreamX = math.cos(angle) * M * a
        freestreamY = -math.sin(angle) * M * a
        print(f'\tUsing Mach number {M:.2f} angle {angle*180/math.pi:.2f}')
        print(f'\tResulting freestream vel x,y: {freestreamX:.2f}, {freestreamY:.2f}')

        pool.apply_async(full_process, args=(airfoil, freestreamX, freestreamY, pressure,), callback=log_id)
        with open('setLog', 'a') as of:
            of.write(f'{n:d}\t|{airfoil.split(".")[0]}\t|{M:.2f}\t|{angle*180/math.pi:.2f}\n')


    pool.close()
    pool.join()
    totalTime = (time.time() - startTime)/60
    print(f'Final time elapsed: {totalTime:.2f} minutes')
    print(ids)
    for id in ids:
        os.system(f'rm -r {id}/')
    #



if __name__ == '__main__':
    main()

# ********************************************************************************
# Extract results from the discrete adjoint run to be used in the GEK algorithm
# Written by: Amir K. Bagheri
# Feb 2020
# ********************************************************************************
# Extract the value of the velocity objective function, along with the 
# gradients wrt each design parameter.

import os
import math
import glob

# File names need to be specified. Standard SU2 output
output_file = 'output.dat'
flow_file = 'flow.dat'
hist_file = 'history_adjoint.dat'

# Create list of folders where results for each sample are located
parent_dir = os.getcwd()
folder_list = [f for f in os.listdir(parent_dir) if os.path.isdir(f)]
folder_list.sort()

# Find X and Y coordinates of velocity objective function as printed out in the output file
# these coordinates differ from the sample coordinates given to SU2 since SU2 finds the
# nearest mesh node instead and evaluates the objective function there.
xy_list = []
for folder in folder_list:
    with open(folder + '/' + output_file) as file:
        for line in file:
            if line.startswith('X:'):
                x = float(line.split(':')[1].split()[0])
            elif line.startswith('Y:'):
                y = float(line.split(':')[1].split()[0])
        xy_list.append([x, y])
         
# Extract velocity from flow solution file. flow file is tab separated
vel_list = []  
for index, folder in enumerate(folder_list):
    # search for x and y in flow file. first, change format to scientific to match flow file.
    x = format(xy_list[index][0],'.6e')
    y = format(xy_list[index][1],'.6e')
    
    with open(folder + '/' + flow_file) as file:
        for line in file:
            if x in line and y in line:
                flow_variables = line.split('\t')
                density = float(flow_variables[2])
                vel_x = float(flow_variables[3]) / density
                vel_y = float(flow_variables[4]) / density
        vel_list.append([vel_x, vel_y])

# Find objective function value from velocities
objfunc_list = []
for vel in vel_list:
    obj = math.atan2(vel[1], vel[0]) * math.sqrt(math.pow(vel[0],2) + math.pow(vel[1],2))
    objfunc_list.append(obj)
            
# Extract gradients from the convergence history file, read last line. history file is comma seperated
grad_list = []            
for folder in folder_list:
    with open(folder + '/' + hist_file) as file:
        for line in file:
            pass # keep going until at the last line
        history = line.split(', ') 
        sens_cb1 = float(history[13])
        sens_sig = float(history[14])
        sens_cb2 = float(history[15])
        sens_kar = float(history[16])
        sens_cw2 = float(history[17])
        sens_cw3 = float(history[18])
        sens_cv1 = float(history[19])
        sens_x   = float(history[22])
        sens_y   = float(history[23])
        grad_list.append([sens_cb1, sens_sig, sens_cb2, sens_kar, \
                          sens_cw2, sens_cw3, sens_cv1, sens_x, sens_y])

# Write all results to file
# Find results file name based on sample file name
sam_filename = glob.glob('samples*')[0]
caseno       = sam_filename.split('samples')[1]
res_filename = 'results' + caseno
res_file = open(res_filename,'w+')
header = ('VARIABLES = "X", "Y", "obj_func", "sens_cb1", sens_sig", "sens_cb2",'
          '"sens_kar", "sens_cw2", sens_cw3", "sens_cv1", "sens_x", "sens_y"')
res_file.write(header + '\n')

# write results, some are not strings so convert
col = 18 # justify column size
form = '.6E' # Format to be printed

for i in range(len(folder_list)):    
    strng = format(xy_list[i][0], form).ljust(col) + format(xy_list[i][1], form).ljust(col) + format(objfunc_list[i], form).ljust(col) + \
            format(grad_list[i][0], form).ljust(col) + format(grad_list[i][1], form).ljust(col) + format(grad_list[i][2], form).ljust(col) + \
            format(grad_list[i][3], form).ljust(col) + format(grad_list[i][4], form).ljust(col) + format(grad_list[i][5], form).ljust(col) + \
            format(grad_list[i][6], form).ljust(col) + format(grad_list[i][7], form).ljust(col) + format(grad_list[i][8], form).ljust(col)
            
    res_file.write(strng + '\n')             
            
            
            
            
            
            
            
            

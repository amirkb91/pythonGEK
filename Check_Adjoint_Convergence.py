# ********************************************************************************
# Check the convergence of the steady + adjoint simulations
# Written by: Amir K. Bagheri
# March 2020
# ********************************************************************************

import os


# File names need to be specified. Standard SU2 output
output_file   = 'output.dat'

# File name to be written. Write header
confilename = 'convcheck.dat'
con_file = open(confilename,'w+')
header = 'Simulation'.ljust(16) + 'Direct Conv'.ljust(16) + 'Direct Iter'.ljust(16) + \
         'Adjoint Conv'.ljust(16) + 'Adjoint Iter'
con_file.write(header + '\n')

# Create list of folders where results for each sample are located
parent_dir = os.getcwd()
folder_list = [f for f in os.listdir(parent_dir) if os.path.isdir(f)]
folder_list.sort()


# Read the output file and look for string containing converged message
for folder in folder_list:
    # reset logicals
    dir_converged = False
    adj_converged = False
    dir_iter = '----'
    adj_iter = '----'

    try:
	    with open(folder + '/' + output_file) as file:
	        # Read file and store as list
	        output = file.readlines()
	        # Check for converged string
	        for i, line in enumerate(output):
	            if 'satisfied' in line:
	                # 3 lines up is the last iteration
	                # for a fully converged solution, 'satisfied' will be found twice
	                lastiter = output[i-3]
	                
	                # set logicals
	                if dir_converged == True: # encountered second instanse of 'satisfied'
	                    adj_converged = True
	                else:
	                    dir_converged = True  # encountered first instance of 'satisfied'
	                
	                # extract info from lastiter
	                if dir_converged == True and adj_converged == False:
	                    dir_iter = lastiter.split()[0]
	                elif dir_converged == True and adj_converged == True:
	                    adj_iter = lastiter.split()[0]
    except FileNotFoundError: # haven't run yet on iridis
        pass
                
    # write to file
    strng = folder.ljust(20) + str(dir_converged).ljust(16) + \
            dir_iter.ljust(16) + str(adj_converged).ljust(16) + adj_iter
    con_file.write(strng + '\n')
        
# Check nearest node printed in the output files
con_file.write('\n'*3)
grepcommand = 'grep -r "Nearest Mesh Node to" -A 6 -B 2 . --exclude={"*.py","' + confilename + '"} >> ' + confilename
os.system(grepcommand)        
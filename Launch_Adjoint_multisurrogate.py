# ********************************************************************************
# Create directories for all CFD simulations for the GEK database and run the jobs
# Written by: Amir K. Bagheri
# May 2020
# ********************************************************************************

# ------------- Version for Multiple Surrogate Models ------------------- 

# Files Needed:
# 1. GEK samples file.dat
# 2. config file.cfg
# 3. runscript.sh
# 4. discrete_adjoint.py
# 5. mesh file.su2


# open and read sample file
# for each sample create a directory and also write cfg and sh files
# run the job for each sample

import os
import shutil
from pathlib import Path

def main():

    parent_dir = os.getcwd()

    # Specify iteration number and surrogate number for folder names. Type = STRING
    srgtno = 'M10'
    iterno = 'I03'        

    # Specify file names
    sample_file = srgtno + '/' + iterno + '/' + 'samples_' + srgtno + '_' + iterno + '.dat'
    # sample_file = 'veribound/veribound/samples_verifybound.dat'
    config_file = 'turb_adjoint_MG_Implicit.cfg'
    submit_file = 'run_script_python.sh'
    python_file = 'discrete_adjoint.py'    
    
    with open(sample_file) as samfile:
        # Extract header
        header = next(samfile).split(",")
        header = [x.strip() for x in header]
        
        # For each line in sample file:
        for sampleno, line in enumerate(samfile, start = 1):
          # check if line isn't commented out and split into floats
          if not line.startswith('#'):
              samples = line.split(",")
              samples = [float(i) for i in samples]
          
              # Create directory for each sample point
              dirname = make_dir(sampleno, iterno, srgtno)
              
              # Create config file in directory
              set_config(config_file, dirname, parent_dir, samples)
              
              # Create run script in directory
              set_submit(submit_file, dirname, parent_dir, sampleno, iterno, srgtno)
              
              # Copy python file to directory
              shutil.copy2(python_file, dirname)
              
              # Submit job
              submit_all(submit_file, dirname, parent_dir)
              
              
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def make_dir(sampleno, iterno, srgtno):
    
    dirname = srgtno + '/' + iterno + '/' + 'Sim_' + str(sampleno).zfill(4)
    
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    Path(dirname).mkdir(parents=True, exist_ok=True)
    
    return dirname

def set_config(config_file, dirname, parent_dir, samples):    
    
    # cd into new directory and create file for writing
    os.chdir(dirname)
    konfig_file = open(config_file, 'w+') # same name as master config file but new file
    
    # read master config file and write to konfig_file line by line, changing the ones 
    # which need updating with sample values
    with open('../../../' + config_file) as konfig:
        for line in konfig:
            if not line.startswith('%'):
                # Change SA coefficients and XY
                if "SA_CB1" in line:
                    konfig_file.write("SA_CB1 = " + str(samples[0]) + '\n')
                elif "SA_SIG" in line:
                    konfig_file.write("SA_SIG = " + str(samples[1]) + '\n')
                elif "SA_CB2" in line:
                    konfig_file.write("SA_CB2 = " + str(samples[2]) + '\n')
                elif "SA_KAR" in line:
                    konfig_file.write("SA_KAR = " + str(samples[3]) + '\n')
                elif "SA_CW2" in line:
                    konfig_file.write("SA_CW2 = " + str(samples[4]) + '\n')
                elif "SA_CW3" in line:
                    konfig_file.write("SA_CW3 = " + str(samples[5]) + '\n')
                elif "SA_CV1" in line:
                    konfig_file.write("SA_CV1 = " + str(samples[6]) + '\n')
                elif "X_VEL_OBJ" in line:
                    konfig_file.write("X_VEL_OBJ = " + str(samples[7]) + '\n')
                elif "Y_VEL_OBJ" in line:
                    konfig_file.write("Y_VEL_OBJ = " + str(samples[8]) + '\n')
                # change mesh file name and add ../
                elif "MESH_FILENAME" in line:
                    mesh = line.split('=')[1].split()[0]
                    konfig_file.write("MESH_FILENAME=" + " ../../../" + mesh + '\n')                     
                else:
                    konfig_file.write(line)
            
    os.chdir(parent_dir) 
    
    return

def set_submit(submit_file, dirname, parent_dir, sampleno, iterno, srgtno):
    
    # cd into new directory and create file for writing
    os.chdir(dirname)
    cubmit_file = open(submit_file, 'w+') # same name as master submit file but new file
    
    # create string for job name
    job = srgtno + iterno + str(sampleno).zfill(2)

    # read master submit file and write to cubmit_file line by line, changing the ones 
    # which need updating with job and directory name    
    with open('../../../' + submit_file) as cubmit:
        for line in cubmit:
            if "--job-name" in line:
                cubmit_file.write("#SBATCH --job-name=" + job + '\n')
            elif "export MYDIR" in line:
                cubmit_file.write("export MYDIR=" + parent_dir + "/" + dirname + '\n')                                  
            else:
                cubmit_file.write(line)
            
    os.chdir(parent_dir)
    
    return

def submit_all(submit_file, dirname, parent_dir):
    
    # cd into new directory and submit the job
    os.chdir(dirname)
    cmd = "sbatch " + submit_file
    os.system(cmd)
    os.chdir(parent_dir)
    return

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~              

# run main          
if __name__ == "__main__":
    main()
       
          
      

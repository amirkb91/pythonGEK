#!/usr/bin/env python 

## \file discrete_adjoint.py
#  \brief Python script for doing the discrete adjoint computation using the SU2 suite.
#  \author Amir K. Bagheri
#  \version 6.2.0 "Falcon"

import os, sys
from optparse import OptionParser
sys.path.append(os.environ['SU2_RUN'])
import SU2

# -------------------------------------------------------------------
#  Main 
# -------------------------------------------------------------------

def main():
    
    # Command Line Options
    parser=OptionParser()
    parser.add_option("-f", "--file",       dest="filename",
                      help="read config from FILE", metavar="FILE")
    parser.add_option("-n", "--partitions", dest="partitions", default=1,
                      help="number of PARTITIONS", metavar="PARTITIONS")
    
    (options, args)=parser.parse_args()
    options.partitions  = int( options.partitions )
    

    # Run direct to get steady solution
    direct_steady(options.filename, options.partitions)

    # Run discrete adjoint to get gradients
    discrete_adjoint(options.filename, options.partitions)
        
#: def main()

# -------------------------------------------------------------------
#  Steady
# -------------------------------------------------------------------

def direct_steady(filename, partitions = 1):
    
    # Config
    config = SU2.io.Config(filename)
    config.NUMBER_PART = partitions
    config.NZONES      = 1

    # State
    state = SU2.io.State()
    
    # read mesh file
    state.FILES.MESH = config.MESH_FILENAME
    
    # Direct Solution
    info = SU2.run.direct(config) 
    state.update(info)
    SU2.io.restart2solution(config,state)
       
    return

# -------------------------------------------------------------------
#  Discrete Adjoint
# -------------------------------------------------------------------

def discrete_adjoint(filename, partitions = 1):

    # Config
    config = SU2.io.Config(filename)
    config.NUMBER_PART = partitions
    config.NZONES      = 1

    # State
    state = SU2.io.State()

    # read mesh file
    state.FILES.MESH = config.MESH_FILENAME

    # Set the discrete adjoint run (this is needed)
    config['GRADIENT_METHOD'] = 'DISCRETE_ADJOINT'
    
    # Change config file entries if needed

    # config['MGLEVEL']  = 0
    config['CONV_CRITERIA'] = "RESIDUAL"
    config['WRT_SOL_FREQ'] = 50
    config['STARTCONV_ITER'] = 500
    config['EXT_ITER'] = 10000
    config['CFL_ADAPT'] = 'NO'
    config['CFL_NUMBER'] = 80
        
    # Adjoint Solution
    info = SU2.run.adjoint(config)
    state.update(info)
    SU2.io.restart2solution(config,state)    
   
    return 

# -------------------------------------------------------------------
#  Run Main Program
# -------------------------------------------------------------------

# this is only accessed if running from command prompt
if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
This is the main script for the Corsika simulations.
It uses the 3 classes imported from utils

FileWriter class can be used to create and write a Corsika inp file 
    and create "data", "temp", "log", "inp" folders.
    
SimulationMaker class can be used for generating the submission stings and sh executable files. 
    It also has the generator function which yields the keys and string to submit, 
    made via the combinations of file and energies 

Submitter class can be used to spawns subprocesses for multiple instances instead of multiple job submissions.

The args values can be used to specify the desired configuration for the simulation.

How to run:
    python3 MakeCorsikaSim.py 
 if you want to change any configuration from the default once add the [args] after it
 e.g.:
    python3 MakeCorsikaSim.py --user myusername --primary 1 ..... 

@author: Federico Bontempo <federico.bontempo@kit.edu> PhD student KIT Germany
@date: October 2022
"""
import sys
import os 
import numpy as np
import random
import subprocess

from utils.FileWriter import FileWriter
from utils.SimulationMaker import SimulationMaker
from utils.Submitter import Submitter

def __checkInputs(args):
    """
    This function should check some basic things before the starting the simulation.
        energyEnd > energyStart
        energyEnd <= 10_000 otherwise the numbering is not unique anymore 
        primary is in the keys of the pimIdDict
        check if the corsika given is correct 
        maybe a warning if seed value is over 900_000_000
        
    seedValue = int((runNumber + self.primIdDict[self.primary]*1_000_000) % 900_000_001) 
    """
    if not args.energyEnd > args.energyStart:
        sys.exit('The energy End value MUST be greater (nor equal) then the starting one!!')
    
    if not args.energyEnd <= 10_000:
        sys.exit('The energy End value MUST be less then 10.000!! The seed number is not unique otherwise!')
    
    if args.primary not in args.primIdDict.keys():
        sys.exit('The primary chosen is not in the primIdDict in the mainCorsikaSim. \nBe sure that the --primary is correct.\
            \nIf so, update the args.primIdDict in the mainCorsikaSim.')
    
    if not os.path.isfile(f"{args.pathCorsika}/{args.corsikaExe}"): 
        sys.exit('The corsikaExe does not exist or the pathCorsika is wrong.\
            \nCheck them, please!')
    
    if args.primIdDict[args.primary]*1_000_000 > 900_000_001:
        import warnings
        warnings.warn("The program is not stopped, \
            but aware that the Corsika seed number is exceeding 900.000.000 (the max allowed value)")
        
    # verify that the filepaths are setup correctly, if not raise an error
    if not os.path.exists(args.dirSimulations):
        raise NotADirectoryError(f"Directory {args.dirSimulations} does not exist, please create it!")
    
    if not os.path.exists(args.pathCorsika):
        raise NotADirectoryError(f"Directory {args.pathCorsika} does not exist, unpack corsika package to this path!")
    
    if not os.path.exists(os.path.join(args.pathCorsika, args.corsikaExe)):
        raise FileNotFoundError(f"Corsika executable {args.corsikaExe} not found, check if you compiled the executable correctly.")
    
    if not os.path.exists(args.pathAntennas):
        raise FileNotFoundError(f"Antenna file {args.pathAntennas} does not exist, create antenna list with this name or check the data directory.")
    return


def mainCorsikaSim(args):
    """
    Some Documentation of the main function for the Corsika Simulator
    
    Defines the indexing of the primaries. This can be updated if needed in the future. 
    Checks if the inputs given are consistent with the script 
    Defines the energy range
    Calls a bunch of classes 
    Finally: 
    start spawning and checking multiple simulations.
    """
    # This is a dictionary, with keys the Corsika numbering of primary, 
    # and values the arbitrary numbering used in this script for all primary particle. 
    # In principle this can be expanded with all primaries that one wants     
    args.primIdDict = {
        1:    0,      # Gammas (photons)
        14:   1,      # Protons (H)
        402:  2,      # Helium (He)
        1608: 3,      # Oxygen (O)
        5626: 4,      # Iron (Fe)
        2814: 5,      # Silicon (Si)
                }

    # Checks if the input given are consistent with the structure of the script
    __checkInputs(args)
    
    # Defines the energy range given the start, end and step 
    energies = np.around( # Need to round the numpy array otherwise the floating is wrong
                    np.arange(
                        args.energyStart, # energy starting point
                        args.energyEnd + args.energyStep, # energy end point plus one step in order to include last step
                        args.energyStep, # step in energies
                        ),
                decimals=1 # the rounding has to have one single decimal point for the folder. 
    )
    
    fW = FileWriter(
        username=args.username,                 # User name on server
        dirRun=args.pathCorsika,
        dirSimulations=args.dirSimulations,
        primary=args.primary,                   # 1 is gamma, 14 is proton, 402 is He, 1608 is Oxygen, 5626 is Fe
        primIdDict = args.primIdDict,

        zenithStart = args.zenithStart,
        zenithEnd = args.zenithEnd,
        
        # zenith =args.zenith,
        obslev =args.obslev,

        pathAntennas=args.pathAntennas,
        pathCorsika = args.pathCorsika,
        corsikaExe = args.corsikaExe,
    )

    simMaker = SimulationMaker(
        startNumber=args.startNumber, 
        endNumber=args.endNumber, 
        energies=energies, 
        fW=fW, # The fileWriter class 
        pathCorsika = args.pathCorsika,
        corsikaExe = args.corsikaExe,

        # zenith = args.zenith,
        zenithStart = args.zenithStart,
        zenithEnd = args.zenithEnd,

        primary_particle = args.primary,
        directory = args.dirSimulations,
        antenna_type=args.antenna_type,
    )

    submitter = Submitter(
        MakeKeySubString=simMaker.generator,
        parallel_sim=args.parallelSim,
        logDir=os.path.join(args.dirSimulations, "logs"),
    )

    # Starts the spawn of the simulations
    submitter.startProcesses()
    # Loops over the running processes and checks if any process is complete.
    # If so, it will spawn the next one
    submitter.checkRunningProcesses()
    


if __name__ == "__main__":

    import argparse

    dir_name = os.path.dirname(os.path.realpath(__name__))

    parser = argparse.ArgumentParser(
        description="Inputs for the Corsika Simulation Maker"
    )

    parser.add_argument(
        "--username", 
        type=str, 
        default="bg5912", 
        help="your user name on server"
    )
    parser.add_argument(
        "--primary",
        type=int,
        default=14,
        help="primary type: 1 is gamma, 14 is proton, 402 is He, 1608 is Oxygen, 5626 is Fe",
    )

    parser.add_argument(
        "--dirSimulations",
        type=str,
        default=os.path.join(dir_name, "..", "outputs"),
        help="Directory where the simulation are stored",
    )
    parser.add_argument(
        "--pathCorsika",
        type=str,
        default=os.path.join(dir_name, "..", "corsika-77550", "run"),
        help="the /run directory where the executable of corsika is located",
    )
    parser.add_argument(
        "--corsikaExe",
        type=str,
        default="mpi_corsika77550Linux_SIBYLL_urqmd_thin_coreas_parallel_runner",
        help="the name of the executable of corsika located in the /run directory",
    )
    parser.add_argument(
        "--startNumber",
        type=int,
        default=0,
        help="start number of simulation (e.g. 0 default)",
    )
    parser.add_argument(
        "--endNumber",
        type=int,
        default=1000,
        help="if you startNumber is 0 then it is equal to the total number of simulation per bin (e.g. 667 default)",
    )

    parser.add_argument(
        "--energyStart", 
        type=float, 
        default=5.0, 
        help="Lower limit of energy"
    )
    parser.add_argument(
        "--energyEnd", 
        type=float, 
        default=7.0, 
        help="Upper limit of energy"
    )
    parser.add_argument(
        "--energyStep", 
        type=float, 
        default=0.1, 
        help="Step in energy, 0.1 default (do not change unless you know what you are doing)"
    )

    parser.add_argument(
        "--zenithStart", 
        type=float, 
        default=55.00000000, 
        help="Start value of zenith range (do not change unless you know what you are doing)"
    )

    parser.add_argument(
        "--zenithEnd", 
        type=float, 
        default=87.00000000, 
        help="End value of zenith range (do not change unless you know what you are doing)"
    )

    parser.add_argument(
        "--obslev", 
        type=float, 
        default=0, 
        help="observation level in cm"
    )

    parser.add_argument(
        "--pathAntennas",
        type=str,
        default=os.path.join(dir_name, "data", "gp300.list"),
        help="the directory where the antenna position file is located"
    )

    parser.add_argument(
        "--parallelSim",
        type=int,
        default=1,
        help="Number of parallel simulation processes - DO NOT USE WITH MPI",
    )

    parser.add_argument(
        "--antenna_type",
        type=str,
        default="random",
        help="Type of antenna layout to use. Default is random, randomly distributing the GP300 antennas.",
        choices=["random", "starshape"]
    )

    args = parser.parse_args()
    mainCorsikaSim(args)

    print("Final incantation complete: All cosmic portals explored, program's journey ends...")
    
    print("-------------------- Program finished --------------------")
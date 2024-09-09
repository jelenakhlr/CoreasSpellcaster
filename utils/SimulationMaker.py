#!/usr/bin/env python3
"""
This class can be used for generating the submission stings and sh executable files. 
It also has the generator function which yields the keys and string to submit, 
made via the combinations of file and energies 

@author: Federico Bontempo <federico.bontempo@kit.edu> PhD student KIT Germany
@date: October 2022

edited for radio by 
@author: Jelena
@date: June 2023

Submitting the sims with this program takes too long with Corsika :(
It's actually better to do one job per shower - for Coreas at least.
So FOR RADIO: use this whole thing to create the input and sh files 
and then run those separately using submit_jobs.py

"""
import numpy as np
import random
import os
import stat
from utils.runNumberGenerator import runNumberGenerator
import sys

class SimulationMaker:
    """
    This class has two useful functions. 
        generator: which yields a key and a string to submit 
        makeStringToSubmit: which writes a temporary file and a string to submit
    
    Parameters:
        startNumber:    the start of the simulation (eg. integer default value 0)
        endNumber:      the end of the simulation (eg. integer default value if startNumber is 0, 
                        it is the total number of simulations.
        energies:       the array binned in energies for the simulation
        fW:             the file writer class. In order to use some of the functions in this class
        pathCorsika:    the path where Corsika is installed
        corsikaExe:     the name of the Corsika executable that needs to be used
    
    """
    def __init__(self, 
                 startNumber, 
                 endNumber, 
                 energies, 
                 fW, 
                 pathCorsika, 
                 corsikaExe, 
                 zenithStart,
                 zenithEnd,
                 primary_particle,
                 directory,
                 antenna_type : str = "random",
    ):
        
        self.startNumber = startNumber
        self.endNumber = endNumber
        self.energies = energies
        self.fW = fW
        self.pathCorsika = pathCorsika
        self.corsikaExe = corsikaExe
        self.zenithStart = zenithStart
        self.zenithEnd = zenithEnd
        self.primary_particle = primary_particle
        self.runNumGen = runNumberGenerator()
        self.directory = directory
        self.antenna_type = antenna_type



    def generator(self):
        """
        This function generates configurations for simulations with various energies, zenith angles, and azimuth angles. 
        It iterates through all possible combinations and yields a unique key and a string 
        required for submitting each simulation job.

        The folder structure for the simulations is created as:
            primary_particle/energy/theta/runNumber/

        Each run will have its own folder within the specified energy and zenith angle subdirectories.
        """
        print("Conjuring energies in log10 GeV of", self.energies)

        # Zenith angle range
        zenith_range = np.around(np.arange(self.zenithStart, self.zenithEnd + 0.1, 2.5), decimals=1)
        # Number of additional values per step
        intervals = 10
        # Initialize empty list for all zenith values
        all_zenith_values = []
        print("zenith range", zenith_range[0], zenith_range[-1])
            
            # This is a loop over all energies and gives the low and high limit values.
            # Eg. 5.0 and 5.1
        for log10_E1, log10_E2 in zip(self.energies[:-1], self.energies[1:]):
                # Calculate cosine values for the current step
            for i, (zenith_start, zenith_end) in enumerate(zip(zenith_range[:-1], zenith_range[1:])):
                cstart = 1 -np.cos(np.deg2rad(zenith_start))
                cend = 1 - np.cos(np.deg2rad(zenith_end))
                cos_value = np.linspace(cstart, cend, intervals, endpoint=False)
                all_zenith_values = (list(np.rad2deg(np.arccos(1-cos_value))))
                if i==(len(zenith_range)-2):
                    all_zenith_values.append(zenith_end)

                for zenith in all_zenith_values:
                    print(zenith)
                    # loop over all the unique numbers 
                    for runIndex in range(self.startNumber, self.endNumber, 1):
                        #! zenith loop here
                        # Get the next azimuth value from the list
                        print("SimMaker using zenith", zenith)

                        #! random azimuth here
                        # Get random azimuth
                        azimuth = round(random.uniform(0, 360), 2)
                        print("SimMaker using azimuth", azimuth)

                        # print runIndex (as double check)
                        print("runIndex", runIndex)

                        # Create the file name (runNumber) for the simulation
                        particleID = self.runNumGen.getPrimaryID(self.primary_particle)
                        zenithID = self.runNumGen.getZenithID(zenith)
                        azimuthID = self.runNumGen.getAzimuthID(azimuth)
                        energyID = self.runNumGen.getEnergyID(log10_E1)
                        runNumber = format(int(particleID * 1E5 + zenithID * 1E4 + azimuthID * 1E3 + energyID * 1E2 + runIndex), '06d')
                        print("runNumber", runNumber)

                        # Create folders with the structure: primary_particle/energy/theta/runNumber/<files>
                        folder_path = os.path.join(f"{self.directory}{self.primary_particle}/{log10_E1}/{zenith_start}/{runNumber}/")
                        os.makedirs(folder_path, exist_ok=True)  # Create folders if they don't already exist

                        # Check if the simulation already exists
                        if f"SIM{runNumber}_coreas" not in os.listdir(folder_path):
                            # Write Corsika input file and generate key/string
                            self.fW.writeFile(runNumber, log10_E1, azimuth, zenith, folder_path,  self.antenna_type)
                            key = f"{log10_E1}_{runNumber}"
                            stringToSubmit = self.makeStringToSubmit(log10_E1, runNumber, zenith, folder_path)
                            yield (key, stringToSubmit)



    # TODO: make this nicer. Figuring out the substring stuff is too much work, so I'm just referring to the subfile created in SubFilesGenerator here.
    def makeStringToSubmit(self, log10_E1, runNumber, zenith, folder_path):
        
        # Makes a temp file for submitting the jobs.
        sub_file = (f"{folder_path}/SIM{runNumber}.sub")
        print(sub_file)
        # The stringToSubmit is basically the execution of the temporary sh file
        subString = sub_file
        return subString


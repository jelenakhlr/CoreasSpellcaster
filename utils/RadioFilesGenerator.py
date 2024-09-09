#!/usr/bin/env python3

"""
This class generates the additional input files needed for CoREAS.
The .reas file specifies core position (and other info).
The .list file contains the antenna positions and names of the detector.
In this generator, starshape and detector antennas (e.g. GP13) are combined.
The core position and the center of the starshape array are fixed on 0, while
the detector antennas are moved at random for each run.

@author: Jelena
"""

import numpy as np
import random
try:
    mrtools = True
    from miniradiotools.starshapes import create_stshp_list, get_starshaped_pattern_radii
except ImportError:
    mrtools = False
import sys
import os

class RadioFilesGenerator:

    _antenna_configs = ["random", "star_shaped"]

    def __init__(self,
        directory,                  # inp directory
        obslev,                     # Observation level in cm
        runNumber,                  
        log10_E1,
        pathAntennas,               # the path to the antennas.list file (the detector antennas)
        zenith,
        azimuth,
        primary,
        folder_path,

    ):
        self.directory = directory
        self.obslev = obslev
        self.runNumber = runNumber
        self.log10_E1 = log10_E1
        self.pathAntennas = pathAntennas
        self.zenith = zenith
        self.azimuth= azimuth
        self.primary = primary
        self.folder_path = folder_path
        self.antennaInfo = {}
        self.starshapeInfo = {}

        # print a warning message if miniradiotools is not installed, and simply skip running star-shaped antennas
        if not mrtools:
            print("miniradiotools is not installed. Please install to use the star-shape pattern layout.")
        self._use_mrtools = mrtools


        """
        For CoREAS it's important that all input files (inp, reas and list) are stored in the same directory.
        CoREAS uses the same directory for input and output (keyword DIRECT in .inp file) and this cannot be 
        changed.

        After the run is complete it is possible to move the files anywhere of course. 
        In SimulationMaker.py I tried to clean things up a bit by moving the DAT files to "data", but for now
        I keep all CoREAS input (inp, reas, list) and output (new .reas file, traces in "SIMxxxxxx_coreas" folder 
        and "SIMxxxxxx_coreas.bins") in "inp".

        Make sure that the value for OBSLEV specified in the .inp file is the same as CoreCoordinateVertical 
        in the .reas file and (approximately) the same for the z component of the antennas in the .list file. 
        Otherwise, CORSIKA will just crash without any explanation.
        """


    def reasWriter(self):

        # create the SIMxxxxxx ID
        sim = f"SIM{self.runNumber}"

        reas_name = f"{self.folder_path}/{sim}.reas"

        # Opening and writing in the file 
        with open(reas_name, "w") as file:
            ######Things that go into the reas file for CoREAS#######
            file.write(""
                + f"# CoREAS V1.4 parameter file\n"
                + f"# parameters setting up the spatial observer configuration:\n"
                + f"CoreCoordinateNorth = 0                ; in cm\n"
                + f"CoreCoordinateWest = 0                ; in cm\n"
                + f"CoreCoordinateVertical = {self.obslev}      ; in cm\n"
                + f"# parameters setting up the temporal observer configuration:\n"
                + f"TimeResolution = 5e-10                ; in s\n"
                + f"AutomaticTimeBoundaries = 12e-07            ; 0: off, x: automatic boundaries with width x in s\n"
                + f"TimeLowerBoundary = -1                ; in s, only if AutomaticTimeBoundaries set to 0\n"
                + f"TimeUpperBoundary = 1                ; in s, only if AutomaticTimeBoundaries set to 0\n"
                + f"ResolutionReductionScale = 0            ; 0: off, x: decrease time resolution linearly every x cm in radius\n"
                + f"# parameters setting up the simulation functionality:\n"
                + f"GroundLevelRefractiveIndex = 1.00031200        ; specify refractive index at 0 m asl\n"
                + f"# event information for Offline simulations:\n"
                + f"EventNumber = 1\n"
                + f"RunNumber = {self.runNumber} \n"
                + f"GPSSecs = 0\n"
                + f"GPSNanoSecs = 0\n"
                + f"CoreEastingOffline = 0.0000                ; in meters\n"
                + f"CoreNorthingOffline = 0.0000                ; in meters\n"
                + f"CoreVerticalOffline = 0.0000                ; in meters\n"
                + f"OfflineCoordinateSystem = Reference                ; in meters\n"
                + f"RotationAngleForMagfieldDeclination = 0.12532        ; in degrees\n"
                + f"Comment =\n"
                + f"CorsikaFilePath = ./\n"
                + f"CorsikaParameterFile = {sim}.inp"
            )


    def _get_random_positions(self):
        """
        Get gp300 positions from gp00.list and move them in x and y.
        .list files are structured like "AntennaPosition = x y z name"
        
        We want to randomly move the antennas, but also not too far from the core.
        Therefore, generate random numbers within a radius of the approximate size of the array.
        """
        
        cherenkov_radius_min = 20000 #cm
        cherenkov_radius_max = 40000 #cm
        
        while True:  # Loop until valid coordinates are generated
            dx = random.uniform(-cherenkov_radius_max, cherenkov_radius_max)
            dy = random.uniform(-cherenkov_radius_max, cherenkov_radius_max)

            # Check if the distance from (0, 0) is greater than cherenkov_radius_min
            distance = (dx**2 + dy**2)**0.5
            if distance > cherenkov_radius_min:
                break

        file = np.genfromtxt(self.pathAntennas, dtype = "str")
        # get antenna positions from file
        # file[:,0] and file[:,1] are useless (they are simply "AntennaPosition" and "=")
        # get the x, y and z positions
        self.antennaInfo["x"] = file[:,2].astype(float) + dx
        self.antennaInfo["y"] = file[:,3].astype(float) + dy
        self.antennaInfo["z"] = abs(file[:,4].astype(float))
        # get the names of the antennas
        self.antennaInfo["name"] = file[:,5]



    def _get_star_shape_positions(self):
        """
        get starshape positions from starshapes.list
        .list files are structured like "AntennaPosition = x y z name"

        """
        if self._use_mrtools:
            # create the SIMxxxxxx ID
            sim = f"SIM{self.runNumber}"
            # * * * * * * * * * * * * * *
            """
            In the best case, you don't need to touch any of this, but here's some explanation on the next few lines of code:

            miniradiotools takes (corsika_azimuth - 270) due to coordinate system fun. 
            create_stshp_list takes that value as input and returns the value you're supposed to use for corsika when using that starshape.list
            so here we need to take our self.azimuth + 270 as input for create_stshp_list for it to work properly.
            as double check, we compare the corsika_azimuth the function returns with our self.azimuth.
            if they're the same, we're good to go!
            """
            # * * * * * * * * * * * * * *

            radiotools_azimuth = self.azimuth + 270 

            print("* * * * * * * * * * * * * *")
            print("* casting starshape pattern *")
            antenna_rings = get_starshaped_pattern_radii(self.zenith, self.obslev, atm_model=41)
            # atm_model = 41: Dunhuang, China

            corsika_azimuth = create_stshp_list(self.zenith, radiotools_azimuth, filename=f"{self.directory}/{self.log10_E1}/{sim}_starshape.list", 
                            obslevel=int(self.obslev), # for Dunhuang, in cm for corsika
                            obsplane = "gp",
                            inclination=61.60523, # for Dunhuang
                            vxB_plot=False,
                            # n_rings = 20 # for 160 antennas
                            antenna_rings = antenna_rings # for 240 antennas
                            )
            print("* * * * * * * * * * * * * *")
            # check if self.azimuth is the same as the corsika_azimuth from the starshapes
            # if it is: yay!
            if self.azimuth == corsika_azimuth:
                print(f"Shower azimuth = starshape azimuth: {corsika_azimuth}")
                print(f"***** Summoning starshapes ***** with azimuth {corsika_azimuth}.")
            # if it isn't, we have a problem:
            else:
                print(f"Shower azimuth {self.azimuth}")
                print(f"Starshape azimuth {corsika_azimuth}")
                sys.exit(f"Shower and starshape azimuth are not the same! Please check the inputs and try again.")


            # use the starshape file we just generated and read the antenna positions and names from it:
            file = np.genfromtxt(f"{self.directory}/{self.log10_E1}/{sim}_starshape.list", dtype = "str")
            
            # get antenna positions from file
            # file[:,0] and file[:,1] are useless (they are simply "AntennaPosition" and "=")
            # get the x and y positions
            self.starshapeInfo["x"] = file[:,2].astype(float)
            self.starshapeInfo["y"] = file[:,3].astype(float)
            self.starshapeInfo["z"] = file[:,4].astype(float)
            # get the names of the antennas
            self.starshapeInfo["name"] = file[:,5]


    def listWriter(self):

        # create the SIMxxxxxx ID
        sim = f"SIM{self.runNumber}"

        # This is the .list file, which gets written into the folder
        list_name = f"{self.folder_path}/{sim}.list"


        # Opening and writing in the file
        with open(list_name, 'w') as f:
            # write the positions (x, y, z) and names of the starshape antennas to the .list file
            # for i in range(self.starshapeInfo["x"].shape[0]):
            #     f.write(f"AntennaPosition = {self.starshapeInfo['x'][i]} {self.starshapeInfo['y'][i]} {self.starshapeInfo['z'][i]} {self.starshapeInfo['name'][i]}\n") 
            # write the positions (x, y, z) and names of the detector's antennas to the .list file
            print("***** Summoning GP300 antennas *****")
            for i in range(self.antennaInfo["x"].shape[0]):
                f.write(f"AntennaPosition = {self.antennaInfo['x'][i]} {self.antennaInfo['y'][i]} 120000 {self.antennaInfo['name'][i]}\n") 
                

    def writeReasList(self, antenna_type : str = "random"):
        # define this to make it easier to call the functions

        self.reasWriter()

        # get the positions of the antennas for detection
        assert antenna_type in self._antenna_configs, f"Antenna type {antenna_type} is not a valid antenna configuration."

        if antenna_type == "random":
            self._get_random_positions()
        elif antenna_type == "starshape":
            # raise exception if miniradiotools is not installed
            if not self._use_mrtools:
                raise ImportError("miniradiotools is required to get star-shaped positions!")
            self._get_star_shape_positions()


        self.listWriter()

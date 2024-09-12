#!/bin/bash

# for Horeka, make sure these exact modules are loaded:
# module load compiler/gnu/10.2
# module load mpi/openmpi/4.1
PYTHON=/home/hk-project-p0022320/wb2359/miniconda3/bin/python3
SCRIPT=/home/hk-project-p0022320/wb2359/Projects/coreas/CoreasSpellcaster/MakeCorsikaSim.py

#TODO Make sure this is the right corsika path
cd /home/hk-project-p0022320/wb2359/Projects/coreas/corsika-77550/run

#TODO Make sure to change the parameters correctly. Documentation in the args of MakeCorsikaSim.py
# specifically:
#TODO check corsikaExe

$PYTHON $SCRIPT \
                --username bg5912 \
                --primary 14 \
                --dirSimulations "/home/hk-project-p0022320/wb2359/Projects/coreas/runs/" \
                --pathCorsika "/home/hk-project-p0022320/wb2359/Projects/coreas/corsika-77550/run" \
                --corsikaExe "/mpi_corsika77550Linux_SIBYLL_urqmd_thin_coreas_parallel_runner" \
                --startNumber 0 \
                --endNumber 1 \
                --energyStart 8.0 \
                --energyEnd 11.0 \
                --energyStep 0.2 \
                --zenithStart 65 \
                --zenithEnd 85 \
                --obslev 120000 \

# proton 14, iron 5626
# obslev Dunhuang 1.2 km -> 1200 m -> 120000 cm 
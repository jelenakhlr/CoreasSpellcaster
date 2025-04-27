#!/bin/bash

# for Horeka, make sure these exact modules are loaded:
# module load compiler/gnu/10.2
# module load mpi/openmpi/4.1
PYTHON=/home/hk-project-radiohfi/bg5912/virtual_env/bin/python3
SCRIPT=/home/hk-project-radiohfi/bg5912/CoreasSpellcaster/MakeCorsikaSim.py

#TODO Make sure this is the right corsika path
cd /home/hk-project-radiohfi/bg5912/work/soft/corsika-77550/run/

#TODO Make sure to change the parameters correctly. Documentation in the args of MakeCorsikaSim.py
# specifically:
#TODO check corsikaExe

$PYTHON $SCRIPT \
                --username bg5912 \
                --primary 14 \
                --dirSimulations "/home/hk-project-radiohfi/bg5912/work/sims/AERA_polarization_tests" \
                --pathCorsika "/home/hk-project-radiohfi/bg5912/work/soft/corsika-77550/run/" \
                --corsikaExe "/mpi_corsika77550Linux_SIBYLL_urqmd_thin_coreas_parallel_runner" \
                --startNumber 0 \
                --endNumber 1 \
                --energyStart 8.0 \
                --energyEnd 11.0 \
                --energyStep 0.2 \
                --zenithStart 55 \
                --zenithEnd 85 \
                --obslev 120000 \

# proton 14, iron 5626
# obslev Dunhuang 1.2 km -> 1200 m -> 120000 cm 
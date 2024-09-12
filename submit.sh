#!/bin/bash
#SBATCH --partition=dev_cpuonly
#SBATCH --job-name=sub
#SBATCH --output=/hkfs/home/project/hk-project-p0022320/wb2359/Projects/coreas/CoreasSpellcaster/../outputs/logs/log%j.out
#SBATCH --error=/hkfs/home/project/hk-project-p0022320/wb2359/Projects/coreas/CoreasSpellcaster/../outputs/logs/log%j.err
#SBATCH --nodes=2
#SBATCH --cpus-per-task=12
#SBATCH --time=03:00:00
#SBATCH --tasks=2
######SBATCH --mem=50gb
######SBATCH --export=NONE
#######################SBATCH --gres=gpu:4

export PYTHON=/home/hk-project-p0022320/wb2359/miniconda3/bin/python
export SCRIPT=/hkfs/home/project/hk-project-p0022320/wb2359/Projects/coreas/CoreasSpellcaster/MakeCorsikaSim.py

$PYTHON $SCRIPT --username wb2359                 --primary 14                 --dirSimulations /hkfs/home/project/hk-project-p0022320/wb2359/Projects/coreas/CoreasSpellcaster/../outputs                 --pathCorsika /hkfs/home/project/hk-project-p0022320/wb2359/Projects/coreas/CoreasSpellcaster/../corsika-77550/run                 --corsikaExe mpi_corsika77550Linux_SIBYLL_urqmd_thin_coreas_parallel_runner                 --startNumber 0                 --endNumber 1                 --energyStart 8.0                 --energyEnd 8.2                 --energyStep 0.2                 --zenithStart 65.0                 --zenithEnd 65.0                 --obslev 120000.0                 --antenna_type random 
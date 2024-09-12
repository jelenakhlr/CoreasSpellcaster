import os, sys
import shutil
import argparse
import numpy as np

dir_name = os.path.dirname(os.path.realpath(__name__))
pythonexec_path = sys.executable

parser = argparse.ArgumentParser(
        description="Inputs for the Corsika Simulation Maker"
)

parser.add_argument(
    "--username", 
    type=str, 
    default="wb2359", 
    help="your user name on server"
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
    "--inputParameterFile",
    type=str,
    default=os.path.join(dir_name, "input_file.txt"),
    help="Input parameters for MakeCorsikaSim.py"
)
parser.add_argument(
    "--antenna_type",
    type=str,
    default="random",
    help="type of antenna layout",
    choices=["random", "starshape"]
)

parser.add_argument(
    "--dryrun",
    action="store_true",
    help="write out the file, but dont submit it.",
)

parser.add_argument(
    "--debug",
    action="store_true",
    help="submit with devel partition for testing",
)

args = parser.parse_args()

# read input parameters
primary, start_num, end_num, en_start, en_end, en_step, zen_start, zen_end, obs_lvl = np.genfromtxt(args.inputParameterFile, skip_header=1)

# verify that the filepaths are setup correctly, if not raise an error
if not os.path.exists(args.dirSimulations):
    raise NotADirectoryError(f"Directory {args.dirSimulations} does not exist, please create it!")

if not os.path.exists(args.pathCorsika):
    raise NotADirectoryError(f"Directory {args.pathCorsika} does not exist, unpack corsika package to this path!")

if not os.path.exists(os.path.join(args.pathCorsika, args.corsikaExe)):
    raise FileNotFoundError(f"Corsika executable {args.corsikaExe} not found, check if you compiled the executable correctly.")

# create log directory in simulation directory
# if it already exists, remove it first
log_dir = os.path.join(args.dirSimulations, "logs")
if os.path.exists(log_dir):
    [os.remove(os.path.join(log_dir, f)) for f in os.listdir(log_dir)]
    os.removedirs(log_dir)
os.mkdir(log_dir)

# partition
partition_type = "dev_cpuonly" if args.debug else "cpu_only"

# submit file template
subfile = f"""#!/bin/bash
#SBATCH --partition={partition_type}
#SBATCH --job-name=sub
#SBATCH --output={args.dirSimulations}/logs/log%j.out
#SBATCH --error={args.dirSimulations}/logs/log%j.err
#SBATCH --nodes=2
#SBATCH --cpus-per-task=12
#SBATCH --time=03:00:00
#SBATCH --tasks=2
######SBATCH --mem=50gb
######SBATCH --export=NONE
#######################SBATCH --gres=gpu:4

export PYTHON={pythonexec_path}
export SCRIPT={dir_name}/MakeCorsikaSim.py

$PYTHON $SCRIPT --username {args.username} \
                --primary {int(primary)} \
                --dirSimulations {args.dirSimulations} \
                --pathCorsika {args.pathCorsika} \
                --corsikaExe {args.corsikaExe} \
                --startNumber {int(start_num)} \
                --endNumber {int(end_num)} \
                --energyStart {en_start} \
                --energyEnd {en_end} \
                --energyStep {en_step} \
                --zenithStart {zen_start} \
                --zenithEnd {zen_end} \
                --obslev {obs_lvl} \
                --antenna_type {args.antenna_type} \
"""

# write to file
submit_filepath = os.path.join(dir_name, "submit.sh")
with open(submit_filepath, "w") as f:
    f.write(subfile)

if args.dryrun:
    print(subfile)
else:
    os.system(f"sbatch {submit_filepath}")
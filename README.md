# CoreasSpellcaster
Unleash the magic of simultaneous shower simulations with this Coreas generator.

### Authors
Keito Watanabe @kwat0308\
Jelena Köhler @jelenakhlr\
original version by @fedbont94\
forked from https://github.com/fedbont94/Horeka\
@date: September 2024

## Installation

The spellcaster can now be readily installed via pip:
```
pip install coreas_spellcaster
```

This will install the necessary dependencies:
- `numpy`

## Optional Dependencies

- [miniradiotools](https://github.com/jelenakhlr/miniradiotools) : for using star-shaped antenna layout

## Usage

1. Compile the version of Corsika you need\
for mpi: Make sure to use the **PARALLEL** option and to compile with **MPILIBRARY** (do not use these for non-mpi)

   For more info, see the [**Corsika** manual](https://web.iap.kit.edu/corsika/usersguide/usersguide.pdf) and the [**Coreas** manual](https://web.ikp.kit.edu/huege/downloads/coreas-manual.pdf).

2. Run `generate_and_submit_subfile.py` to generate and submit the `submit.sh` file. 

   **NB: the submit file is configured for a SLURM batch system. Other batch systems (e.g. HTcondor) will be implemented in the future.**

   Here, the following should be specified:
   - `--username` : your username in the batch system
   - `--dirSimulations` : the directory to where the simulations are stored
   - `--pathCorsika` : the path to the corsika run directory ("$CORSIKA_PATH/runs")
   - `--corsikaExec` : the executable for corsika
   - `--antenna_type` : the type of antenna layout to use. Either `random` or `starshape` is available for now.

   The relevant input parameters can be modified in `input_file.txt`.

   To test the implementation, one can use the `--dryrun` flag to write the submission script, and `--debug` to run on a development partition.

Running this should submit a script that manages the corsika simulations, gathers the outputs, and sort them in a coherent manner.

## General Information
by @fedbont94

`MakeCorsikaSim.py` - Is the main script that for Corsika air shower simulation (more documentation in the script) \
`MakeDetectorResponse.py` - Is the main script that for detector response simulation (more documentation in the script)


`utils/FileWriter.py` -       Contains a class that can be used to create and write a Corsika inp file and create "data", "temp", "log", "inp" folders. \
                            (more documentation in the script)

                            
`utils/SimulationMaker.py` -  Contains a class that can be used for generating the submission stings and sh executable files. \
                            It also has the generator function which yields the keys and string to submit, 
                            made via the combinations of file and energies \
                            (more documentation in the script)

                            
`utils/Submitter.py` -        Contains a class that can be used to spawns subprocesses for multiple instances instead of multiple job submissions.
                            (more documentation in the script)\
                            

`utils/DetectorSimulator.py` - Contains a class that can be used to simulate the detector response for a given corsika file. \
                            (more documentation in the script)
                            
                            
`utils/MultiProcesses.py` -   Contains a class that can be used to spawn multiple processes for the detector response simulation. \
                            (more documentation in the script)

## LICENSE
This work is under the BSD-3 LICENSE. See [LICENSE](./LICENSE) for details.

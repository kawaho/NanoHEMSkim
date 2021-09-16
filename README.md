# NanoHEMSkim
This is a repository to produce skimmed NanoAOD files for H -> e + mu analysis. Follow instructions in and clone https://github.com/cms-nanoAOD/nanoAOD-tools. Then clone this repository to $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/.
# Get sample/dataset paths
To produce json files of sample/dataset paths:
```bash
python get_das_info.py 
```
# Submit CRAB jobs
First go to the `./crab` directory set up the env
```bash
source setup.sh 
```
and clean all previous CRAB jobs (use this carefully as this will remove all your CRAB files)
```bash
source cleaning.sh 
```
Then submit jobs
```bash
python crab_cfg.py ../NanoAODUL_2017_data.json 
```
# Resubmit CRAB jobs
To resubmit failed CRAB jobs, do
```bash
python resubmit.py -f
```
which also creates a json file named ```finishedJobs.json``` that contains a list of the finished jobs. The option ```-f``` creates a new ```finishedJobs.json``` for a new patch of CRAB jobs. Omit ```-f``` if ```finishedJobs.json``` was already created for the patch of jobs.
# Local run
To test locally before submitting to CRAB, uncomment and put your input files to the inputFiles list in ```crab_script.py``` and replae all ```inputFiles()``` to ```inputFiles```. Then do
```bash
python crab_script.py --isMC $isMC --era $ERA
```

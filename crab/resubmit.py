import CRABClient
from CRABAPI.RawCommand import crabCommand
import json, glob, argparse
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fresh', action='store_true', help='Fresh patch of crab jobs')
args = parser.parse_args()

list_of_jobs = glob.glob('/afs/cern.ch/work/k/kaho/crabspace/*')

if args.fresh:
  list_of_finished_jobs = []
else:
  with open('finishedJobs.json') as f:
    list_of_finished_jobs = json.load(f)

for job in list_of_jobs:
  if job in list_of_finished_jobs:
    continue
  else:
    res = crabCommand('status', dir = job)
    if any(['failed' in i for i in res['jobList']]):
      res = crabCommand('resubmit', dir = job)
    elif all(['finished' in i for i in res['jobList']]):
      list_of_finished_jobs.append(job)
with open('finishedJobs.json', 'w') as f: 
  json.dump(list_of_finished_jobs, f)


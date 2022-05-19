import subprocess
import json
import pandas as pd

def get_das_info(query):
    '''Interface with das.py to get the query output.
    Could be done better, but this is time effective.
    Unfortunately the QL is more complicated than the 
    DBS one. '''
    
    das_command = [ 
        'dasgoclient',
        '--query=%s' % query,
        '--limit=0' 
        ]   
    p = subprocess.Popen(
        das_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )   
    out, err = p.communicate()
    das_exitcode = p.wait()
    
    if das_exitcode <> 0:
        #sometimes das sends the crash message to stdout
        raise RuntimeError('das.py crashed with error:\n%s' % err+out ) 
    return [i.strip() for i in out.split('\n') if i.strip()]

campaigns = {'2016preVFP':'RunIISummer20UL16NanoAODAPVv9-*', '2016postVFP':'RunIISummer20UL16NanoAODv9-*', '2017':'RunIISummer20UL17NanoAODv9-*', '2018':'RunIISummer20UL18NanoAODv9-*'}
#campaigns = {'2016preVFP':'RunIISummer20UL16NanoAODAPVv2-*', '2016postVFP':'RunIISummer20UL16NanoAODv2-*', '2017':'RunIISummer20UL17NanoAODv2-*', '2018':'RunIISummer20UL18NanoAODv2-*'}
#campaigns = {'2016':'*RunIISummer16NanoAODv3*'}
missing_samples = {'2016preVFP':[], '2016postVFP':[], '2017':[], '2018':[]}

with open("NanoAOD_HEM_MC_FULL.json", 'r') as f:
  MC_names = json.load(f)
  print(MC_names)
for year, campaign in campaigns.iteritems():
  print "----------------------Checking MC samples DAG for year %s----------------------"%year
  allsamples = {}
  for MC_shorthand, MC_name in MC_names.iteritems():
    sample = get_das_info("/*%s*/%s/*"%(MC_name,campaign))
    if sample:
      allsamples[MC_shorthand]=list(sample)
      print "%s Found!!"%MC_name
      if len(sample) > 1: 
        print "!!%s has duplicates!!"%MC_name
	for subsample in sample:
          if 'ext' in subsample:
            allsamples.setdefault(MC_shorthand+'_ext',[]).append(subsample)
            allsamples[MC_shorthand].remove(subsample)
          if 'JMENano' in subsample or 'Pilot' in subsample:
            allsamples[MC_shorthand].remove(subsample) 
    else:
      print "%s is Missing!!"%MC_name
      missing_samples[year].append(MC_name)
  with open("NanoAODUL_%s_MC.json"%year, 'w') as f:
    json.dump(allsamples, f, indent=4, sort_keys=True)
with open("MissingSamples.json", 'w') as f:
  json.dump(missing_samples, f, indent=4, sort_keys=True)

#campaigns = {'2016':'*RunIISummer16NanoAODv3*'}
campaigns = {'2016':'Run2016*UL2016_MiniAODv2_NanoAODv9-v*', '2017':'Run2017*-UL2017_MiniAODv2_NanoAODv9-v*', '2018':'Run2018*-UL2018_MiniAODv2_NanoAODv9-*'}
#campaigns = {'2016':'Run2016*UL2016_MiniAODv1_NanoAODv2-v*', '2017':'Run2017*-UL2017_MiniAODv1_NanoAODv2-v*', '2018':'Run2018*-UL2018_MiniAODv1_NanoAODv2-*'}
dataNames = ['SingleMuon']
for year, campaign in campaigns.iteritems():
  print "----------------------Checking DATA samples DAG for year %s----------------------"%year
  allsamples = {}
  for dataname in dataNames:
    sample = get_das_info("/%s/%s/*"%(dataname,campaign))
    if sample:
      for run in sample:
        runName = run.split("/")[2].split("_")[0]
        subsample = dataname+'_'+runName
        if subsample in allsamples: 
          allsamples[subsample].append(run)
        else:
          allsamples[subsample]=[run]
        print "%s Found!!"%(subsample)
  if year=='2016':
    allsamplespostVFP,  allsamplespreVFP = {}, {}
    for shorthand2016, names2016 in allsamples.iteritems():     
      if '2016F-UL' in shorthand2016 or '2016G-' in shorthand2016 or '2016H-' in shorthand2016:
        allsamplespostVFP[shorthand2016]= names2016
      else: 
        allsamplespreVFP[shorthand2016] = names2016
 
    with open("NanoAODUL_2016preVFP_data.json", 'w') as f:
      json.dump(allsamplespreVFP, f, indent=4, sort_keys=True)
    with open("NanoAODUL_2016postVFP_data.json", 'w') as f:
      json.dump(allsamplespostVFP, f, indent=4, sort_keys=True)
  else:
    with open("NanoAODUL_%s_data.json"%year, 'w') as f:
      json.dump(allsamples, f, indent=4, sort_keys=True)



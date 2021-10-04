#from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config#, getUsernameFromSiteDB
import sys
import json

config = config()
config.section_("General")
config.General.requestName = 'NanoPost1'
config.General.transferLogs = True
config.General.workArea = '/afs/cern.ch/work/k/kaho/crabspace/'
config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script.sh'
# hadd nano will not be needed once nano tools are in cmssw
config.JobType.inputFiles = ['crab_script.py', '../../../../scripts/haddnano.py', 'keep_and_drop_in.txt', 'keep_and_drop_out.txt']
config.JobType.sendPythonFolder = True
config.JobType.scriptArgs = ['isMC=1','era=2018']
config.section_("Data")
config.Data.inputDataset = '/GluGlu_LFV_HToEMu_M125_TuneCP5_13TeV_PSweights_powheg_pythia8/RunIISummer20UL18NanoAODv2-106X_upgrade2018_realistic_v15_L1v1-v1/NANOAODSIM'
#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
#config.Data.splitting = 'LumiBased'
#config.Data.unitsPerJob = 250
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
#config.Data.splitting = 'EventAwareLumiBased'
#config.Data.totalUnits = 10

config.Data.outLFNDirBase = '/store/user/kaho/NanoPost_' 
#config.Data.outLFNDirBase = '/store/user/%s/NanoPost' % (
#    getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'NanoTestPost'
config.section_("Site")
config.Site.storageSite = "T2_US_Wisconsin"
#config.Site.storageSite = "T3_US_NotreDame"

#config.Site.storageSite = "T2_CH_CERN"
# config.section_("User")
#config.User.voGroup = 'dcms'

if __name__ == '__main__':
    f=open(sys.argv[1]) 
    era = sys.argv[1].split('_')[1]
    isMC = 1 if 'MC' in sys.argv[1] else 0
    samples = json.load(f)
    print 'isMC=%s'%isMC,'era=%s'%era
    from CRABAPI.RawCommand import crabCommand
    if not isMC:
      config.Data.splitting = 'LumiBased'
      config.Data.unitsPerJob = 250
      if '2016' in era:
        config.Data.lumiMask = 'Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt'
      elif era=='2017':
        config.Data.lumiMask = 'Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt'
      elif era=='2018':
        config.Data.lumiMask = 'Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt'
      config.JobType.inputFiles.append(config.Data.lumiMask)
    for sample_shorthand, sample in samples.iteritems():
        print "Submitting Jobs for "+sample_shorthand
        assert (len(sample) == 1), "Multiple VERs of samples are imported! Pick one!"
        config.Data.outLFNDirBase = '/store/user/kaho/NanoPost_'+era+'_v1p4'
        config.Data.inputDataset = sample[0]
        config.General.requestName = sample_shorthand+'_'+era
        config.Data.outputDatasetTag = sample_shorthand
        config.JobType.scriptArgs = ['isMC=%s'%isMC,'era=%s'%era]
        crabCommand('submit', config=config)#, dryrun=True)

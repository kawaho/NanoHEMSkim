#!/usr/bin/env python
import os
import argparse

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *

# this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles, runsAndLumis

from PhysicsTools.NanoAODTools.postprocessing.examples.exampleModule import *

from PhysicsTools.NanoAODTools.postprocessing.modules.common.muonScaleResProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSFProducer_v2 import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *

from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
#from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducerV2 import *

from PhysicsTools.NanoAODTools.postprocessing.NanoHEMSkim.cleaning_superfast import *
from PhysicsTools.NanoAODTools.postprocessing.NanoHEMSkim.Zpt_reweight import *

parser = argparse.ArgumentParser("")
parser.add_argument('-jobNum', '--jobNum', type=str, default='1', help="")
parser.add_argument('-isMC', '--isMC', type=int, default=1, help="")
parser.add_argument('-era', '--era', type=str, default="2017", help="")
args = parser.parse_args()
print "args = ",args
isMC = args.isMC
era = args.era
print "isMC = ",isMC," era = ",era

ElectronVeto = "(Electron_pt > 10 && abs(Electron_eta) < 2.5 && Electron_mvaFall17V2noIso_WP90 && Electron_convVeto && abs(Electron_dxy) < 0.045 && abs(Electron_dz) < 0.2 && Electron_pfRelIso03_all < 0.3)"

ElectronSel = "(Electron_pt > 24 && abs(Electron_eta) < 2.5 && Electron_mvaFall17V2noIso_WP80 && Electron_convVeto && abs(Electron_dxy) < 0.045 && abs(Electron_dz) < 0.2 && Electron_pfRelIso03_all < 0.1 && Electron_lostHits<2)"

MuonVeto = "(Muon_pt > 10 && abs(Muon_eta) < 2.4 && Muon_mediumId && abs(Muon_dxy) < 0.045 && abs(Muon_dz) < 0.2 && Muon_pfRelIso04_all < 0.3)"

MuonSel = "(Muon_pt > 24 && abs(Muon_eta) < 2.4 && Muon_tightId && abs(Muon_dxy) < 0.045 && abs(Muon_dz) < 0.2 && Muon_pfRelIso04_all < 0.15)"

MuonSel_low = "(Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_tightId && abs(Muon_dxy) < 0.045 && abs(Muon_dz) < 0.2 && Muon_pfRelIso04_all < 0.15)"

selections_emu="(Sum$(%s&&!%s)==0 && Sum$(%s)==1 && Sum$(%s&&!%s)==0 && Sum$(%s)==1)"%(ElectronVeto, ElectronSel, ElectronSel, MuonVeto, MuonSel, MuonSel)

selections_mumu="(Sum$(%s)==0 && Sum$(%s&&!%s)==0 && Sum$(%s)==2)"%(ElectronVeto, MuonVeto, MuonSel_low, MuonSel_low)

METFilters = "(Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_eeBadScFilter && Flag_eeBadScFilter)" # && Flag_BadPFMuonDzFilter 

if not '2016' in era:
  METFilters.replace(")",  "&& Flag_ecalBadCalibFilter)")

#selections = "("+selections_emu+")&&"+METFilters
selections = "("+selections_emu+"||"+selections_mumu+")&&"+METFilters+"&&(PV_npvsGood > 0)"

#inputFiles = ["../../../../GG.root"]
if era == "2018":
  jmeCorrections_2018UL = createJMECorrector(isMC=True, dataYear="UL2018", jesUncert="Merged", applyHEMfix=True)
  jmeCorrections_2018UL_data = createJMECorrector(isMC=False, dataYear="UL2018", jesUncert="Merged")
  if isMC:
    p = PostProcessor(".",
                  inputFiles(),
                  selections,
                  branchsel="keep_and_drop_in.txt",
                  outputbranchsel="keep_and_drop_out.txt",
                  modules=[jmeCorrections_2018UL(), cleaning_2018UL(), MuonSFTrig_2018UL(), MuonSFID_2018UL(), MuonSFISO_2018UL(), ElectronSFReco_2018UL(), ElectronSFID_2018UL(), btagSF_jet_2018UL(), puWeight_UL2018(), Zpt_reweightUL(), muonScaleRes2018UL()],
                  provenance=True,
                  fwkJobReport=True,
                  jsonInput=runsAndLumis())
  else:
    p = PostProcessor(".",
                  inputFiles(),
                  selections,
                  branchsel="keep_and_drop_in.txt",
                  outputbranchsel="keep_and_drop_out.txt",
                  modules=[jmeCorrections_2018UL_data(), cleaning_2018UL(), muonScaleRes2018UL()],
                  provenance=True,
                  fwkJobReport=True,
                  jsonInput=runsAndLumis())
elif era == "2017":
  jmeCorrections_2017UL = createJMECorrector(isMC=True, dataYear="UL2017", jesUncert="Merged")
  jmeCorrections_2017UL_data = createJMECorrector(isMC=False, dataYear="UL2017", jesUncert="Merged")
  if isMC:
    p = PostProcessor(".",
                  inputFiles(),
                  selections,
                  branchsel="keep_and_drop_in.txt",
                  outputbranchsel="keep_and_drop_out.txt",
                  modules=[jmeCorrections_2017UL(), cleaning_2017UL(), PrefCorr_2017UL(), MuonSFTrig_2017UL(), MuonSFID_2017UL(), MuonSFISO_2017UL(), ElectronSFReco_2017UL(), ElectronSFID_2017UL(), btagSF_jet_2017UL(), puWeight_UL2017(), muonScaleRes2017UL(), Zpt_reweightUL()], #btagSF_csv_2017UL()
                  provenance=True,
                  fwkJobReport=True,
                  jsonInput=runsAndLumis())
  else:
    p = PostProcessor(".",
                  inputFiles(),
                  selections,
                  branchsel="keep_and_drop_in.txt",
                  outputbranchsel="keep_and_drop_out.txt",
                  modules=[jmeCorrections_2017UL_data(), cleaning_2017UL(), muonScaleRes2017UL()],
                  provenance=True,
                  fwkJobReport=True,
                  jsonInput=runsAndLumis())

elif era == "2016postVFP":
  METFilters = METFilters2016
  jmeCorrections_2016postVFPUL = createJMECorrector(isMC=True, dataYear="UL2016", jesUncert="Merged")
  jmeCorrections_2016postVFPUL_data = createJMECorrector(isMC=False, dataYear="UL2016", jesUncert="Merged")
  if isMC:
    p = PostProcessor(".",
                  inputFiles(),
                  selections,
                  branchsel="keep_and_drop_in.txt",
                  outputbranchsel="keep_and_drop_out.txt",
                  modules=[jmeCorrections_2016postVFPUL(), PrefCorr_2016postVFPUL(), MuonSFTrig_2016postVFPUL(), MuonSFID_2016postVFPUL(), MuonSFISO_2016postVFPUL(), ElectronSFReco_2016postVFPUL(), ElectronSFID_2016postVFPUL(), cleaning_2016postVFPUL(), btagSF_jet_2016postVFPUL(), puWeight_UL2016(), Zpt_reweightUL(), muonScaleRes2016postVFPUL()],
                  provenance=True,
                  fwkJobReport=True,
                  jsonInput=runsAndLumis())
  else:
    p = PostProcessor(".",
                  inputFiles(),
                  selections,
                  branchsel="keep_and_drop_in.txt",
                  outputbranchsel="keep_and_drop_out.txt",
                  modules=[jmeCorrections_2016postVFPUL_data(), cleaning_2016postVFPUL(), muonScaleRes2016postVFPUL()],
                  provenance=True,
                  fwkJobReport=True,
                  jsonInput=runsAndLumis())

elif era == "2016preVFP":
  METFilters = METFilters2016
  jmieCorrections_2016preVFPUL = createJMECorrector(isMC=True, dataYear="UL2016_preVFP", jesUncert="Merged")
  jmieCorrections_2016preVFPUL_data = createJMECorrector(isMC=False, dataYear="UL2016_preVFP", jesUncert="Merged")
  if isMC:
    p = PostProcessor(".",
                  inputFiles(),
                  selections,
                  branchsel="keep_and_drop_in.txt",
                  outputbranchsel="keep_and_drop_out.txt",
                  modules=[jmeCorrections_2016preVFPUL(), PrefCorr_2016preVFPUL(), MuonSFTrig_2016preVFPUL(), MuonSFID_2016preVFPUL(), MuonSFISO_2016preVFPUL(), ElectronSFReco_2016preVFPUL(), ElectronSFID_2016preVFPUL(), cleaning_2016preVFPUL(), btagSF_jet_2016preVFPUL(), puWeight_UL2016(), Zpt_reweightUL(), muonScaleRes2016preVFPUL()],
                  provenance=True,
                  fwkJobReport=True,
                  jsonInput=runsAndLumis())
  else:
    p = PostProcessor(".",
                  inputFiles(),
                  selections,
                  branchsel="keep_and_drop_in.txt",
                  outputbranchsel="keep_and_drop_out.txt",
                  modules=[jmeCorrections_2016preVFPUL_data(), cleaning_2016preVFPUL(), muonScaleRes2016preVFPUL()],
                  provenance=True,
                  fwkJobReport=True,
                  jsonInput=runsAndLumis())


p.run()
print("DONE")

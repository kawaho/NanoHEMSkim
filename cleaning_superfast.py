from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class cleaning(Module):
    def __init__(self, era="2018", runJEC=True):
        self.era = era
        self.runJEC = runJEC
        #https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation
        #using 2017 for 2016 at the moment 
        self.btag_WP = {
          'deepcsv': {
             "L": {'2016ULpreVFP': 0.2027, '2016ULpostVFP': 0.1918, '2017UL': 0.1355, '2018UL': 0.1208},
             "M": {'2016ULpreVFP': 0.6001, '2016ULpostVFP': 0.5847, '2017UL': 0.4506, '2018UL': 0.4168},
             "T": {'2016ULpreVFP': 0.8819, '2016ULpostVFP': 0.8767, '2017UL': 0.7738, '2018UL': 0.7665},
          },
          'deepjet': {
             "L": {'2016ULpreVFP': 0.0508, '2016ULpostVFP': 0.0480, '2017UL': 0.0532, '2018UL': 0.0490},
             "M": {'2016ULpreVFP': 0.2598, '2016ULpostVFP': 0.2489, '2017UL': 0.3040, '2018UL': 0.2783},
             "T": {'2016ULpreVFP': 0.6502, '2016ULpostVFP': 0.6377, '2017UL': 0.7476, '2018UL': 0.7100},
          }
        } 
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        # -1 should be rejected, 1 is mm, 0 is em
        self.out.branch("channel", "I")
        self.out.branch("channelIso", "I")
        self.out.branch("nJet30", "I")
        self.out.branch("Jet_passJet30ID", "b", lenVar="nJet")
        self.out.branch("Jet_passDeepJet_L", "b", lenVar="nJet")
        self.out.branch("Jet_passDeepJet_M", "b", lenVar="nJet")
        self.out.branch("Jet_passDeepJet_T", "b", lenVar="nJet")
#        self.out.branch("Jet_passDeepCSV_L", "b", lenVar="nJet")
#        self.out.branch("Jet_passDeepCSV_M", "b", lenVar="nJet")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def tauVeto(self, Leps, Taus):
	#Dont need t.idDecayModeNewDMs for tau since its the default
        if len(Leps)==2:
          return bool(len(filter(lambda t: ((t.p4().DeltaR(Leps[0]) > 0.4 and t.p4().DeltaR(Leps[1]) > 0.4) and t.pt>20 and abs(t.eta)<2.3 and t.idDeepTau2017v2p1VSjet>8 and abs(t.dz) < 0.2), Taus)) > 0)
        else:
          return True

    def LepOverlap(self, Leps):
        if len(Leps)==2:
          return bool(Leps[0].DeltaR(Leps[1]) < 0.3)
        else:
          return True

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        jets = Collection(event, "Jet")
        Electrons = Collection(event, "Electron")
        Muons = Collection(event, "Muon")
        Taus = Collection(event, "Tau")

        channel = -1
        channel_iso = -1
     
        Leps_em_iso = []
        Leps_em_noiso = []
        Leps_mm = []

        for e in Electrons:
          if (e.pt > 20 and abs(e.eta) < 2.5 and e.mvaFall17V2Iso_WP80 and e.convVeto and abs(e.dxy) < 0.05 and abs(e.dz) < 0.2 and e.lostHits < 2):
            Leps_em_iso.append(e.p4())
          if (e.pt > 20 and abs(e.eta) < 2.5 and e.mvaFall17V2noIso_WP80 and e.convVeto and abs(e.dxy) < 0.05 and abs(e.dz) < 0.2 and e.pfRelIso03_all < 0.1 and e.lostHits < 2):
            Leps_em_noiso.append(e.p4())
        nE_iso = len(Leps_em_iso)
        nE_noiso = len(Leps_em_noiso)
        for m in Muons:
          if (m.pt > 15 and abs(m.eta) < 2.4 and m.tightId and abs(m.dxy) < 0.05 and abs(m.dz) < 0.2 and m.pfRelIso04_all < 0.15):
            Leps_mm.append(m.p4())
            Leps_em_iso.append(m.p4())
            Leps_em_noiso.append(m.p4())

        if nE_iso==1 and not self.tauVeto(Leps_em_iso, Taus) and not self.LepOverlap(Leps_em_iso):
          channel_iso = 0
        if nE_noiso==1 and not self.tauVeto(Leps_em_noiso, Taus) and not self.LepOverlap(Leps_em_noiso):
          channel = 0
        elif not self.tauVeto(Leps_mm, Taus) and not self.LepOverlap(Leps_mm):
          channel = 1
       
        self.out.fillBranch("channel", channel)
        self.out.fillBranch("channelIso", channel_iso)

        passJet30ID = []
        passDeepJet_L = []
        passDeepJet_M = []
        passDeepJet_T = []
#        passDeepCSV_L = []
#        passDeepCSV_M = []

        if channel!=-1:
          if channel == 0:
            Leps = Leps_em_noiso
          elif channel_iso == 0:
            Leps = Leps_em_iso
          else:
            Leps = Leps_mm
          for j in jets:
            jp4 = j.p4()
            jpt = j.pt_nom if self.runJEC else j.pt
            #puID Tight and Loose bits are flipped for 2016 v9
            puID = (j.puId&1) if '2016' in self.era else (j.puId>>2)&1
            if ((j.jetId>>1)&1 and abs(j.eta)<4.7 and (puID or jpt > 50) and jp4.DeltaR(Leps[0]) > 0.4 and jp4.DeltaR(Leps[1]) > 0.4) and (jpt > 30):

              passJet30ID.append(1) 

              if abs(j.eta)<2.5:
                if j.btagDeepFlavB > self.btag_WP['deepjet']["T"][self.era]:
                  passDeepJet_L.append(1) 
                  passDeepJet_M.append(1) 
                  passDeepJet_T.append(1) 
                elif j.btagDeepFlavB > self.btag_WP['deepjet']["M"][self.era]:
                  passDeepJet_L.append(1) 
                  passDeepJet_M.append(1) 
                  passDeepJet_T.append(0) 
                elif j.btagDeepFlavB > self.btag_WP['deepjet']["L"][self.era]:
                  passDeepJet_L.append(1) 
                  passDeepJet_M.append(0) 
                  passDeepJet_T.append(0) 
                else:
                  passDeepJet_L.append(0) 
                  passDeepJet_M.append(0) 
                  passDeepJet_T.append(0) 

                #if j.btagDeepB > self.btag_WP['deepcsv']["M"][self.era]:
                #  passDeepCSV_L.append(1) 
                #  passDeepCSV_M.append(1) 
                #elif j.btagDeepB > self.btag_WP['deepcsv']["L"][self.era]:
                #  passDeepCSV_L.append(1) 
                #  passDeepCSV_M.append(0) 
                #else:
                #  passDeepCSV_L.append(0) 
                #  passDeepCSV_M.append(0) 
              else:
                passDeepJet_L.append(0) 
                passDeepJet_M.append(0) 
                passDeepJet_T.append(0) 
                #passDeepCSV_L.append(0) 
                #passDeepCSV_M.append(0) 
            else:
              passJet30ID.append(0) 
              passDeepJet_L.append(0) 
              passDeepJet_M.append(0) 
              passDeepJet_T.append(0) 
              #passDeepCSV_L.append(0) 
              #passDeepCSV_M.append(0) 

          self.out.fillBranch("nJet30", sum(passJet30ID))
          self.out.fillBranch("Jet_passJet30ID", passJet30ID)
          self.out.fillBranch("Jet_passDeepJet_L", passDeepJet_L)
          self.out.fillBranch("Jet_passDeepJet_M", passDeepJet_M)
          self.out.fillBranch("Jet_passDeepJet_T", passDeepJet_T)
#          self.out.fillBranch("Jet_passDeepCSV_L", passDeepCSV_L)
#          self.out.fillBranch("Jet_passDeepCSV_M", passDeepCSV_M)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

cleaning_2016preVFPUL = lambda: cleaning("2016ULpreVFP")
cleaning_2016postVFPUL = lambda: cleaning("2016ULpostVFP")
cleaning_2017UL = lambda: cleaning(era="2017UL")
cleaning_2018UL = lambda: cleaning("2018UL")

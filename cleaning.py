from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class cleaning(Module):
    def __init__(self, era="2018"):
        self.era = era
        #https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation
        #using 2017 for 2016 at the moment 
        self.btag_WP = {
          'deepcsv': {
             "L": {'2016UL': 0.1355, '2017UL': 0.1355, '2018UL': 0.1208},
             "M": {'2016UL': 0.4506, '2017UL': 0.4506, '2018UL': 0.4168},
          },
          'deepjet': {
             "L": {'2016UL': 0.0532, '2017UL': 0.0532, '2018UL': 0.0490},
             "M": {'2016UL': 0.3040, '2017UL': 0.3040, '2018UL': 0.2783},
          }
        } 
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        # 2 should be rejected, 1 is mm, 0 is em
        self.out.branch("channel", "I")
        self.out.branch("Electron_Tagged", "b", lenVar="nElectron")
        self.out.branch("Muon_Tagged", "b", lenVar="nMuon")
        self.out.branch("nJet30", "I")
        self.out.branch("Jet_passJet30ID", "b", lenVar="nJet")
#        self.out.branch("nbJet20_deepcsv_L", "I")
#        self.out.branch("nbJet20_deepcsv_M", "I")
        self.out.branch("nbJet20_deepjet_L", "I")
        self.out.branch("Jet_passDeepJet_L", "b", lenVar="nJet")
        self.out.branch("nbJet20_deepjet_M", "I")
        self.out.branch("Jet_passDeepJet_M", "b", lenVar="nJet")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def tauVeto(self, Leps, Taus):
        if len(Leps)==2:
          return bool(len(filter(lambda t: ((t.p4().DeltaR(Leps[0]) > 0.4 and t.p4().DeltaR(Leps[1]) > 0.4) and t.pt>20 and abs(t.eta)<2.3 and t.idDeepTau2017v2p1VSjet>8), Taus)) > 0)
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
        eTagged, mTagged = [], []
        Leps_em = []
        Leps_mm = []

        for e in Electrons:
          if (e.pt > 24 and abs(e.eta) < 2.5 and e.mvaFall17V2noIso_WP80 and e.convVeto and abs(e.dxy) < 0.045 and abs(e.dz) < 0.2):
            eTagged.append(1)
            Leps_em.append(e.p4())
          else:
            eTagged.append(0)

        for m in Muons:
          if (m.pt > 15 and abs(m.eta) < 2.4 and m.tightId and abs(m.dxy) < 0.045 and abs(m.dz) < 0.2):
            mTagged.append(1)
            Leps_mm.append(m.p4())
            if (m.pt > 24):
              Leps_em.append(m.p4())
          else:
            mTagged.append(0)

        self.out.fillBranch("Electron_Tagged", eTagged)
        self.out.fillBranch("Muon_Tagged", mTagged)
      
        if not self.tauVeto(Leps_em, Taus) and not self.LepOverlap(Leps_em):
          channel = 0
        elif not self.tauVeto(Leps_mm, Taus) and not self.LepOverlap(Leps_mm):
          channel = 1
        else:
          channel = -1
       

        self.out.fillBranch("channel", channel)

        nJet30 = 0 
        passJet30ID = []
        #nbJet20_deepcsv_L = 0 
        #nbJet20_deepcsv_M = 0 
        nbJet20_deepjet_L = 0 
        passDeepJet_L = []
        nbJet20_deepjet_M = 0 
        passDeepJet_M = []
        for j in jets:
          if channel==-1: 
            passJet30ID.append(0) 
            passDeepJet_L.append(0) 
            passDeepJet_M.append(0) 
            continue

          jp4 = j.p4()
          jp4.SetPtEtaPhiM(j.pt_nom, jp4.Eta(), jp4.Phi(), jp4.M())
          
          Leps = Leps_em if channel == 0 else Leps_mm
         
          if not ((j.jetId>>1)&1 and abs(j.eta)<4.7 and ((j.puId>>2)&1 or j.pt_nom > 50) and jp4.DeltaR(Leps[0]) > 0.4 and jp4.DeltaR(Leps[1]) > 0.4):  
            passJet30ID.append(0) 
            passDeepJet_L.append(0) 
            passDeepJet_M.append(0) 
            continue
          if j.pt_nom > 30:
            nJet30 += 1
            passJet30ID.append(1) 
          else:
            passJet30ID.append(0) 
          #if j.btagDeepB > self.btag_WP['deepcsv']["L"][self.era]:
          #  nbJet20_deepcsv_L += 1  
          #if j.btagDeepB > self.btag_WP['deepcsv']["M"][self.era]:
          #  nbJet20_deepcsv_M += 1  
          if j.pt_nom > 20 and j.btagDeepFlavB > self.btag_WP['deepjet']["L"][self.era] and abs(j.eta)<2.5:
            nbJet20_deepjet_L += 1  
            passDeepJet_L.append(1) 
          else:
            passDeepJet_L.append(0) 
          if j.pt_nom > 20 and j.btagDeepFlavB > self.btag_WP['deepjet']["M"][self.era] and abs(j.eta)<2.5:
            nbJet20_deepjet_M += 1  
            passDeepJet_M.append(1) 
          else:
            passDeepJet_M.append(0) 
        self.out.fillBranch("nJet30", nJet30)
        self.out.fillBranch("Jet_passJet30ID", passJet30ID)
        #self.out.fillBranch("nbJet20_deepcsv_L", nbJet20_deepcsv_L)
        #self.out.fillBranch("nbJet20_deepcsv_M", nbJet20_deepcsv_M)
        self.out.fillBranch("nbJet20_deepjet_L", nbJet20_deepjet_L)
        self.out.fillBranch("Jet_passDeepJet_L", passDeepJet_L)
        self.out.fillBranch("nbJet20_deepjet_M", nbJet20_deepjet_M)
        self.out.fillBranch("Jet_passDeepJet_M", passDeepJet_M)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

cleaning_2016preVFPUL = lambda: cleaning("2016UL")
cleaning_2016postVFPUL = lambda: cleaning("2016UL")
cleaning_2017UL = lambda: cleaning("2017UL")
cleaning_2018UL = lambda: cleaning("2018UL")

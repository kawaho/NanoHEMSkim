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
        # -1 should be rejected, 1 is mm, 0 is em
        self.out.branch("channel", "I")
        self.out.branch("nJet30", "I")
        self.out.branch("Jet_passJet30ID", "b", lenVar="nJet")
        self.out.branch("Jet_passDeepJet_L", "b", lenVar="nJet")
        self.out.branch("Jet_passDeepJet_M", "b", lenVar="nJet")
        self.out.branch("Jet_passDeepCSV_L", "b", lenVar="nJet")
        self.out.branch("Jet_passDeepCSV_M", "b", lenVar="nJet")

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
     
        Leps_em = []
        Leps_mm = []

        for e in Electrons:
          if (e.pt > 24 and abs(e.eta) < 2.5 and e.mvaFall17V2noIso_WP80 and e.convVeto and abs(e.dxy) < 0.045 and abs(e.dz) < 0.2 and e.pfRelIso03_all < 0.1):
            Leps_em.append(e.p4())
        nE=len(Leps_em)
        for m in Muons:
          if (m.pt > 15 and abs(m.eta) < 2.4 and m.tightId and abs(m.dxy) < 0.045 and abs(m.dz) < 0.2 and m.pfRelIso04_all < 0.15):
            Leps_mm.append(m.p4())
            if (m.pt > 24):
              Leps_em.append(m.p4())

        if nE==1 and not self.tauVeto(Leps_em, Taus) and not self.LepOverlap(Leps_em):
          channel = 0
        elif nE==0 and not self.tauVeto(Leps_mm, Taus) and not self.LepOverlap(Leps_mm):
          channel = 1
        else:
          channel = -1
       
        self.out.fillBranch("channel", channel)

        passJet30ID = []
        passDeepJet_L = []
        passDeepJet_M = []
        passDeepCSV_L = []
        passDeepCSV_M = []

        if channel!=-1:
          Leps = Leps_em if channel == 0 else Leps_mm
          for j in jets:
            jp4 = j.p4()
            jpt = j.pt_nom if self.runJEC else j.pt

            if ((j.jetId>>1)&1 and abs(j.eta)<4.7 and ((j.puId>>2)&1 or jpt > 50) and jp4.DeltaR(Leps[0]) > 0.4 and jp4.DeltaR(Leps[1]) > 0.4):
           
              if jpt > 30:
                passJet30ID.append(1) 
              else:
                passJet30ID.append(0) 

              if jpt > 20 and abs(j.eta)<2.5:
                if j.btagDeepFlavB > self.btag_WP['deepjet']["M"][self.era]:
                  passDeepJet_L.append(1) 
                  passDeepJet_M.append(1) 
                elif j.btagDeepFlavB > self.btag_WP['deepjet']["L"][self.era]:
                  passDeepJet_L.append(1) 
                  passDeepJet_M.append(0) 
                else:
                  passDeepJet_L.append(0) 
                  passDeepJet_M.append(0) 

                if j.btagDeepB > self.btag_WP['deepcsv']["M"][self.era]:
                  passDeepCSV_L.append(1) 
                  passDeepCSV_M.append(1) 
                elif j.btagDeepB > self.btag_WP['deepcsv']["L"][self.era]:
                  passDeepCSV_L.append(1) 
                  passDeepCSV_M.append(0) 
                else:
                  passDeepCSV_L.append(0) 
                  passDeepCSV_M.append(0) 
              else:
                passDeepJet_L.append(0) 
                passDeepJet_M.append(0) 
                passDeepCSV_L.append(0) 
                passDeepCSV_M.append(0) 
            else:
              passJet30ID.append(0) 
              passDeepJet_L.append(0) 
              passDeepJet_M.append(0) 
              passDeepCSV_L.append(0) 
              passDeepCSV_M.append(0) 

          self.out.fillBranch("nJet30", sum(passJet30ID))
          self.out.fillBranch("Jet_passJet30ID", passJet30ID)
          self.out.fillBranch("Jet_passDeepJet_L", passDeepJet_L)
          self.out.fillBranch("Jet_passDeepJet_M", passDeepJet_M)
          self.out.fillBranch("Jet_passDeepCSV_L", passDeepCSV_L)
          self.out.fillBranch("Jet_passDeepCSV_M", passDeepCSV_M)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

cleaning_2016preVFPUL = lambda: cleaning("2016UL")
cleaning_2016postVFPUL = lambda: cleaning("2016UL")
cleaning_2017UL = lambda: cleaning(era="2017UL")
cleaning_2018UL = lambda: cleaning("2018UL")

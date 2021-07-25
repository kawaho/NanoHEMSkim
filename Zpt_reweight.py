from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


class Zpt_reweight(Module):
    def __init__(self):
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("genZ_pt", "F")
        self.out.branch("genZ_M", "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        genPart = Collection(event, "GenPart")
        genZ_p4 = ROOT.TLorentzVector()
        for gen in genPart:
          if (abs(gen.pdgId) >=11 and abs(gen.pdgId) <=16 and (gen.statusFlags>>8)&1 and gen.status==1) or (gen.statusFlags>>9)&1:
            genZ_p4 += gen.p4()

        self.out.fillBranch("genZ_pt", genZ_p4.Pt())
        self.out.fillBranch("genZ_M", genZ_p4.M())

        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

Zpt_reweightUL = lambda: Zpt_reweight()

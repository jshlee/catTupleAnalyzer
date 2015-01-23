###
import ROOT
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.AutoLibraryLoader.enable()
from DataFormats.FWLite import Events, Handle
import os
import sys
from math import sqrt
from array import array
import time
import copy

ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
pi = ROOT.TMath.Pi()

def cal_del_eta(eta1, eta2):
  diff = eta2 - eta1
  eta1_sign = ROOT.TMath.Sign(1.0, eta1)
  return eta1_sign*diff

def cal_del_phi(phi1, phi2):
  diff = phi2 - phi1
  if(diff > pi):
    return diff - 2. * pi
  elif(diff < -pi):
    return diff + 2. * pi
  else:
    return diff

def cal_beta(eta1, phi1, eta2, phi2):
  del_eta = cal_del_eta(eta1, eta2)
  del_phi = cal_del_phi(phi1, phi2)
  del_r = sqrt(del_eta**2 + del_phi**2)
  beta = ROOT.TMath.ATan2(del_phi, del_eta)
  return [beta, del_eta, del_phi, del_r]

def cal_dr(jet1, jet2):
  de = cal_del_eta(jet1.Eta(), jet2.Eta())
  dp = cal_del_phi(jet1.Phi(), jet2.Phi())
  return sqrt(de**2 + dp**2)


in_f = sys.argv[1]
out_f = sys.argv[2]

out_root = ROOT.TFile(out_f,"RECREATE")
out_num_event = open(out_f[:-5]+"_num_of_events.txt","w")
in_put_num_event = 0

### ntuple booking
sys_e = ["pt", "eup", "edown", "es", "esup", "esdown"]
tr_l = []
br_c = ["beta", "del_eta", "del_phi", "del_r", "jet1_pt", "jet1_eta", "jet1_phi", "jet2_pt", "jet2_eta", "jet2_phi", "jet3_pt", "jet3_eta", "jet3_phi", "njet", "met", "nvtx", "npuvtx", "mc_w", "pu_w"]
br_l = []
for x in xrange(len(sys_e)):
  tr_l.append(copy.deepcopy(ROOT.TTree(sys_e[x]+"_beta", "color cohernece systematic errors : "+sys_e[x])))
  br_l.append([])
  for y in xrange(len(br_c)):
    br_l[x].append(array("d", [0.0]))
    tr_l[x].Branch(sys_e[x]+"_"+br_c[y], br_l[x][y], sys_e[x]+"_"+br_c[y]+"/D")
### ntuple booking end

root_l = []
root_fath = open(in_f)
for x in root_fath:
root_l.append(x[:-1])
print root_l


for rf in root_l:
  events = Events(rf)
  in_put_num_event += events.size()

  jetsLabel, jets = "catJets", Handle("std::vector<cat::Jet>")
  goodVTXLabel, GVTX = "goodOfflinePrimaryVertices", Handle("vector<reco::Vertex>")
  triggerPLabel, hlt_path = "patTrigger", Handle("vector<pat::TriggerPath>")
  metLabel, mets = "catMETs", Handle("vector<cat::MET>")

  genJetsLabel, genJets = "catGenJets", Handle("std::vector<cat::GenJet>")
  geninfoLabel, gen_info = "generator", Handle("GenEventInfoProduct")
  puvtxLabel, puvtx = "addPileupInfo", Handle("vector<PileupSummaryInfo>")

  for iev,event in enumerate(events):
    ### event cut
    event.getByLabel(jetsLabel,jets)
    try :
      jets.product() 
    except :
      continue
    event.getByLabel(goodVTXLabel, GVTX)
    goodvtx = GVTX.isValid()
    if not goodvtx:
      continue
           
    event.getByLabel(metLabel,mets)
    mets_ = mets.product().at(0).et()
    jet_l = []
    for i,g in enumerate(jets.product()):
      if g.LooseId() == 0:
        continue
      jet_l.append({'pt':g.pt(), 'eta':g.eta(), 'phi':g.phi(), 'eup':g.shiftedEnUp(), 'edown':g.shiftedEnDown(), 'es':g.smearedRes(), 'esup':g.smearedResUp(), 'esdown':g.smearedResDown()})
    if len(jet_l)<3:
      continue
    for x in xrange(len(sys_e)):      
      res_l = []
      sorted(jet_l, key = lambda l : l.get(sys_e[x]), reverse=True)
      beta_result = cal_beta(jet_l[1].get('eta'), jet_l[1].get('phi'), jet_l[2].get('eta'), jet_l[2].get('phi'))
      res_l.extend(beta_result)
      for ji in xrange(3):
        res_l.append(jet_l[ji].get(sys_e[x]))
        res_l.append(jet_l[ji].get('eta'))
        res_l.append(jet_l[ji].get('phi'))
     
      event.getByLabel(geninfoLabel, gen_info)
      gen_w = gen_info.product().weight()
      #event.getByLabel(genJetsLabel, genJets)
      event.getByLabel(puvtxLabel, puvtx)
      res_l.extend([len(jet_l), mets_, GVTX.product().size(), puvtx.product().at(0).getTrueNumInteractions(),  gen_w, 0.0])      
      for y in xrange(len(br_c)):
        br_l[x][y][0] = res_l[y]
      tr_l[x].Fill()

out_root.cd()
for t in tr_l:
  t.Write()


out_root.Write()
out_root.Close()


out_num_event.write("total input evnets : %d\n"%in_put_num_event)

out_num_event.close()



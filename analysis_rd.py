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
  return [abs(beta), del_eta, del_phi, del_r]

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
tr = ROOT.TTree("beta", "beta")
br_c = ["beta", "del_eta", "del_phi", "del_r", "raw_mass",  "jet1_pt", "jet1_eta", "jet1_phi", "jet2_pt", "jet2_eta", "jet2_phi", "jet3_pt", "jet3_eta", "jet3_phi", "njet", "met", "nvtx", "hlt80_pass", "hlt140_pass", "hlt320_pass", "hlt80_pre", "hlt140_pre", "hlt320_pre"]
br_l = []
for y in xrange(len(br_c)):
  br_l.append(array("d", [0.0]))
  tr.Branch(br_c[y], br_l[y], br_c[y]+"/D")
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

  hlt80passL, hlt80pass = ("recoEventInfo","HLTPFJet80"), Handle("bool")
  hlt140passL, hlt140pass = ("recoEventInfo","HLTPFJet140"), Handle("bool")
  hlt320passL, hlt320pass = ("recoEventInfo","HLTPFJet320"), Handle("bool")
  hlt80preL, hlt80pre = ("recoEventInfo","psHLTPFJet80"), Handle("int")
  hlt140preL, hlt140pre = ("recoEventInfo","psHLTPFJet140"), Handle("int")
  hlt320preL, hlt320pre = ("recoEventInfo","psHLTPFJet320"), Handle("int")

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

    jet_l = []
    for g in jets.product():
      if g.LooseId() == 0 or g.pt() < 30:
        continue
      jet_l.append(g)
    if len(jet_l)<3:
      continue

    res_l = []
    beta_result = cal_beta(jet_l[1].eta(), jet_l[1].phi(), jet_l[2].eta(), jet_l[2].phi())
    res_l.extend(beta_result)
    res_l.append((jet_l[0].p4() + jet_l[1].p4()).M())
    for ji in xrange(3):
      res_l.append(jet_l[ji].pt())
      res_l.append(jet_l[ji].eta())
      res_l.append(jet_l[ji].phi())
    event.getByLabel(metLabel, mets)
    mets_ = mets.product().at(0).et()
    res_l.extend([len(jet_l), mets_, GVTX.product().size()])
    event.getByLabel(hlt80passL, hlt80pass)
    event.getByLabel(hlt140passL, hlt140pass)
    event.getByLabel(hlt320passL, hlt320pass)
    if hlt80pass.product():
      res_l.append(1.0)
    else:
      res_l.append(0.0)
    if hlt140pass.product():
      res_l.append(1.0)
    else:
      res_l.append(0.0)
    if hlt320pass.product():
      res_l.append(1.0)
    else:
      res_l.append(0.0)
      print "hlt320 f"
    event.getByLabel(hlt80preL, hlt80pre)
    event.getByLabel(hlt140preL, hlt140pre)
    event.getByLabel(hlt320preL, hlt320pre)
    res_l.extend([hlt80pre.product()[0], hlt140pre.product()[0], hlt320pre.product()[0]])
    for y in xrange(len(br_c)):
      br_l[y][0] = res_l[y]
    tr.Fill()


out_root.Write()
out_root.Close()


out_num_event.write("total input evnets : %d\n"%in_put_num_event)

out_num_event.close()



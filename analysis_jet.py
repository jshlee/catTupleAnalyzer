###
import ROOT
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.AutoLibraryLoader.enable()
from DataFormats.FWLite import Events, Handle
import os, gc
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

in_type = sys.argv[1]
in_f = sys.argv[2]
out_f = sys.argv[3]

mc = True
if not in_type == 'mc':
  mc = False

out_root = ROOT.TFile(out_f,"RECREATE")
out_num_event = open(out_f[:-5]+"_num_of_events.txt","w")

in_put_num_event = 0
cut_is_jet = 0
cut_is_gvtx = 0
cut_h = 0
cut_m = 0
cut_l = 0

cut_h_w = 0
cut_m_w = 0
cut_l_w = 0

### ntuple booking

h_h_njet = ROOT.TH1F("hnjet", "hnjet",50,0,50)
h_h_njet.Sumw2()
h_h_jet1_pt = ROOT.TH1F("hjet1pt", "hjet1p",30,500,2500)
h_h_jet1_pt.Sumw2()
h_h_hlt = ROOT.TH1F("hlt","hlt",10,0,10)
h_h_hlt.Sumw2()

h_m_njet = ROOT.TH1F("mjet", "mnjet",50,0,50)
h_m_njet.Sumw2()
h_m_jet1_pt = ROOT.TH1F("mjet1pt", "mjet1p",30,220,507)
h_m_jet1_pt.Sumw2()

h_l_njet = ROOT.TH1F("lnjet", "lnjet",50,0,50)
h_l_njet.Sumw2()
h_l_jet1_pt = ROOT.TH1F("ljet1pt", "ljet1p",30,74,220)
h_l_jet1_pt.Sumw2()

### ntuple booking end

root_l = []
root_fath = open(in_f)
for x in root_fath:
  root_l.append(x[:-1])
#print root_l

for rf in root_l:
  events = Events(rf)
  in_put_num_event += events.size()

  jetsLabel, jets = "catJets", Handle("std::vector<cat::Jet>")
  goodVTXLabel, GVTX = "goodOfflinePrimaryVertices", Handle("vector<reco::Vertex>")
  triggerPLabel, hlt_path = "patTrigger", Handle("vector<pat::TriggerPath>")

  hlt80preL, hlt80pre = ("recoEventInfo","HLTPFJet80", "CAT"), Handle("int")
  hlt140preL, hlt140pre = ("recoEventInfo","HLTPFJet140","CAT"), Handle("int")
  hlt320preL, hlt320pre = ("recoEventInfo","HLTPFJet320", "CAT"), Handle("int")
  if mc:
    gen_wL, gen_w = ("recoEventInfo", "generatorWeight", "CAT"), Handle("double")


 
  for iev,event in enumerate(events):
    ### event cut
    if not event.getByLabel(jetsLabel,jets): continue
    cut_is_jet += 1

    event.getByLabel(goodVTXLabel, GVTX)
    goodvtx = GVTX.isValid()
    if not goodvtx: continue
    cut_is_gvtx += 1

    event.getByLabel(hlt80preL, hlt80pre)
    event.getByLabel(hlt140preL, hlt140pre)
    event.getByLabel(hlt320preL, hlt320pre)

    if mc:
      event.getByLabel(gen_wL, gen_w)
    
    jet_l = []
    for i,g in enumerate(jets.product()):
      if g.LooseId() == 0 or g.pileupJetId() < 0.9 or abs(g.eta()) > 2.5 or g.pt() < 30.0:
        continue
      jet_l.append(g)
      if hlt320pre.product()[0] > 0 and jet_l[0].pt() > 507 and jet_l[0].pt() < 2500:
        h_h_njet.Fill(len(jet_l))
        if mc:
          h_h_jet1_pt.Fill(jet_l[0].pt(), gen_w.product()[0])
        else:
          h_h_jet1_pt.Fill(jet_l[0].pt())
        h_h_hlt.Fill(hlt320pre.product()[0])
        cut_h += 1 
	#cut_h_w += hlt320pre.product()[0]
	cut_h_w += gen_w.product()[0]
      if hlt140pre.product()[0] > 0 and jet_l[0].pt() > 220 and jet_l[0].pt() < 507:
        h_m_njet.Fill(len(jet_l))
        if mc:
          h_m_jet1_pt.Fill(jet_l[0].pt(), gen_w.product()[0])
        else:
          h_m_jet1_pt.Fill(jet_l[0].pt())
        cut_m += 1 
        #cut_m_w += hlt140pre.product()[0]
	cut_m_w += gen_w.product()[0]
      if hlt80pre.product()[0] > 0 and jet_l[0].pt() > 74 and jet_l[0].pt() < 220:
        h_l_njet.Fill(len(jet_l))
        if mc:
          h_l_jet1_pt.Fill(jet_l[0].pt(), gen_w.product()[0])
        else:
          h_l_jet1_pt.Fill(jet_l[0].pt())
        cut_l += 1 
        #cut_l_w += hlt80pre.product()[0]
	cut_l_w += gen_w.product()[0]
  gc.collect()


out_root.Write()
out_root.Close()


out_num_event.write("total input evnets : %d\n"%in_put_num_event)
out_num_event.write("total cut_is_jet evnets : %d\n"%cut_is_jet)
out_num_event.write("total cut_is_gvtx evnets : %d\n"%cut_is_gvtx)
out_num_event.write("total h_pt evnets : %d\n"%cut_h)
out_num_event.write("total m_pt evnets : %d\n"%cut_m)
out_num_event.write("total l_pt evnets : %d\n"%cut_l)
out_num_event.write("total h_pt_w evnets : %d\n"%cut_h_w)
out_num_event.write("total m_pt_w evnets : %d\n"%cut_m_w)
out_num_event.write("total l_pt_w evnets : %d\n"%cut_l_w)


out_num_event.close()



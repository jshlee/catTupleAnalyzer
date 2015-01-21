## to setup cmsenv
## export CMSREL=CMSSW_5_3_20;cmsrel $CMSREL;cd $CMSREL/src;cmsenv
## to use once cmsenv is set up
## export CMSREL=CMSSW_5_3_20;cd $CMSREL/src;cmsenv;cd $OLDPWD;echo $SRT_CMSSW_BASE_SCRAMRTDEL
import ROOT
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.AutoLibraryLoader.enable()
from DataFormats.FWLite import Events, Handle
import os
import sys
from math import sqrt
import numpy as n

ROOT.gROOT.Reset()
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

type_tag = sys.argv[1]
if type_tag == "mc":
  mc = True
else:
  mc = False

in_f = sys.argv[2]
out_f = sys.argv[3]

out_root = ROOT.TFile(out_f,"RECREATE")
out_num_event = open(out_f[:-5]+"_num_of_events.txt","w")
in_put_num_event = 0
select_d = 0
select_cc = 0
### ntuple booking

out_tr = ROOT.TTree("beta", "color coherence")
br_beta = n.zeros(1, dtype=float)
br_del_eta = n.zeros(1, dtype=float)
br_del_phi = n.zeros(1, dtype=float)
br_del_r = n.zeros(1, dtype=float)
br_raw_mass = n.zeros(1, dtype=float)

br_jet1_pt = n.zeros(1, dtype=float) 
br_jet2_pt = n.zeros(1, dtype=float)
br_jet3_pt = n.zeros(1, dtype=float)
br_jet1_eta = n.zeros(1, dtype=float)
br_jet2_eta = n.zeros(1, dtype=float)
br_jet3_eta = n.zeros(1, dtype=float)
br_jet1_phi = n.zeros(1, dtype=float)
br_jet2_phi = n.zeros(1, dtype=float)
br_jet3_phi = n.zeros(1, dtype=float)

br_njet = n.zeros(1, dtype=float)
br_met = n.zeros(1, dtype=float)
br_nvtx = n.zeros(1, dtype=float)
br_hlt_pass = n.zeros(1, dtype=float)
br_hlt_pre = n.zeros(1, dtype=float)

br_a = [br_beta, br_del_eta, br_del_phi, br_del_r, br_raw_mass, br_jet1_pt, br_jet2_pt, br_jet3_pt, br_jet1_eta, br_jet2_eta, br_jet3_eta, br_jet1_phi, br_jet2_phi, br_jet3_phi,br_njet, br_met, br_nvtx, br_hlt_pass, br_hlt_pre]
br_b = ["beta", "del_eta", "del_phi", "del_r", "raw_mass", "jet1_pt", "jet2_pt", "jet3_pt", "jet1_eta", "jet2_eta", "jet3_eta", "jet1_phi", "jet2_phi", "jet3_phi", "njet", "met", "nvtx", "hlt_pass", "hlt_pre"]

if mc:
  br_puvtx = n.zeros(1, dtype=float)
  br_mc_w = n.zeros(1, dtype=float)
  gen_beta = n.zeros(1, dtype=float)
  gen_del_eta = n.zeros(1, dtype=float)
  gen_del_phi = n.zeros(1, dtype=float)
  gen_del_r = n.zeros(1, dtype=float)
  gen_jet1_pt = n.zeros(1, dtype=float)
  gen_jet2_pt = n.zeros(1, dtype=float)
  gen_jet3_pt = n.zeros(1, dtype=float)
  gen_jet1_eta = n.zeros(1, dtype=float)
  gen_jet2_eta = n.zeros(1, dtype=float)
  gen_jet3_eta = n.zeros(1, dtype=float)
  gen_jet1_phi = n.zeros(1, dtype=float)
  gen_jet2_phi = n.zeros(1, dtype=float)
  gen_jet3_phi = n.zeros(1, dtype=float)
  br_a.extend([br_puvtx, br_mc_w, gen_beta, gen_del_eta, gen_del_phi, gen_del_r, gen_jet1_pt, gen_jet2_pt, gen_jet3_pt, gen_jet1_eta, gen_jet2_eta, gen_jet3_eta, gen_jet1_phi, gen_jet2_phi, gen_jet3_phi])
  br_b.extend(["puvtx", "mc_w", "gen_beta", "gen_del_eta", "gen_del_phi", "gen_del_r", "gen_jet1_pt", "gen_jet2_pt", "gen_jet3_pt", "gen_jet1_eta", "gen_jet2_eta", "gen_jet3_eta", "gen_jet1_phi", "gen_jet2_phi", "gen_jet3_phi"])

for x in xrange(len(br_a)):
  print br_b[x]
  out_tr.Branch(br_b[x], br_a[x], br_b[x]+"/D")

### ntuple booking end

hlt_n = ["HLT_PFJet40_","HLT_PFJet80_","HLT_PFJet140_","HLT_PFJet200_","HLT_PFJet260_","HLT_PFJet320_"]

root_l = []
root_fath = open(in_f)
for x in root_fath:
  root_l.append(x[:-1])
print root_l


for rf in root_l:
  print "open : "+rf
  events = Events(rf)
  in_put_num_event += events.size()

  jetsLabel, jets = "catJets", Handle("std::vector<cat::Jet>")
  goodVTXLabel, GVTX = "goodOfflinePrimaryVertices", Handle("vector<reco::Vertex>")
  triggerPLabel, hlt_path = "patTrigger", Handle("vector<pat::TriggerPath>")
  metLabel, mets = "catMETs", Handle("vector<cat::MET>")

  if mc:
    genJetsLabel, genJets = "catGenJets", Handle("std::vector<cat::GenJet>")
    geninfoLabel, gen_info = "generator", Handle("GenEventInfoProduct")
    puvtxLabel, puvtx = "addPileupInfo", Handle("vector<PileupSummaryInfo>")

  jet_cc = 0
  for iev,event in enumerate(events):
    event.getByLabel(goodVTXLabel, GVTX)
    goodvtx = GVTX.isValid()
    if not goodvtx:
      continue

    event.getByLabel(triggerPLabel, hlt_path)
    hlt_p = hlt_path.product()
    hlt_pass = []
    hlt_pre = []
    for i, hlt in enumerate(hlt_p):
      for j, n in enumerate(hlt_n):
        if hlt.name().startswith(n):
          hlt_pass.append(hlt.wasAccept())
          hlt_pre.append(hlt.prescale())
           
    event.getByLabel(metLabel,mets)
    mets_ = mets.product().at(0).et()
    event.getByLabel(jetsLabel,jets)
    jet_l = []
    for i,g in enumerate(jets.product()):
      if g.pt()<30 or g.LooseId() == 0:
        continue
      jet_l.append(g.p4())
       
    if len(jet_l)<3:
      continue
    for xh in [5,4,3,2,1,0]:
      if hlt_pass[xh] == 1:
        br_hlt_pass[0] = hlt_pass[xh]
        br_hlt_pre[0] = hlt_pre[xh]
        break
    hlt_pass.sort()
    if hlt_pass[-1] == 0:
      br_hlt_pass[0] = -10.0
      br_hlt_pre[0] = -10.0
    beta_result = cal_beta(jet_l[1].Eta(), jet_l[1].Phi(), jet_l[2].Eta(), jet_l[2].Phi())
    r_mass = (jet_l[0] + jet_l[1]).M()

    br_beta[0] = abs(beta_result[0])
    br_del_eta[0] = beta_result[1]
    br_del_phi[0] = beta_result[2]
    br_del_r[0] = beta_result[3]
    br_raw_mass[0] = r_mass
    br_jet1_pt[0] = jet_l[0].Pt()
    br_jet2_pt[0] = jet_l[1].Pt()
    br_jet3_pt[0] = jet_l[2].Pt()
    br_jet1_eta[0] = jet_l[0].Eta()
    br_jet2_eta[0] = jet_l[1].Eta()
    br_jet3_eta[0] = jet_l[2].Eta()
    br_jet1_phi[0] = jet_l[0].Phi()
    br_jet2_phi[0] = jet_l[1].Phi()
    br_jet3_phi[0] = jet_l[2].Phi()
      
    br_njet[0] = len(jet_l)
    br_met[0] = mets_
    br_nvtx[0] = GVTX.product().size()
    #br_hlt_pass[0] = hlt_pass
    #br_hlt_pre[0] = hlt_pre
    if mc:
      event.getByLabel(geninfoLabel, gen_info)
      gen_w = gen_info.product().weight()
      event.getByLabel(genJetsLabel, genJets)
      event.getByLabel(puvtxLabel, puvtx)
      br_puvtx[0] = puvtx.product().at(0).getTrueNumInteractions()
      br_mc_w[0] = gen_w
      
      genjet_l = []
      for  g in genJets.product():
        if g.pt() < 30:
          continue
        genjet_l.append(g.p4())
      if len(genjet_l) > 2:
        mjet = []
        for jet_index in xrange(3):
          for g_jet in genjet_l:
            dr = cal_dr(jet_l[jet_index], g_jet)
            if dr < 0.5:
              mjet.append(g_jet)
              genjet_l.remove(g_jet)
              break
        if len(mjet) == 3:
          gbeta_res = cal_beta(mjet[1].Eta(),mjet[1].Phi(),mjet[2].Eta(),mjet[2].Phi())
          gen_beta[0] = abs(gbeta_res[0])
          gen_del_eta[0] = gbeta_res[1]
          gen_del_phi[0] = gbeta_res[2]
          gen_del_r[0] = gbeta_res[3]
          gen_jet1_pt[0] = mjet[0].Pt()
          gen_jet2_pt[0] = mjet[1].Pt()
          gen_jet3_pt[0] = mjet[2].Pt()
          gen_jet1_eta[0] = mjet[0].Eta()
          gen_jet2_eta[0] = mjet[1].Eta()
          gen_jet3_eta[0] = mjet[2].Eta()
          gen_jet1_phi[0] = mjet[0].Phi()     
          gen_jet2_phi[0] = mjet[1].Phi()     
          gen_jet3_phi[0] = mjet[2].Phi()     
        else:
          gen_beta[0] = -10.0
          gen_del_eta[0] = -10.0
          gen_del_phi[0] = -10.0
          gen_del_r[0] = -10.0
          gen_jet1_pt[0] = -10.0
          gen_jet2_pt[0] = -10.0
          gen_jet3_pt[0] = -10.0
          gen_jet1_eta[0] = -10.0
          gen_jet2_eta[0] = -10.0
          gen_jet3_eta[0] = -10.0
          gen_jet1_phi[0] = -10.0
          gen_jet2_phi[0] = -10.0
          gen_jet3_phi[0] = -10.0
    out_tr.Fill()

out_root.Write()
out_root.Close()


out_num_event.write("total input evnets : %d\n"%in_put_num_event)
out_num_event.write("total selected evnets : %d\n"%select_d)
out_num_event.write("total selected color coherence events : %d"%select_cc)

out_num_event.close()



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

### ntuple booking
if mc:
    sys_e = ["pt", "eup", "edown", "es", "esup", "esdown"]
else:
    sys_e = ["pt"]    
tr_l = []
if mc:
    br_c = ["beta", "del_eta", "del_phi", "del_r", "raw_mass", "gen_beta", "jet1_pt", "jet1_eta", "jet1_phi", "jet2_pt", "jet2_eta", "jet2_phi", "jet3_pt", "jet3_eta", "jet3_phi", "jet1_d_pt", "jet1_d_eta", "jet1_d_phi", "gen_jet1_pt", "gen_jet1_eta", "gen_jet1_phi", "jet2_d_pt", "jet2_d_eta", "jet2_d_phi", "gen_jet2_pt", "gen_jet2_eta", "gen_jet2_phi", "jet3_d_pt", "jet3_d_eta", "jet3_d_phi", "gen_jet3_pt", "gen_jet3_eta", "gen_jet3_phi", "njet", "met", "nvtx", "pu_w", "pu_w_up", "pu_w_down", "pdf_w_q", "pdf_w_x1", "pdf_w_x2", "pdf_w_id1", "pdf_w_id2"]
else:
    br_c = ["beta", "del_eta", "del_phi", "del_r", "raw_mass", "jet1_pt", "jet1_eta", "jet1_phi", "jet2_pt", "jet2_eta", "jet2_phi", "jet3_pt", "jet3_eta", "jet3_phi", "njet", "met", "nvtx", "hlt80_pass", "hlt80_pre", "hlt140_pass", "hlt140_pre", "hlt320_pass", "hlt320_pre"]
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

  if mc:
    puvtxLabel, puvtx = "addPileupInfo", Handle("vector<PileupSummaryInfo>")
    puwLabel, puw = ("pileupWeight", ""), Handle("double")
    puwupLabel, puwup = ("pileupWeight", "up"), Handle("double")
    puwdownLabel, puwdown = ("pileupWeight", "dn"), Handle("double")
    pdfwqLabel, pdfwq = ("pdfWeight", "Q"), Handle("double")
    pdfwx1Label, pdfwx1 = ("pdfWeight", "x1"), Handle("double")
    pdfwx2Label, pdfwx2 = ("pdfWeight", "x2"), Handle("double")
    pdfwid1Label, pdfwid1 = ("pdfWeight", "id1"), Handle("int")
    pdfwid2Label, pdfwid2 = ("pdfWeight", "id2"), Handle("int")
  else:
    hlt80preL, hlt80pre = ("recoEventInfo","HLTPFJet80", "CAT"), Handle("int")
    hlt140preL, hlt140pre = ("recoEventInfo","HLTPFJet140","CAT"), Handle("int")
    hlt320preL, hlt320pre = ("recoEventInfo","HLTPFJet320", "CAT"), Handle("int")
        
  for iev,event in enumerate(events):
    ### event cut
    if not event.getByLabel(jetsLabel,jets): continue
    event.getByLabel(goodVTXLabel, GVTX)
    goodvtx = GVTX.isValid()
    if not goodvtx:
      continue
    event.getByLabel(metLabel, mets)
    mets_ = mets.product().at(0).et()
    if mc:
      event.getByLabel(puwLabel, puw)
      event.getByLabel(metLabel, mets)
      event.getByLabel(puwLabel, puw)
      event.getByLabel(puwupLabel, puwup)
      event.getByLabel(puwdownLabel, puwdown)
      event.getByLabel(pdfwqLabel, pdfwq)
      event.getByLabel(pdfwx1Label, pdfwx1)
      event.getByLabel(pdfwx2Label, pdfwx2)
      event.getByLabel(pdfwid1Label, pdfwid1)
      event.getByLabel(pdfwid2Label, pdfwid2)
    else:
      event.getByLabel(hlt80preL, hlt80pre)
      event.getByLabel(hlt140preL, hlt140pre)
      event.getByLabel(hlt320preL, hlt320pre)
    """
    if not mets.isValid():
      print "F"
      mets_ = -10.0
    else:
      mets_ = mets.product().at(0).et()
    """
    jet_l = []
    for i,g in enumerate(jets.product()):
      if g.LooseId() == 0 or g.pileupJetId() < 0.9 or g.pt() < 30:
        continue
      if mc:
        jet_l.append({'pt':g.pt(), 'eup':g.shiftedEnUp()*g.pt(), 'edown':g.shiftedEnDown()*g.pt(), 'es':g.smearedRes()*g.pt(), 'esup':g.smearedResUp()*g.pt(), 'esdown':g.smearedResDown()*g.pt(), 'jet':g})
      else:
        jet_l.append({'pt':g.pt(),'jet':g})
    if len(jet_l)<3:
      continue
    for x in xrange(len(sys_e)):      
      res_l = []
      sorted(jet_l, key = lambda l : l.get(sys_e[x]), reverse=True)
      beta_result = cal_beta(jet_l[1].get('jet').eta(), jet_l[1].get('jet').phi(), jet_l[2].get('jet').eta(), jet_l[2].get('jet').phi())
      res_l.extend(beta_result)
      res_l.append((jet_l[0].get('jet').p4()*(jet_l[0].get(sys_e[x])/jet_l[0].get('pt')) + jet_l[1].get('jet').p4()*(jet_l[1].get(sys_e[x])/jet_l[1].get('pt'))).M())
      jet_c_l = []
      gjet_c = 0
      for ji in xrange(3):
        jet_c_l.append(jet_l[ji].get(sys_e[x]))
        jet_c_l.append(jet_l[ji].get('jet').eta())
        jet_c_l.append(jet_l[ji].get('jet').phi())
      if mc:
        for ji in xrange(3):  
          if jet_l[ji].get('jet').genJet():
            gjet_c += 1
            jet_c_l.append(jet_l[ji].get(sys_e[x])/jet_l[ji].get('jet').genJet().pt())
            jet_c_l.append(jet_l[ji].get('jet').eta()-jet_l[ji].get('jet').genJet().eta())
            jet_c_l.append(cal_del_phi(jet_l[ji].get('jet').phi(), jet_l[ji].get('jet').genJet().phi()))
            jet_c_l.append(jet_l[ji].get('jet').genJet().pt())
            jet_c_l.append(jet_l[ji].get('jet').genJet().eta())
            jet_c_l.append(jet_l[ji].get('jet').genJet().phi())
          else:
            jet_c_l.extend([-10.0, -10.0, -10.0, -10.0, -10.0, -10.0])      
        if gjet_c == 3:
          res_l.append(cal_beta(jet_l[1].get('jet').eta(), jet_l[1].get('jet').phi(), jet_l[2].get('jet').eta(), jet_l[2].get('jet').phi())[0])
        else:
          res_l.append(-10.0)
      res_l.extend(jet_c_l) 

      
      #event.getByLabel(geninfoLabel, gen_info)
      #event.getByLabel(genJetsLabel, genJets)
      #event.getByLabel(puvtxLabel, puvtx)
      res_l.extend([len(jet_l), mets_, GVTX.product().size()])   
      if mc:
        res_l.extend([puw.product()[0], puwup.product()[0], puwdown.product()[0]])
        res_l.extend([pdfwq.product()[0], pdfwx1.product()[0], pdfwx2.product()[0], pdfwid1.product()[0], pdfwid2.product()[0]])
      if not mc:
        hlt80pass = 0
        hlt140pass = 0
        hlt320pass = 0
        if not hlt80pre.product()[0] == 0:
          hlt80pass = 1
        if not hlt140pre.product()[0] == 0:
          hlt140pass = 1
        if not hlt320pre.product()[0] == 0:
          hlt320pass = 1
        res_l.extend([hlt80pass, hlt80pre.product()[0], hlt140pass, hlt140pre.product()[0], hlt320pass, hlt320pre.product()[0]])

      for y in xrange(len(br_c)):
        br_l[x][y][0] = res_l[y]
      tr_l[x].Fill()
  gc.collect()
out_root.cd()
for t in tr_l:
  t.Write()


out_root.Write()
out_root.Close()


out_num_event.write("total input evnets : %d\n"%in_put_num_event)

out_num_event.close()



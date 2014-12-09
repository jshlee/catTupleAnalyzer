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

def add_hist(name, title, bin, x_min, x_max):
  tmp_h = ROOT.TH1F(name, title, bin, x_min, x_max)
  tmp_h.Sumw2()
  return tmp_h

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


eta_bin = ["low_eta","high_eta"]

pt_bin = ["low_pt","medium_pt","high_pt"]
j_c = ["pt", "eta", "phi"]
j_bin = [[[30,0,250],[30,0,550],[30,0,2500]], [[30, -3, 3]]*3, [[30, -pi, pi]]*3]

beta_c = ["beta", "del_eta", "del_phi", "del_r23", "raw_mass"]
beta_bin = [[18, 0, pi], [30, -3, 3], [30, -3, 3], [30, 0, 3], [50, 0, 5000]]
if mc:
  event_c = ["weight", "met", "pvtx","puvtx"]
  event_bin = [[200, 0, 2],[100, 0, 1000], [100, 0, 100], [100, 0, 100]]
else:
  event_c = ["weight", "met", "pvtx"]
  event_bin = [[200, 0, 2],[100, 0, 1000], [100, 0, 100]]

event_l = []
jet_l = []
beta_l = [] 
jet_cc_l = []
hlt_h = []

hlt_n = ["HLT_PFJet40_","HLT_PFJet80_","HLT_PFJet140_","HLT_PFJet200_","HLT_PFJet260_","HLT_PFJet320_"]

for x in hlt_n:
  hlt_h.append(add_hist(x+"h",x[:-1],100,0,2500))

for i, x in enumerate(pt_bin):
  tmp_event_c = []
  for bin, e_c in enumerate(event_c):
    tmp_event_c.append(add_hist(x+"_"+e_c, x+"_"+e_c, event_bin[bin][0], event_bin[bin][1], event_bin[bin][2]))
  event_l.append(tmp_event_c)
  tmp_jet_index = []
  for jet_index in xrange(1,4):
    tmp_jet_c = []
    for bin, j in enumerate(j_c):
      tmp_jet_c.append(add_hist(x+"_jet_%d_%s"%(jet_index,j), x+"_jet_%d_%s"%(jet_index,j), j_bin[bin][i][0], j_bin[bin][i][1], j_bin[bin][i][2]))
    tmp_jet_index.append(tmp_jet_c)
  jet_l.append(tmp_jet_index)
  tmp_beta_eta_bin = []
  tmp_jet_eta_bin = []
  for eta_c in eta_bin:
    tmp_beta_c = []
    for bin, b_c in enumerate(beta_c):
      tmp_beta_c.append(add_hist(x+"_"+eta_c+"_"+b_c, x+"_"+eta_c+"_"+b_c, beta_bin[bin][0], beta_bin[bin][1], beta_bin[bin][2]))
    tmp_beta_eta_bin.append(tmp_beta_c)
    tmp_jet_index = []
    for jet_index in xrange(1,4):
      tmp_jet_c = []
      for bin, j in enumerate(j_c):
        tmp_jet_c.append(add_hist(x+"_"+eta_c+"_jet_%d_%s"%(jet_index,j), x+"_"+eta_c+"_jet_%d_%s"%(jet_index,j), j_bin[bin][i][0], j_bin[bin][i][1], j_bin[bin][i][2]))
      tmp_jet_index.append(tmp_jet_c)
    tmp_jet_eta_bin.append(tmp_jet_index)
  beta_l.append(tmp_beta_eta_bin)
  jet_cc_l.append(tmp_jet_eta_bin)

h_jet1_pt = add_hist("jet1 pt", "jet1 pt", 100, 0, 2500)

hist_l = []
hist_l.append(h_jet1_pt)
hist_l.append(hlt_h)
hist_l.append(event_l)
hist_l.append(jet_l)
hist_l.append(beta_l)
hist_l.append(jet_cc_l)


if mc:
  unfold_l = []
  for x in pt_bin:
    tmp_eta_bin = []
    for y in eta_bin:
      tmp_eta_bin.append(ROOT.TH2D(x+"_"+y+"_beta_unfold",x+"_"+y+"_beta_unfold",18,0,pi,18,0,pi))
    unfold_l.append(tmp_eta_bin)
  ROOT.gSystem.Load("/pnfs/user/hyunyong/RooUnfold-1.1.1/libRooUnfold")
  roounfold_res = []
  for x in pt_bin:
    tmp_eta_bin = []
    for y in eta_bin:
      tmp_eta_bin.append(ROOT.RooUnfoldResponse(18, 0, pi, x+"_"+y+"_beta_rooulfold", x+"_"+y+"_beta_rooulfold"))
    roounfold_res.append(tmp_eta_bin)

      
#hist_l[0] = jet1_pt for hlt
#hist_l[1] = hlt_h[hlt]
#hist_l[2] = event_l[l,m,h][weight, met, pvtx]
#hist_l[3] = jet_l[l,m,h][jet 1, 2, 3][pt, eta, phi]
#hist_l[4] = beta_l[l,m,h][low eta, high eta][beta, del eta, del phi, del r23, raw mass]
#hist_l[5] = jet_cc_l[l,m,h][low eta, high eta][jet 1, 2, 3][pt, eta, phi]



root_l = []
root_fath = open(in_f)
for x in root_fath:
  root_l.append(x[:-1])
print root_l


for rf in root_l:
  print "open : "+rf
  events = Events(rf)
  in_put_num_event += events.size()
  if mc:
    genJetsLabel, genJets = "catGenJets", Handle("std::vector<cat::GenJet>")
    geninfoLabel, gen_info = "generator", Handle("GenEventInfoProduct")
    puvtxLabel, puvtx = "addPileupInfo", Handle("vector<PileupSummaryInfo>")
  jetsLabel, jets = "catJets", Handle("std::vector<cat::Jet>")
  goodVTXLabel, GVTX = "goodOfflinePrimaryVertices", Handle("vector<reco::Vertex>")
  triggerPLabel, hlt_path = "patTrigger", Handle("vector<pat::TriggerPath>")
  metLabel, mets = "catMETs", Handle("vector<cat::MET>")

  wrong_sort = 0
  jet_cc = 0
  for iev,event in enumerate(events):
    if mc:
      event.getByLabel(geninfoLabel, gen_info)
      gen_w = gen_info.product().weight()
      event.getByLabel(genJetsLabel, genJets)
    else:
      gen_w = 1.0
 
    event.getByLabel(triggerPLabel, hlt_path)
    hlt_p = hlt_path.product() 
    hltpass = []
    for i, hlt in enumerate(hlt_p):
      for j, n in enumerate(hlt_n):
        if hlt.name().startswith(n):
          hltpass.append(hlt.wasAccept())
    
    #if not hltpass:
    #  continue
    #print "Good VTX collection"
    event.getByLabel(goodVTXLabel, GVTX)
    goodvtx = GVTX.isValid()
    if mc:
      event.getByLabel(puvtxLabel, puvtx)
    if not goodvtx:
      continue

    event.getByLabel(metLabel,mets)
    mets_ = mets.product().at(0).et()
    #print "jet collection"

    event.getByLabel(jetsLabel,jets)
    jet_list = [] 
    if jets.product().size()<1:
      continue
    jet_l = []
    for i,g in enumerate(jets.product()):
      if g.pt()<30 or g.LooseId() == 0:
        continue
      jet_l.append(g.p4())
       
        
    if len(jet_l)>2:
      cut_pass = 0
      beta_res = cal_beta(jet_l[1].Eta(),jet_l[1].Phi(),jet_l[2].Eta(),jet_l[2].Phi())
      if beta_res[3] > 0.5 and beta_res[3] < 1.5 and abs(jet_l[1].Eta()) < 2.5 and abs(jet_l[0].Eta()) < 2.5:
        r_mass = (jet_l[0]+jet_l[1]).M()
        beta_res.append(r_mass)
        if r_mass > 220.0:
          cut_pass = 1


      hist_l[0].Fill(jet_l[0].Pt(), gen_w)
      for j, hlt_p in enumerate(hltpass):
        if hlt_p:
          hist_l[1][j].Fill(jet_l[0].Pt(), gen_w)

      pt_bin_i = -1
      eta_bin_i = -1
      cut_pt = 0 
      if jet_l[0].Pt()>74 and jet_l[0].Pt()<220 and hltpass[1]:
        pt_bin_i = 0
        cut_pt =1
      if jet_l[0].Pt()>220 and jet_l[0].Pt()<507 and hltpass[2]:
        pt_bin_i = 1
        cut_pt = 1
      if jet_l[0].Pt()>507 and jet_l[0].Pt()<2500 and hltpass[5]:
        pt_bin_i = 2
        cut_pt = 1
      if abs(jet_l[1].Eta()) < 0.8:
        eta_bin_i = 0
      else:
        eta_bin_i = 1

      if cut_pt ==1:
        select_d += 1
        if mc:
          event_v = [gen_w, mets_, GVTX.product().size(), puvtx.product().at(0).getTrueNumInteractions()]
        else:
          event_v = [gen_w, mets_, GVTX.product().size()]
        jet_input = []
        for jet_index in  xrange(3):
          tmp = [jet_l[jet_index].Pt(), jet_l[jet_index].Eta(), jet_l[jet_index].Phi()] 
          jet_input.append(tmp)
         
        for h in xrange(len(event_v)):
          if h==0:
            hist_l[2][pt_bin_i][h].Fill(event_v[h],1.0)
          else:
            hist_l[2][pt_bin_i][h].Fill(event_v[h], gen_w)
        for jet_index in xrange(3):
          for jet_c in xrange(3):
            hist_l[3][pt_bin_i][jet_index][jet_c].Fill(jet_input[jet_index][jet_c], gen_w)
      if cut_pass == 1 and cut_pt == 1:
        select_cc += 1
        for beta_index in xrange(len(beta_res)):
          hist_l[4][pt_bin_i][eta_bin_i][beta_index].Fill(beta_res[beta_index], gen_w)
        for jet_index in xrange(3):
          for jet_c in xrange(3):
            hist_l[5][pt_bin_i][eta_bin_i][jet_index][jet_c].Fill(jet_input[jet_index][jet_c], gen_w)
        if mc:
          genjet_l = []
          for  g in genJets.product():
            genjet_l.append(g.p4())
          if len(genjet_l) > 2:
            mget = []
            for jet_index in xrange(3):
              dr = cal_dr(jet_l[jet_index], genjet_l[jet_index])
              if dr < 0.5:
                mget.append(genjet_l[jet_index])
            if len(mget) == 3:
              gbeta_res = cal_beta(genjet_l[1].Eta(),genjet_l[1].Phi(),genjet_l[2].Eta(),genjet_l[2].Phi())
              unfold_l[pt_bin_i][eta_bin_i].Fill(beta_res[0],gbeta_res[0])
              roounfold_res[pt_bin_i][eta_bin_i].Fill(beta_res[0],gbeta_res[0])


out_root.cd()
for x in xrange(3):
  for y in xrange(2):
    roounfold_res[x][y].Write()   
out_root.Write()
out_root.Close()


out_num_event.write("total input evnets : %d\n"%in_put_num_event)
out_num_event.write("total selected evnets : %d\n"%select_d)
out_num_event.write("total selected color coherence events : %d"%select_cc)

out_num_event.close()



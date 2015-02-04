import ROOT
import os
import sys
import copy
ROOT.gROOT.SetBatch()
pi = ROOT.TMath.Pi()



in_type = sys.argv[1]
in_f = sys.argv[2]
out_f = sys.argv[3]

mc = True
if not in_type == 'mc':
    mc = False

in_rf = ROOT.TFile(in_f)
out_rf = ROOT.TFile(out_f, "RECREATE")

def hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut):
  hist = ROOT.TH1F(name, title, bin_set[0], bin_set[1], bin_set[2])
  hist.GetXaxis().SetTitle(x_name)
  hist.GetYaxis().SetTitle(y_name)
  #hist.SetLineColor(color)
  hist.Sumw2()
  #hist.SetStats(0)
  tr.Project(name, br, cut)
  return hist

def hist2_maker(name,tr,br_reco,br_gen,cut):
  hist2 = ROOT.TH2F(name, name, 18,0,pi, 18,0,pi)
  hist2.GetXaxis().SetTitle("reco_beta")
  hist2.GetYaxis().SetTitle("gen_beta")
  hist2.Sumw2()
  tr.Project(name,br_gen+":"+br_reco,cut)
  return hist2
### analysis cuts for data

if mc:
    sys_e = ["pt", "eup", "edown", "es", "esup", "esdown"]
else:
    sys_e = ["pt"]    
hist_l = []
for sys in sys_e:

  tr_beta  = in_rf.Get("%s_beta"%sys)
  ## event selection
  r_mass_cut = "(%s_raw_mass > 220)*"%sys
  dr_cut = "(%s_del_r>0.5)*(%s_del_r<1.5)*"%(sys,sys)
  eta_cut = "(abs(%s_jet1_eta)<2.5)*"%sys
  min_pt_cut = "(%s_jet1_pt>30)*(%s_jet2_pt>30)*(%s_jet3_pt>30)*"%(sys,sys,sys)
  d_cut = r_mass_cut+dr_cut+eta_cut+min_pt_cut

## event classification

  l_eta = "(abs(%s_jet2_eta)<0.8)*"%sys
  h_eta = "(abs(%s_jet2_eta)>0.8)*(abs(%s_jet2_eta)<2.5)*"%(sys,sys)
  ##hlt : 40:0, 80:1, 140:2, 200:3, 260:4, 320:5
  if mc:
    h_pt = "(%s_jet1_pt>507)*(%s_jet1_pt<2500)*"%(sys,sys)
    m_pt = "(%s_jet1_pt>220)*(%s_jet1_pt<507)*"%(sys,sys)
    l_pt = "(%s_jet1_pt>74)*(%s_jet1_pt<220)*"%(sys,sys)
    e_w = "(%s_pu_w)"%sys
  else:
    h_pt = "(%s_jet1_pt>507)*(%s_jet1_pt<2500)*(%s_hlt80_pass == 1)*(%s_hlt80_pre)"%(sys,sys,sys,sys)
    m_pt = "(%s_jet1_pt>220)*(%s_jet1_pt<507)*(%s_hlt140_pass == 1)*(%s_hlt140_pre)"%(sys,sys,sys,sys)
    l_pt = "(%s_jet1_pt>74)*(%s_jet1_pt<220)*(%s_hlt320_pass == 1)*(%s_hlt320_pre)"%(sys,sys,sys,sys)
    e_w = "*(1.0)"
  ## event weight


  ## cc hist
  eta_bin = ["low_eta", "high_eta"]
  eta_bin_cut = [l_eta, h_eta]
  pt_bin = ["low_pt", "medium_pt", "high_pt"]
  pt_bin_cut = [l_pt, m_pt, h_pt]
  beta_l = ["beta", "del_eta", "del_phi", "del_r", "raw_mass"] 
  beta_bin = [[18, 0, pi], [30, -3, 3], [30, -3, 3], [30, 0, 3], [50, 0, 5000]]

  jet_l = ["pt", "eta", "phi"]

  jet_bin = [[[30,0,250],[30,-3,3],[30,-pi,pi]],[[30,0,550],[30,-3,3],[30,-pi,pi]],[[30,0,2500],[30,-3,3],[30,-pi,pi]]]
  ev_l = ["njet", "met", "nvtx"]  
  ev_bin = [[50, 0, 50],[100, 0, 1000], [70, 0, 70]]

  for eta_i, eta_loop in enumerate(eta_bin):
    for pt_i, pt_loop in enumerate(pt_bin):
      for i, beta_loop in enumerate(beta_l):
        name = eta_loop+"_"+pt_loop+"_%s_"%sys+beta_loop
        title = name
        bin_set = beta_bin[i]
        x_name = beta_loop
        y_name = "count"
        tr = tr_beta
        br = "%s_"%sys + beta_loop
        cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
        hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))
      for ji in xrange(3):
        for i, jet_loop in enumerate(jet_l):
          name = eta_loop+"_"+pt_loop+"_%s_jet%d_"%(sys,ji+1)+jet_loop
          title = name
          bin_set = jet_bin[pt_i][i]
          x_name = jet_loop
          y_name = "count"
          tr = tr_beta
          br = "%s_jet%d_"%(sys,ji+1)+jet_loop
          cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
          hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))
      for i, ev_loop in enumerate(ev_l):
        name = eta_loop+"_"+pt_loop+"_%s_"%sys+ev_loop
        title = name
        bin_set = ev_bin[i]
        x_name = ev_loop
        y_name = "count"
        tr = tr_beta
        br = "%s_"%sys+ev_loop
        cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
        hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))
if mc:
  pu_l = ["pu_w_up", "pu_w_down"]
  for pu in pu_l:
    sys = "pt"
    tr_beta  = in_rf.Get("%s_beta"%sys)
    ## event selection
    r_mass_cut = "(%s_raw_mass > 220)*"%sys
    dr_cut = "(%s_del_r>0.5)*(%s_del_r<1.5)*"%(sys,sys)
    eta_cut = "(abs(%s_jet1_eta)<2.5)*"%sys
    min_pt_cut = "(%s_jet1_pt>30)*(%s_jet2_pt>30)*(%s_jet3_pt>30)*"%(sys,sys,sys)
    d_cut = r_mass_cut+dr_cut+eta_cut+min_pt_cut

## event classification
    l_eta = "(abs(%s_jet2_eta)<0.8)*"%sys
    h_eta = "(abs(%s_jet2_eta)>0.8)*(abs(%s_jet2_eta)<2.5)*"%(sys,sys)
    ##hlt : 40:0, 80:1, 140:2, 200:3, 260:4, 320:5
    h_pt = "(%s_jet1_pt>507)*(%s_jet1_pt<2500)*"%(sys,sys)
    m_pt = "(%s_jet1_pt>220)*(%s_jet1_pt<507)*"%(sys,sys)
    l_pt = "(%s_jet1_pt>74)*(%s_jet1_pt<220)*"%(sys,sys)

  ## event weight
    e_w = "(%s_%s)"%(sys, pu)

  ## cc hist
    eta_bin = ["low_eta", "high_eta"]
    eta_bin_cut = [l_eta, h_eta]
    pt_bin = ["low_pt", "medium_pt", "high_pt"]
    pt_bin_cut = [l_pt, m_pt, h_pt]
    beta_l = ["beta", "del_eta", "del_phi", "del_r", "raw_mass"] 
    beta_bin = [[18, 0, pi], [30, -3, 3], [30, -3, 3], [30, 0, 3], [50, 0, 5000]]

    jet_l = ["pt", "eta", "phi"]

    jet_bin = [[[30,0,250],[30,-3,3],[30,-pi,pi]],[[30,0,550],[30,-3,3],[30,-pi,pi]],[[30,0,2500],[30,-3,3],[30,-pi,pi]]]
    ev_l = ["njet", "met", "nvtx"]  
    ev_bin = [[50, 0, 50],[100, 0, 1000], [70, 0, 70]]
    for eta_i, eta_loop in enumerate(eta_bin):
      for pt_i, pt_loop in enumerate(pt_bin):
        for i, beta_loop in enumerate(beta_l):
          name = eta_loop+"_"+pt_loop+"_%s_"%pu+beta_loop
          title = name
          bin_set = beta_bin[i]
          x_name = beta_loop
          y_name = "count"
          tr = tr_beta
          br = "%s_"%sys + beta_loop
          cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
          hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))
        for ji in xrange(3):
          for i, jet_loop in enumerate(jet_l):
            name = eta_loop+"_"+pt_loop+"_%s_jet%d_"%(pu,ji+1)+jet_loop
            title = name
            bin_set = jet_bin[pt_i][i]
            x_name = jet_loop
            y_name = "count"
            tr = tr_beta
            br = "%s_jet%d_"%(sys,ji+1)+jet_loop
            cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
            hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))
        for i, ev_loop in enumerate(ev_l):
          name = eta_loop+"_"+pt_loop+"_%s_"%pu+ev_loop
          title = name
          bin_set = ev_bin[i]
          x_name = ev_loop
          y_name = "count"
          tr = tr_beta
          br = "%s_"%sys+ev_loop
          cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
          hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))


    tr_beta  = in_rf.Get("pt_beta")
    ## event selection
    r_mass_cut = "(pt_raw_mass > 220)*"
    dr_cut = "(pt_del_r>0.5)*(pt_del_r<1.5)*"
    eta_cut = "(abs(pt_jet1_eta)<2.5)*"
    min_pt_cut = "(pt_jet1_pt>30)*(pt_jet2_pt>30)*(pt_jet3_pt>30)*"
    d_cut = r_mass_cut+dr_cut+eta_cut+min_pt_cut

    ## event classification
    l_eta = "(abs(pt_jet2_eta)<0.8)*"
    h_eta = "(abs(pt_jet2_eta)>0.8)*(abs(pt_jet2_eta)<2.5)*"
    ##hlt : 40:0, 80:1, 140:2, 200:3, 260:4, 320:5
    h_pt = "(pt_jet1_pt>507)*(pt_jet1_pt<2500)*"
    m_pt = "(pt_jet1_pt>220)*(pt_jet1_pt<507)*"
    l_pt = "(pt_jet1_pt>74)*(pt_jet1_pt<220)*"
    ## event weight
    e_w = "(pt_pu_w)"
    eta_bin = ["low_eta", "high_eta"]
    eta_bin_cut = [l_eta, h_eta]
    pt_bin = ["low_pt", "medium_pt", "high_pt"]
    pt_bin_cut = [l_pt, m_pt, h_pt]

  for eta_i, eta_loop in enumerate(eta_bin):
    for pt_i, pt_loop in enumerate(pt_bin):
      name = eta_loop+"_"+pt_loop+"_unfold"
      tr = tr_beta
      br_gen = "pt_gen_beta"
      br_reco = "pt_beta"
      cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
      hist_l.append(copy.deepcopy(hist2_maker(name,tr,br_reco,br_gen,cut)))


for x in hist_l:
  x.Write()
out_rf.Write()
out_rf.Close()
in_rf.Close()

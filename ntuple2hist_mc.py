import ROOT
import os
import sys
import copy
ROOT.gROOT.SetBatch()
pi = ROOT.TMath.Pi()

in_f = sys.argv[1]
out_f = sys.argv[2]

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

### analysis cuts for data


sys_e = ["pt", "eup", "edown", "es", "esup", "esdown"]
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
  h_pt = "(%s_jet1_pt>507)*(%s_jet1_pt<2500)*"%(sys,sys)
  m_pt = "(%s_jet1_pt>220)*(%s_jet1_pt<507)*"%(sys,sys)
  l_pt = "(%s_jet1_pt>74)*(%s_jet1_pt<220)*"%(sys,sys)

  ## event weight
  e_w = "(%s_pu_w)"%sys

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
  ev_bin = [[100, 0, 100],[100, 0, 1000], [100, 0, 100]]

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



for x in hist_l:
  x.Write()
out_rf.Write()
out_rf.Close()
in_rf.Close()

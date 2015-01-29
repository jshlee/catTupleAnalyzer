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

tr_beta  = in_rf.Get("beta")


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

## event selection
r_mass_cut = "(raw_mass > 220)*"
dr_cut = "(del_r>0.5)*(del_r<1.5)*"
eta_cut = "(abs(jet1_eta)<2.5)*"
min_pt_cut = "(jet1_pt>30)*(jet2_pt>30)*(jet3_pt>30)*"
d_cut = r_mass_cut+dr_cut+eta_cut+min_pt_cut

## event classification

l_eta = "(abs(jet2_eta)<0.8)*"
h_eta = "(abs(jet2_eta)>0.8)*(abs(jet2_eta)<2.5)*"
##hlt : 40:0, 80:1, 140:2, 200:3, 260:4, 320:5
h_pt = "(jet1_pt>507)*(jet1_pt<2500)*(hlt320_pass==1)*(hlt320_pre)"
m_pt = "(jet1_pt>220)*(jet1_pt<507)*(hlt140_pass==1)*(hlt320_pass==0)*(hlt140_pre)"
l_pt = "(jet1_pt>74)*(jet1_pt<220)*(hlt80_pass==1)*(hlt140_pass==0)*(hlt320_pass==0)*(hlt80_pre)"

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
ev_bin = [[100, 0, 100],[100, 0, 1000], [100, 0, 100]]



hist_l = []
for eta_i, eta_loop in enumerate(eta_bin):
  for pt_i, pt_loop in enumerate(pt_bin):
    for i, beta_loop in enumerate(beta_l):
      name = eta_loop+"_"+pt_loop+"_"+beta_loop
      title = name
      bin_set = beta_bin[i]
      x_name = beta_loop
      y_name = "count"
      tr = tr_beta
      br = beta_loop
      cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i]
      hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))
    for ji in xrange(3):
      for i, jet_loop in enumerate(jet_l):
        name = eta_loop+"_"+pt_loop+"_jet%d_"%(ji+1)+jet_loop
        title = name
        bin_set = jet_bin[pt_i][i]
        x_name = jet_loop
        y_name = "count"
        tr = tr_beta
        br = br = "jet%d_"%(ji+1)+jet_loop
        cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i]
        hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))
    for i, ev_loop in enumerate(ev_l):
      name = eta_loop+"_"+pt_loop+"_"+ev_loop
      title = name
      bin_set = ev_bin[i]
      x_name = ev_loop
      y_name = "count"
      tr = tr_beta
      br = ev_loop
      cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i]
      hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))



for x in hist_l:
  x.Write()
out_rf.Write()
out_rf.Close()
in_rf.Close()

import ROOT, os, sys, copy
from array import array

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
  if bin_set[2] == 2500:
    bin = []
    for x in xrange(15):
      bin.append(2500.0/2.0*float(x)/15.0)
    bin.append(1500)
    bin.append(2000)
    bin.append(2500)
    pt_bin = array('d', bin)
    hist = ROOT.TH1F(name, title, len(pt_bin)-1, pt_bin)
  else:
    hist = ROOT.TH1F(name, title, bin_set[0], bin_set[1], bin_set[2])
  hist.GetXaxis().SetTitle(x_name)
  hist.GetYaxis().SetTitle(y_name)
  hist.Sumw2()
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
    sys_e = ["pt", "es", "esup", "esdown", "jarup", "jardown", "pu_w_up", "pu_w_down"]
else:
    sys_e = ["pt","eup","edown"]    
hist_l = []
for sys in sys_e:
  if mc:
    e_w = "*(%s_pu_w)"%(sys)
    if sys.startswith("pu_w"):
      e_w = "*(pt_%s)"%sys
  else:
    e_w = "*(1.0)"
  if sys.startswith("pu_w"):
    s_name = sys
    sys = "pt"
  else:
    s_name = sys
  tr_beta  = in_rf.Get("%s_beta"%sys)
  ## event selection
  r_mass_cut = "(%s_raw_mass > 220)*"%sys
  #r_mass_cut = "(%s_raw_mass > 250)*"%sys
  dr_cut = "(%s_del_r>0.5)*(%s_del_r<1.5)*"%(sys,sys)
  dr12_cut = "(%s_del_r12<1.0)*"%(sys)
  eta_cut = "(abs(%s_jet1_eta)<2.5)*"%sys
  min_pt_cut = "(%s_jet1_pt>30)*(%s_jet2_pt>30)*(%s_jet3_pt>30)*"%(sys,sys,sys)
  met_cut = "(%s_met<0.3)*"%(sys)
  #d_cut = r_mass_cut+dr_cut+dr12_cut+eta_cut+min_pt_cut+met_cut
  d_cut = r_mass_cut+dr_cut+dr12_cut+eta_cut+min_pt_cut

## event classification

  l_eta = "(abs(%s_jet2_eta)>0.0)*(abs(%s_jet2_eta)<0.8)*"%(sys,sys)
  m_eta = "(abs(%s_jet2_eta)>0.8)*(abs(%s_jet2_eta)<1.5)*"%(sys,sys)
  h_eta = "(abs(%s_jet2_eta)>1.5)*(abs(%s_jet2_eta)<2.5)*"%(sys,sys)

  h_pt = "(%s_jet1_pt>510)*(%s_jet1_pt<2500)*(%s_hlt320_pass == 1)"%(sys,sys,sys)
  m_pt = "(%s_jet1_pt>220)*(%s_jet1_pt<500)*(%s_hlt140_pass == 1)"%(sys,sys,sys)
  l_pt = "(%s_jet1_pt>150)*(%s_jet1_pt<220)*(%s_hlt80_pass == 1)"%(sys,sys,sys)

  ## cc hist
  eta_bin = ["low_eta", "medium_eta", "high_eta"]
  eta_bin_cut = [l_eta, m_eta, h_eta]
  pt_bin = ["low_pt", "medium_pt", "high_pt"]
  pt_bin_cut = [l_pt, m_pt, h_pt]
  beta_l = ["beta", "del_eta", "del_phi", "del_r", "raw_mass","del_r12"] 
  beta_bin = [[18, 0, pi], [30, -3, 3], [30, -3, 3], [30, 0, 3], [50, 0, 5000], [30,0,3]]
  jet_l = ["pt", "eta", "phi"]
  jet_bin = [[[30,0,250],[30,-3,3],[30,-pi,pi]],[[30,0,550],[30,-3,3],[30,-pi,pi]],[[30,0,2500],[30,-3,3],[30,-pi,pi]]]
  ev_l = ["njet", "met", "nvtx"]  
  ev_bin = [[30, 0, 30],[100, 0, 1], [50, 0, 50]]

  for eta_i, eta_loop in enumerate(eta_bin):
    for pt_i, pt_loop in enumerate(pt_bin):
      if mc and s_name == "pt":
        name = eta_loop+"_"+pt_loop+"_unfold"
        name2 = eta_loop+"_"+pt_loop+"_gen_beta"
        br_gen = "pt_gen_beta"
        br_reco = "pt_beta"
        tr = tr_beta
        cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
        hist_l.append(copy.deepcopy(hist_maker(name2,name2, [18,0,pi], "gen_beta", "count", tr,br_gen,cut)))
        hist_l.append(copy.deepcopy(hist2_maker(name,tr,br_reco,br_gen,cut)))
 
      for i, beta_loop in enumerate(beta_l):
        name = eta_loop+"_"+pt_loop+"_%s_"%s_name+beta_loop
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
          name = eta_loop+"_"+pt_loop+"_%s_jet%d_"%(s_name,ji+1)+jet_loop
          title = name
          bin_set = jet_bin[pt_i][i]
          x_name = jet_loop
          y_name = "count"
          tr = tr_beta
          br = "%s_jet%d_"%(sys,ji+1)+jet_loop
          cut = d_cut + eta_bin_cut[eta_i] + pt_bin_cut[pt_i] + e_w
          hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut)))
      for i, ev_loop in enumerate(ev_l):
        name = eta_loop+"_"+pt_loop+"_%s_"%s_name+ev_loop
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

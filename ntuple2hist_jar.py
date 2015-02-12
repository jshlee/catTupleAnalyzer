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

### hist booking 
eta_bin = [0.0, 0.8,2.0,2.5,5.0]
pt_bin = [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 500.0, 1000.0]
eta_l = [[],[],[],[]]
for i,eta in enumerate(eta_l):
  for pt in pt_bin:
    eta_l[i].append(copy.deepcopy(ROOT.TH1F("%1.1fTo%1.1f_eta_%.1f_pt_d_eta"%(eta_bin[i],eta_bin[i+1],pt), "%1.1fTo%1.1f_eta_%.1f_pt_d_eta"%(eta_bin[i],eta_bin[i+1],pt), 100,-0.5,0.5)))

phi_l = [[],[],[],[]]
for i,phi in enumerate(phi_l):
  for pt in pt_bin:
    phi_l[i].append(copy.deepcopy(ROOT.TH1F("%1.1fTo%1.1f_eta_%.1f_pt_d_phi"%(eta_bin[i],eta_bin[i+1],pt),"%1.1fTo%1.1f_eta_%.1f_pt_d_phi"%(eta_bin[i],eta_bin[i+1],pt), 100,-0.5,0.5)))

tr = in_rf.Get("pt_beta")

def find_bin(pt):
  pt_bin = [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 500.0, 1000.0]
  for index, x in enumerate(pt_bin[:-1]):
    if pt < pt_bin[index+1]:
      return index
      break

for e in tr:
  pt1 = find_bin(e.pt_jet1_pt)
  pt2 = find_bin(e.pt_jet2_pt)
  pt3 = find_bin(e.pt_jet3_pt)
  eta1 = abs(e.pt_jet1_eta)
  eta2 = abs(e.pt_jet2_eta)
  eta3 = abs(e.pt_jet3_eta)
  d_eta1 = e.pt_jet1_d_eta
  d_eta2 = e.pt_jet2_d_eta
  d_eta3 = e.pt_jet3_d_eta
  d_phi1 = e.pt_jet1_d_phi
  d_phi2 = e.pt_jet2_d_phi
  d_phi3 = e.pt_jet3_d_phi

  for i in xrange(4):
    if eta1 > eta_bin[i] and eta1 < eta_bin[i+1]:
      eta_l[i][pt1].Fill(d_eta1)
      phi_l[i][pt1].Fill(d_phi1)
    if eta2 > eta_bin[i] and eta2 < eta_bin[i+1]:
      eta_l[i][pt2].Fill(d_eta2)
      phi_l[i][pt2].Fill(d_phi2)  
    if eta3 > eta_bin[i] and eta3 < eta_bin[i+1]:
      eta_l[i][pt3].Fill(d_eta3)
      phi_l[i][pt3].Fill(d_phi3)
    

   
for x in eta_l:
  for y in x:
    y.Write()
for x in phi_l:
  for y in x:
    y.Write()

out_rf.Write()
out_rf.Close()
in_rf.Close()

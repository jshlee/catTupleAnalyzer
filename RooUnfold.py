import ROOT, sys, os, copy

ROOT.gSystem.Load("/pnfs/user/hyunyong/RooUnfold-1.1.1/libRooUnfold")

iter = 4

mc = ROOT.TFile("QCD_HT_TuneZ2star_8TeV-madgraph-pythia6_hist.root")



beta_list = []

reco_list = []
gen_list = []
h2d_list = []

pt_bin = ["low_pt", "medium_pt", "high_pt"]
eta_bin = ["low_eta", "high_eta"]
for pt in pt_bin:
  for eta in eta_bin:
    beta_list.append(eta+"_"+pt)
    
for beta in beta_list:
  reco_list.append(copy.deepcopy(mc.Get(beta+"_pt_beta").Clone(beta+"_mc")))
  gen_list.append(copy.deepcopy(mc.Get(beta+"_gen_beta")))
  h2d_list.append(copy.deepcopy(mc.Get(beta+"_unfold")))

RooUnfold_res = []

for i, beta in enumerate(beta_list):
  RooUnfold_res.append(ROOT.RooUnfoldResponse(reco_list[i], gen_list[i], h2d_list[i], beta+"_roounfold_res", beta+"_roounfold_res"))

RooUnfold_bay = []

for i,res in enumerate(RooUnfold_res):
  RooUnfold_bay.append(ROOT.RooUnfoldBayes(res, reco_list[i], iter))

Unfold_list = []
for res in RooUnfold_bay:
  tmph= res.Hreco()
  Unfold_list.append(tmph.Clone(tmph.GetName()+"_h"))

out_f = ROOT.TFile("Unfold_hist_MAD.root","RECREATE")
out_f.cd()
for x in xrange(len(Unfold_list)):
  gen_list[x].Write()
  reco_list[x].Write()
  Unfold_list[x].Write()
  RooUnfold_res[x].Write()


out_f.Write()
out_f.Close()

"""
from plot_maker_r4 import comp_plot
os.chdir("plots_MAD_unf")
color = [1,2,3,4]
root_name = ["Data", "MC_RECO", "MC_GEN", "Unfold"]
for x in xrange(len(Unfold_list)):
  tmp_l = []
  tmp_l.append(data_list[x])
  tmp_l.append(reco_list[x])
  tmp_l.append(gen_list[x])
  tmp_l.append(Unfold_list[x])
  comp_plot(tmp_l, color, root_name)
"""




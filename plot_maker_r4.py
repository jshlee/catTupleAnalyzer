from ROOT import *
from os import mkdir, chdir
import copy
#from cc_ana_tool import *


def comp_plot(h_list, color, root_name):
  #pad = TCanvas(h_list[0].GetName(), h_list[0].GetName(), 800, 600)
  pad = TCanvas("c1", "c1", 800, 600)
  set_log = 0
  tmp = h_list[0].GetName().split("_")
  if tmp[-1] =="pt" or tmp[-1] == "met" or tmp[-1] == "mass":
    set_log = 1
  pad.cd()
  #set_log = 0
  le = TLegend(0.8, 0.5, 0.9, 0.6)
  le.SetFillStyle(0)
  le.SetBorderSize(0)
  padt = TPad("t", "t", 0.0, 1.0, 1.0, 0.45)
  padb = TPad("b", "b", 0.0, 0.45, 1.0, 0.0)
  margin_s = 0.005
  margin_b = 2.0
  padt.Draw()
  padt.cd()
  padt.SetLogy(set_log)
  padt.SetBottomMargin(0.05)
  padt.SetTopMargin(0.18)

  tmp_h =[]
  for x in h_list:
    tmp_h.append(copy.deepcopy(x.DrawNormalized()))
  t_max = 0.0
  t_min = 1.0
  ent_l = []
  for i, x in enumerate(tmp_h):
    x.SetLineColor(color[i])
    x.SetLineWidth(2)
    tmp_max = x.GetMaximum()
    if t_max < tmp_max:
      t_max = tmp_max
  for i, h in enumerate(tmp_h):
    le.AddEntry(h, root_name[i])
    if i == 0:
      if set_log == 1:
        h.SetMinimum(0.00001)
      else:
        h.SetMinimum(0)
      h.SetMaximum(t_max*1.2)
      h.SetStats(0)
      h.GetYaxis().SetTitle("Normalized Yield")
      h.GetYaxis().SetTitleOffset(0.9)
      h.GetYaxis().SetTitleSize(0.06)
      h.GetYaxis().SetLabelSize(0.06)
      h.GetXaxis().SetLabelOffset(1.7)
      h.GetXaxis().SetTitleOffset(1.7)
      h.SetTitle(h.GetTitle())
      gStyle.SetTitleFontSize(0.1);
      h.Draw()
    else:
      h.Draw("same")
  pad.cd()
  padb.Draw()
  ###div. plot
  padb.cd()
  padb.SetGrid()
  padb.SetTopMargin(0.018)
  padb.SetBottomMargin(0.3)
  div_h = []
  for x in tmp_h:
    tmp_0 = tmp_h[0].Clone()
    tmp_h1 = x.Clone()
    tmp_h1.Divide(tmp_0)
    div_h.append(tmp_h1)
  le2 = TLegend(0.8, 0.15, 0.9, 0.3)
  le2.SetFillStyle(0)
  le2.SetBorderSize(0)
  for i, h in enumerate(div_h):
    h.SetLineWidth(2)
    h.SetLineColor(color[i])
    if i == 0:
      continue
    if i == 1:
      le2.AddEntry(h, root_name[i])
      h.SetStats(0)
      h.SetTitle("")
      h.SetMaximum(2.0)
      h.SetMinimum(0.0)
      h.GetYaxis().SetTitle("mc / data")
      h.GetYaxis().SetTitleSize(0.08)
      h.GetYaxis().SetTitleOffset(0.65)
      h.GetYaxis().SetLabelSize(0.1)
      h.GetXaxis().SetTitleSize(0.1)
      h.GetYaxis().SetLabelSize(0.05)
      h.GetXaxis().SetLabelSize(0.07)
      h.Draw()
    else:
      le2.AddEntry(h, root_name[i])
      h.Draw("same")
  pad.cd()
  le.Draw()
  le2.Draw()
  p = h_list[0].GetName()
  print p
  store_n = p+".png"
  pad.SaveAs(store_n)

  return pad



root_f_list = ["Jet_ALL_hist.root", "QCD_HT_TuneZ2star_8TeV-madgraph-pythia6_hist.root"]
root_name = ["Data", "MC"]
tr_list = []
for x in root_f_list:
  tr_list.append(TFile(x))


chdir("./plots3")

his_list = [x.GetName() for x in tr_list[0].GetListOfKeys()]

#color = [1,3,4,5,6]
color = [1,2,3,4,5,6]

for p in his_list:
  h_list = []
  for x in tr_list:
    h_list.append(copy.deepcopy(x.Get(p)))
  tmpc = comp_plot(h_list,color,root_name)



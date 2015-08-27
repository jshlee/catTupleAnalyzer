from ROOT import *
import copy
from array import array
gROOT.SetBatch()
tf = TFile("jar.root")
h_l = [x.GetName() for x in tf.GetListOfKeys()]

out_f = TFile("jar_sig_pt.root","RECREATE")

eta_l = []
phi_l = []
pt_bin = array('d',[0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 500.0, 1000.0, 2500.0])
ev = [0.0,0.8,2.0,2.5,5.0]
for x in xrange(4):
  eta_l.append(copy.deepcopy(TH1F("%1.1fTo%1.1f_eta_eta_r"%(ev[x],ev[x+1]), "#eta %1.1f To %1.1f #Delta #eta Resolution"%(ev[x],ev[x+1]), len(pt_bin)-1, pt_bin)))
  phi_l.append(copy.deepcopy(TH1F("%1.1fTo%1.1f_eta_phi_r"%(ev[x],ev[x+1]), "#eta %1.1f To %1.1f #Delta #phi Resolution"%(ev[x],ev[x+1]), len(pt_bin)-1, pt_bin)))
for h in h_l:
  x = tf.Get(h)
  n = x.GetName().split("_")
  eta = float(n[0].split("To")[0])
  pt = float(n[2].split("To")[0])+25.0
  if pt >1050.0:
    continue
  type = n[-1]
  x.Fit("gaus")
  fitresult = TVirtualFitter.GetFitter()
  sig = fitresult.GetParameter(2)
  if not sig:
    continue
  for i,e in enumerate([0.0,0.8,2.0,2.5]):
    if eta == e:
      if type == "eta":
        eta_l[i].Fill(pt,sig)
      else:
        phi_l[i].Fill(pt,sig)

f1 = TF1("myfunc", "[0]/x + [1]/sqrt(x) + [2]")
for x in eta_l:
  print x
  x.Fit("myfunc")
for x in phi_l:
  print x
  x.Fit("myfunc")


out_f.cd()
for x in eta_l:
  x.Write()
for x in phi_l:
  x.Write()
out_f.Write()
out_f.Close()
    

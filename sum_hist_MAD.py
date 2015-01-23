import ROOT, sys, copy, os

target = sys.argv[1]

list = [x for x in os.listdir(target) if x.endswith("num_of_events.txt")] 

sample_l = [[],[],[],[]]
eve_num = [[0,0,0,0], [0,0,0,0], [0,0,0,0]]
for x in list:
  index = -1
  tmp = x.split("_")[1]
  if tmp == "HT-100To250":
    index = 0
  if tmp == "HT-250To500":
    index = 1
  if tmp == "HT-500To1000":
    index = 2
  if tmp == "HT-1000ToInf":
    index = 3
  sample_l[index].append(x)

for x in xrange(4):
  for y in sample_l[x]:
    tmp = open(target+"/"+y)
    for i,z in enumerate(tmp):
       eve_num[i][x] += float(z.split()[-1])
      
  

cross = [1.036E7, 276000.0, 8426.0, 204.0]

root_list = ["QCD_HT-100To250_TuneZ2star_8TeV-madgraph-pythia_hist.root", "QCD_HT-250To500_TuneZ2star_8TeV-madgraph-pythia6_hist.root", "QCD_HT-500To1000_TuneZ2star_8TeV-madgraph-pythia6_hist.root", "QCD_HT-1000ToInf_TuneZ2star_8TeV-madgraph-pythia6_hist.root"]

tf = []
for x in root_list:
  tf.append(ROOT.TFile(x))

key = [x.GetName() for x in tf[0].GetListOfKeys()]

weight = [x*eve_num[1][i]/eve_num[0][i] for i,x in enumerate(cross)]
weight2 = [x*eve_num[2][i]/eve_num[0][i] for i,x in enumerate(cross)]
"""
sum_hist = []
for x in key:
  tmp_hist = []
  for y in tf:
    tmp_hist.append(y.Get(x))
  hist = tmp_hist[0].Clone()
  hist.Reset()
  for i,h in enumerate(tmp_hist):
    tmp_name = x.split("_")
    if len(tmp_name)>3 and  tmp_name[1] == "pt" and tmp_name[3] == "eta":
      hist.Add(h, weight2[i])
    else:
      hist.Add(h, weight[i])
  sum_hist.append(copy.deepcopy(hist))

out_root = ROOT.TFile("QCD_HT_TuneZ2star_8TeV-madgraph-pythia6_hist.root","RECREATE")
for h in sum_hist:
  h.Write()

out_root.Write()
out_root.Close()
"""
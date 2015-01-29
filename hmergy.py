import os
import sys

target = sys.argv[1]


root_f  = [d for d in os.listdir(target) if d.endswith(".root")]
sample_list = []
for x in root_f:
  tmp = x.split("_")
  tmp2 = ""
  for t in tmp:
    if t == "ntuple":
      break
    tmp2 += t+"_" 
  try:
    if sample_list.index(tmp2)<0:
      sample_list.append(tmp2)
  except:
    sample_list.append(tmp2)


print sample_list
os.chdir(target)

for x in sample_list:
  nu_root = x+"hist.root"
  if os.path.exists(nu_root):
    os.system("rm "+nu_root)
  os.system("hadd "+x+"hist.root "+x+"*.root")
  os.system("mv "+nu_root+" ..")


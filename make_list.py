import os, sys

max_n = 10
type = sys.argv[1]
mc = False
if type == "mc":
  mc = True

path = "/pnfs/user/cattuple"
f_list = os.listdir(path)

if mc:
  dir = "MC_ROOT_FILE_LISTS"+str(max_n)
else:
  dir = "RD_ROOT_FILE_LISTS"+str(max_n)

os.mkdir(dir)
os.chdir(dir)

in_root_f = []
out_root_f = []

for x in f_list:
  tmp = x.split("_")[2:]
  tmp2 = ""
  for n in tmp:
    tmp2 += (n+"_")
  tmp2+="hist"
  if mc:
    if len(tmp2) >3 and tmp2.startswith("QCD_HT"):
      out_root_f.append(tmp2)
      in_root_f.append(path+"/"+x+"/results/")
  else:
    if len(tmp2) >3 and tmp2.startswith("Jet"):
      out_root_f.append(tmp2)
      in_root_f.append(path+"/"+x+"/results/")

list_log = open("list_log.log","w")

print  in_root_f
for i,ipath in enumerate(in_root_f):
  print ipath
  list_log.write(ipath+"\n")
  counter = 0
  tmp_l = os.listdir(ipath)
  file_l =[]
  for x in tmp_l:
    if x.endswith(".root"):
      file_l.append(x)
      counter += 1
  list_log.write("total number of root file : %d\n"%counter)
      
  co = 1
  f_in = 1
  tmp_f = open(out_root_f[i]+"_%03d.txt"%f_in,"w")
  for file in file_l:
    if divmod(co,max_n)[1]==0:
      tmp_f.close()
      f_in += 1
      tmp_f = open(out_root_f[i]+"_%03d.txt"%f_in,"w")
    tmp_f.write(ipath+file+"\n")
    co += 1



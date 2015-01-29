import os, sys, time

target = sys.argv[1]
if target[-1] =="/":
  target = target[:-1]

mc = False
type = "rd"
if target.split("_")[2] == "mc":
  mc = True
  type = "mc"

time_dir = time.strftime(target+"_hist_%d%b%Y_%HH%MM",time.localtime())
os.mkdir(time_dir)
itime_dir = os.getcwd()+"/"+time_dir

f_list = os.listdir(target)
ipath = os.getcwd()+"/"+target

ana_path = os.getcwd()

script_head ="""#PBS -S /bin/bash
#PBS -N color_coherence_hist_%s
#PBS -l nodes=1:ppn=1,walltime=72:00:00
#PBS -o $PBS_JOBID.$PBS_O_HOST.out
#PBS -e $PBS_JOBID.$PBS_O_HOST.err
#PBS -m abe
#PBS -V

#echo $PBS_O_HOST
cat $PBS_NODEFILE
#echo $PBS_TASKNUM

source /pnfs/etc/profile.d/cmsset_default.sh
cd /pnfs/user/hyunyong/cat7
eval `scramv1 runtime -sh`
"""%type

q_txt = os.listdir(target)
    
os.chdir(itime_dir)
for x in q_txt:
  if x.endswith(".root"):
    tmp_sc = open(itime_dir+"/"+x[:-5]+".cmd","w")
    tmp_sc.write(script_head)
    tmp_sc.write("\ncd "+itime_dir+"\n")
    tmp_sc.write("python "+ana_path+"/ntuple2hist_%s.py "%type+ipath+"/"+x+" "+itime_dir+"/"+x[:-5]+".root")
    tmp_sc.close()
    os.system("qsub -q kcms "+itime_dir+"/"+x[:-5]+".cmd")







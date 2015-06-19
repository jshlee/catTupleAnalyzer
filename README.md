# catTupleAnalyzer

##1st step
```
python make_list.py job_type
```
job_type is rd or mc.

make_list.py is going to make list of cattuple files and it will be in RD_ROOT_FILE_LISTS or MC_ROOT_FILE_LISTS


2nd step
```
python RunAna.py dir
```
dir is RD_ROOT_FILE_LIST or MC_ROOT_FILE_LIST

RunAna.py is submit batch job for analysis.py
Result files will be writed 
if you want run single job,
```
analysis.py job_type[rd|mc] in_put_file[Jet_Run2012A-22Jan2013-v1_ntuple_XXX.txt] out_put_file[Jet_Run2012A-22Jan2013-v1_ntuple_001.root]
```

3rd step
```
python Runhist.py dir
```
dir is ANA_RD_XXX or ANA_MC_XXX.
Runhist.py is submit bacth job for ntuple2hist.py

single run 
```
python ntuple2hist.py job_type in_put_file out_file_name
```
job_type is rd or mc.
in_put_file is ntuple file from analysis.py

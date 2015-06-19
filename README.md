# catTupleAnalyzer

1st step
make_list.py is going to make list of cattuple files and it will be in RD_ROOT_FILE_LISTS or MC_ROOT_FILE_LISTS
e.g)make_list.py rd 

2nd step
RunAna.py is summit batch job for analysis.py e.g.) RunAna.py RD_ROOT_FILE_LISTS
Result files will be writed in directory. e.g.) ANA_type_sample_name
if you want run single job,
analysis.py job_type[rd|mc] in_put_file[Jet_Run2012A-22Jan2013-v1_ntuple_XXX.txt] out_put_file[Jet_Run2012A-22Jan2013-v1_ntuple_001.root]


import os, sys

target = sys.argv[1]
err_log = [x for x in os.listdir(target) if x.endswith(".err") ]
os.chdir(target)
for x in err_log:
  os.system("cat "+x)

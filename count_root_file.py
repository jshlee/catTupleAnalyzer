import os
import sys

target = sys.argv[1]


dir = os.listdir(target)
root_f = [f for f in dir if f.endswith(".root")]
txt_f = [f for f in dir if f.endswith(".cmd")]

print len(txt_f), len(root_f)

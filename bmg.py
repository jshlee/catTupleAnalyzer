
head = """
\documentclass{beamer}
%\usepackage{graphics}
\usepackage{graphicx}
%\usepackage{hyperref}
%\usepackage{textpos}
%\usepackage{subfig}
%\usepackage{amssymb}
%\usepackage{amsmath}
\setbeamertemplate{footline}{\hspace*{.3cm}\hspace*{343pt} \insertframenumber}
\\begin{document}

"""
tail = """
\end{document}
"""
plot_beta =""
plot_pt = "jet_pt_cor_%d_log_1_cut_"
plot_eta = "jet_eta_%d_log_0_cut_"
plot_phi = "jet_phi_%d_log_0_cut_"
pt_end = "_log_y.eps"
o_end = ".eps"
cut_list = ["b_h_r15", "e_h_r15", "b_m_r15", "e_m_r15", "b_l_r15", "e_l_r15"]


sys_n = ["eud", "esud", "pu_ud"]
eta_l = ["low", "high"]
pt_l = ["high","medium", "low"]
g_l = ["beta", "del_eta", "del_phi", "del_r", "raw_mass", "jet1_pt", "jet1_eta", "jet1_phi", "jet2_pt", "jet2_eta", "jet2_phi", "jet3_pt", "jet3_eta", "jet3_phi","nvtx", "met"]

def make_bp():
  tex_l = """
  \\frame
  {
  }
"""
  
def make_fig(name):
  tmp = name.split("_")
  tmp_t = ""
  if tmp[0] == "eud":
    tmp_t += "Jet Energy Scale Up Down"
  elif tmp[0] == "esud":
    tmp_t += "Jet Energy Smear Up Down"
  elif tmp[0] == "pu":
    tmp_t += "Pile Up Weight Up Down"
  fig_l = "  \\frame{"
  fig_l = fig_l + "    \\vspace{-20pt} \n"
  fig_l = fig_l + "\\frametitle{%s}"%tmp_t
  fig_l = fig_l + "    \\begin{figure} \n"
  fig_l = fig_l + "    \scalebox{0.5} \n      { \n"
  fig_l = fig_l + "\includegraphics{./plotsSys/"+name+"}~~~ \n"
  fig_l = fig_l + "        }\n \end{figure}"
  fig_l = fig_l + "}"
  return fig_l


out_f = open("test.tex","w")
out_f.write(head)
for sys in sys_n:
  for eta in eta_l:
    for pt in pt_l:
      for g in g_l:
        out_f.write(make_fig(sys+"_"+eta+"_eta_"+pt+"_pt_pt_"+g+".eps"))
out_f.write(tail)

import os, sys
#os.system("latex test.tex")
#os.system("dvipdf test.dvi")





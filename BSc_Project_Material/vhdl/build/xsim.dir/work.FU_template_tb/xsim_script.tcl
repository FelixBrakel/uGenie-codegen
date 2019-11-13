set_param project.enableReportConfiguration 0
load_feature core
current_fileset
xsim {work.FU_template_tb} -autoloadwcfg -tclbatch {run.tcl}

set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/fe_export.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1
catch {*feoutputwithdata "C:/Program Files/Altair/2019/hm/templates/feoutput/nastran/nastran" "D:/training/caedecoder/hmdecoding/output/ground_truth/ws_nastran.bdf" 0 0 1 1 0} er
logit "feoutput: $er"
close $log
*quit 1

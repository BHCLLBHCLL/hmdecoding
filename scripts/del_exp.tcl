set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/del_exp.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
*createmark elements 1 5
catch {*deletemark elements 1} d1
logit "deleted elem 5: $d1"
*writefile "D:/training/caedecoder/hmdecoding/corpus/synthetic/1d_del_elem5.hm" 1
close $log
*quit 1

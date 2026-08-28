set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/car_miss2.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/car_section.hm" 1} rr
logit "readfile: $rr"
foreach eid {6885 6886 6911 6912 6956 28041 28100 28200 28300 28400 28437 28438 28443 28511} {
  set cfg "?"; set nodes "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} e1
  catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} e2
  logit "eid=$eid config=$cfg nodes=$nodes err1=$e1"
}
close $log
*quit 1

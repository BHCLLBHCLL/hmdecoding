set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/truck_miss_meta.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/truck.hm" 1} rr
logit "readfile: $rr"

# 采样缺失 eid 的 config / comp / 节点
set samples {216179 216180 216181 216200 217000 218000 219000 219500 219669 219677 219700 220000 220300 220409}
foreach eid $samples {
  set cfg "?"; set comp "?"; set name "?"; set nodes "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  catch {set comp [hm_getvalue elements id=$eid dataname=comp]} _
  catch {set name [hm_getvalue elements id=$eid dataname=name]} _
  catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} _
  logit "eid=$eid config=$cfg comp=$comp name=$name nodes=[llength $nodes] $nodes"
}
close $log
*quit 1

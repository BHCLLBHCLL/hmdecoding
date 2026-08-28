set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/car_node12861.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/car_section.hm" 1} rr
logit "readfile: $rr"
# 找包含 node 12861 的元素
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
set found 0
foreach eid $elist {
  set nodes ""
  catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} _
  if {[lsearch -exact $nodes 12861] >= 0} {
    set cfg "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    logit "eid=$eid config=$cfg nodes=$nodes"
    incr found
    if {$found >= 5} {break}
  }
}
logit "found=$found"
# 也查 12861 节点是否存在
set x "?"; set y "?"; set z "?"
catch {set x [hm_getvalue nodes id=12861 dataname=x]} _
catch {set y [hm_getvalue nodes id=12861 dataname=y]} _
catch {set z [hm_getvalue nodes id=12861 dataname=z]} _
logit "node 12861: x=$x y=$y z=$z"
close $log
*quit 1

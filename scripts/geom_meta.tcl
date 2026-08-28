set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/geom_meta.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/geometry.hm" 1} rr
logit "readfile: $rr"
# 采样几个 eid 的 config/nodes
foreach eid {1 2 3 4 5 100 1000 2000 3000 4000 4116} {
  set cfg "?"; set nodes "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} _
  logit "eid=$eid config=$cfg nnodes=[llength $nodes] nodes=$nodes"
}
# 元素 id 范围
catch {logit "max_elem_id=[hm_entityinfo maxid elements]"}
catch {logit "elem_count=[hm_entityinfo count elements]"}
close $log
*quit 1

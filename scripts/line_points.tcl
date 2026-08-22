set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/line_points.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
*createmark lines 1 "all"
set llist [hm_getmark lines 1]
logit "lines: $llist"
foreach lid $llist {
  # 尝试按线选点
  set pts ""
  catch {*createmark points 1 "by line" $lid} e1
  catch {set pts [hm_getmark points 1]} _
  logit "line $lid -> points(by line): $pts err=$e1"
}
# 也试 nodes by line
foreach lid $llist {
  set ns ""
  catch {*createmark nodes 1 "by line" $lid} e2
  catch {set ns [hm_getmark nodes 1]} _
  logit "line $lid -> nodes(by line): $ns err=$e2"
}
close $log
*quit 1

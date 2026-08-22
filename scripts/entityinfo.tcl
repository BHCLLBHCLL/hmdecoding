set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/entityinfo.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
foreach op {maxid count exist} {
  set v ""
  catch {set v [hm_entityinfo $op lines]} e1
  logit "hm_entityinfo $op lines -> '$v' err=$e1"
}
catch {set v [hm_entityinfo name lines 18]} e2
logit "hm_entityinfo name lines 18 -> '$v' err=$e2"
catch {set v [hm_entityinfo exist lines 18]} e3
logit "hm_entityinfo exist lines 18 -> '$v' err=$e3"
# lines 的更多 dataname 尝试（mark 方式）
*createmark lines 1 18
foreach dn {points point1 point2 p1x p1y p1z p2x p2y p2z length area} {
  set v "?"
  catch {set v [hm_getvalue lines mark=1 dataname=$dn]} _
  logit "lines dn=$dn -> $v"
}
close $log
*quit 1

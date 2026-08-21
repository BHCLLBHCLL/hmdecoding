set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/synth_probe.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
proc mknode {x y z} {
  *createnode $x $y $z  0 0 0 0
  return [hm_latestentityid nodes]
}
proc mk {cfg} {
  global log
  set a [mknode 0 0 0]
  set b [mknode 1 0 0]
  set c [mknode 0 1 0]
  set d [mknode 0 0 1]
  *createlist nodes 1 $a $b $c $d
  catch {*createelement $cfg 1 1 1} er
  set eid ""
  catch {set eid [hm_latestentityid elems]} _
  set cfgback ""
  catch {set cfgback [hm_getvalue elements id=$eid dataname=config]} _
  logit "mk cfg=$cfg err=$er eid=$eid config_back=$cfgback"
}
mk 103
mk 204
mk 301
mk 304
# try hm_info elementtypes
set et ""
catch {set et [hm_info elementtypes]} e1
logit "hm_info elementtypes err=$e1 result=[string range $et 0 200]"
close $log
*quit 1

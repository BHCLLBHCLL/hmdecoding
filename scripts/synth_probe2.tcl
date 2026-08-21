set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/synth_probe2.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
proc mknode {x y z} {
  *createnode $x $y $z  0 0 0 0
  return [hm_latestentityid nodes]
}
set a [mknode 0 0 0]
set b [mknode 1 0 0]
set c [mknode 0 1 0]
set d [mknode 0 0 1]
set e [mknode 2 0 0]
set f [mknode 2 1 0]
# cfg 103 on 4 nodes
*createlist nodes 1 $a $b $c $d
catch {*createelement 103 1 1 1} er1
set e1 [hm_latestentityid elems]
# cfg 204 on 4 nodes
*createlist nodes 1 $a $b $c $d
catch {*createelement 204 1 1 1} er2
set e2 [hm_latestentityid elems]
# cfg 104 on 2 nodes
*createlist nodes 1 $a $b
catch {*createelement 104 1 1 1} er3
set e3 [hm_latestentityid elems]
logit "e1=$e1 err=$er1 cfg=[hm_getvalue elements id=$e1 dataname=config]"
logit "e2=$e2 err=$er2 cfg=[hm_getvalue elements id=$e2 dataname=config]"
logit "e3=$e3 err=$er3 cfg=[hm_getvalue elements id=$e3 dataname=config]"
foreach opt {configs elemconfigs elemtypes elementtype types} {
  set v ""
  set err ""
  catch {set v [hm_info $opt]} err
  logit "hm_info $opt err=$err val=[string range $v 0 120]"
}
catch {*writefile "D:/training/caedecoder/hmdecoding/output/ground_truth/synth_probe.fem" 1} wr
logit "writefile fem: $wr"
close $log
*quit 1

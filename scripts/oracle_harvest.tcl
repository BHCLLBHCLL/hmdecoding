# Batch ground-truth harvest over the 122-file tutorial corpus + repo sample.
# Writes a single delimited log; parsed by scripts/oracle_harvest.py into JSON.
set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/harvest.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
proc probe {path} {
  global log
  logit "==FILE== $path"
  catch {*readfile $path 1} rr
  logit "readfile: $rr"
  foreach ent {nodes elements comps mats props points lines surfaces solids systems groups loads} {
    set n -1
    catch {*createmark $ent 1 "all"} mk
    catch {set n [llength [hm_getmark $ent 1]]} e2
    logit "count $ent: $n"
  }
  set clist ""
  catch {*createmark comps 1 "all"} _
  catch {set clist [hm_getmark comps 1]} _
  foreach cid $clist {
    set nm "?"
    catch {set nm [hm_getvalue comps id=$cid dataname=name]} _
    logit "comp id=$cid name=$nm"
  }
  set mlist ""
  catch {*createmark mats 1 "all"} _
  catch {set mlist [hm_getmark mats 1]} _
  foreach mid $mlist {
    set nm "?"
    catch {set nm [hm_getvalue mats id=$mid dataname=name]} _
    logit "mat id=$mid name=$nm"
  }
  set plist ""
  catch {*createmark props 1 "all"} _
  catch {set plist [hm_getmark props 1]} _
  foreach pid $plist {
    set nm "?"
    catch {set nm [hm_getvalue props id=$pid dataname=name]} _
    logit "prop id=$pid name=$nm"
  }
  set elist ""
  catch {*createmark elements 1 "all"} _
  catch {set elist [hm_getmark elements 1]} _
  set total [llength $elist]
  logit "elements_total: $total"
  set cap 5000
  if {$total > $cap} {
    set elist [lrange $elist 0 [expr {$cap - 1}]]
    logit "config_sampled: $cap"
  } else {
    logit "config_sampled: $total"
  }
  foreach eid $elist {
    set cfg "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    logit "elem id=$eid config=$cfg"
  }
}
probe "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm"
set f [open "D:/training/caedecoder/hmdecoding/corpus/corpus_paths.txt" r]
while {[gets $f line] >= 0} {
  if {$line eq ""} {continue}
  probe $line
}
close $f
close $log
*quit 1

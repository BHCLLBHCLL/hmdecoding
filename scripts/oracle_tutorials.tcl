set log [open "D:/training/caedecoder/hmdecoding/output/oracle_tutorials.txt" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
proc probe_file {path tag} {
  global log
  logit "===== $tag $path"
  catch {*readfile $path 1} rerr
  logit "  readfile: $rerr"
  foreach ent {nodes elements comps mats props points lines surfaces solids} {
    set n -1
    catch {*createmark $ent 1 "all"} mk
    catch {set n [llength [hm_getmark $ent 1]]} e2
    logit "  $ent: $n"
  }
  set clist ""
  catch {*createmark comps 1 "all"} _
  catch {set clist [hm_getmark comps 1]} _
  foreach cid $clist {
    set nm "?"
    catch {set nm [hm_getvalue comps id=$cid dataname=name]} _
    logit "  comp id=$cid name=$nm"
  }
  # element config histogram (cap 5000)
  set elist ""
  catch {*createmark elements 1 "all"} _
  catch {set elist [hm_getmark elements 1]} _
  set hist ""
  set cnt 0
  foreach eid $elist {
    incr cnt
    if {$cnt > 5000} {break}
    set cfg "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    set hist [string map [list "$cfg " ""] " $hist$cfg "]
    lappend ::histlist($cfg) $eid
  }
  foreach cfg [lsort -integer [array names ::histlist]] {
    logit "  config $cfg: [llength $::histlist($cfg)] elements"
  }
  array unset ::histlist
}
probe_file "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" "REPO"
probe_file "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" "TUT-1D"
probe_file "C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm" "TUT-LEG"
close $log
*quit 1

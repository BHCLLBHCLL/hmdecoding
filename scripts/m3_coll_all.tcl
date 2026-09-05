set log [open "D:/training/caedecoder/hmdecoding/output/m3_coll_all.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm" 1
foreach ent {comps mats props groups loads systems} {
  *createmark $ent 1 "all"
  set ids [hm_getmark $ent 1]
  logit "== $ent [llength $ids] =="
  foreach id $ids {
    set nm "?"
    catch {set nm [hm_getvalue $ent id=$id dataname=name]} _
    logit "$ent $id $nm"
  }
}
close $log
*quit 1

# 面板级 oracle 骨架: 无头驱动示范面板 (nodes/translate/renumber)
# 用法: hmbatch -tcl panel_oracle.tcl  (panel 名由 output/panel_oracle.panel 传入)
set fp [open "D:/training/caedecoder/hmdecoding/output/panel_oracle.panel" r]
set panel [string trim [read $fp]]
close $fp
set log [open "D:/training/caedecoder/hmdecoding/output/panel_oracle.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1

*createmark nodes 1 "all"; set nb [llength [hm_getmark nodes 1]]
*createmark elems 1 "all"; set eb [llength [hm_getmark elems 1]]
logit "BEFORE nodes=$nb elems=$eb"

if {$panel == "nodes"} {
  *createnode 10.0 20.0 30.0 0
  *createmark nodes 1 "all"; set na [llength [hm_getmark nodes 1]]
  *createmark nodes 1 466
  set newx [hm_getvalue nodes id=466 dataname=x]
  logit "AFTER nodes=$na newid=466 newx=$newx"
} elseif {$panel == "translate"} {
  foreach nid {2 24 25} {
    set x [hm_getvalue nodes id=$nid dataname=x]
    logit "PRE nid=$nid x=$x"
  }
  *createmark nodes 1 2 24 25
  *movemark nodes 1 1 0 0
  foreach nid {2 24 25} {
    set x [hm_getvalue nodes id=$nid dataname=x]
    logit "POST nid=$nid x=$x"
  }
} elseif {$panel == "renumber"} {
  *createmark elems 1 "all"; set ids0 [hm_getmark elems 1]
  logit "PRE first_elems=[lrange $ids0 0 4]"
  *createmark elems 1 "all"
  *renumber elems 1 1 1
  *createmark elems 1 "all"; set ids1 [hm_getmark elems 1]
  logit "POST first_elems=[lrange $ids1 0 4]"
}
logit "DONE panel=$panel"
close $log
*quit 1

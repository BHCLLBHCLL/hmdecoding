
set f [open "output/ground_truth/multi_elem.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
foreach pth {
  "C:/Program Files/Altair/2019/tutorials/hm/bottle.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/clip_refine.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/frame_assembly.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/housing.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/head_2.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/fe_only.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/quality_index.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/s_bend_tube.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/yoke.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/propeller.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/dummy.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/molding1.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/truck.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/car_section.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/cover.hm"
  "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm"
} {
  set tag [file tail $pth]
  logit "===== $tag"
  catch {*readfile $pth 1} rerr
  logit "  read=$rerr"
  catch {*createmark elements 1 "all"} _
  set ids [hm_getmark elements 1]
  set n [llength $ids]
  logit "  count=$n first8=[lrange $ids 0 7]"
  foreach id [lrange $ids 0 4] {
    set cfg [hm_getvalue elements id=$id dataname=config]
    set nds ""
    foreach dn {node1 node2 node3 node4 node5 node6 node7 node8} {
        set v [hm_getvalue elements id=$id dataname=$dn]
        if {$v eq ""} { break }
        append nds " $v"
    }
    logit "  E $id cfg=$cfg nodes=$nds"
  }
}
close $f
*quit 1


set f [open "output/ground_truth/v17_nodes.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/dummy_positioner.hm" 1} rerr
logit "read: $rerr"
catch {*createmark nodes 1 "all"} _
set ids [hm_getmark nodes 1]
logit "nodes=[llength $ids] first5=[lrange $ids 0 4]"
foreach id [lrange $ids 0 4] {
    set x [hm_getvalue nodes id=$id dataname=x]
    set y [hm_getvalue nodes id=$id dataname=y]
    set z [hm_getvalue nodes id=$id dataname=z]
    logit "N $id $x $y $z"
}
catch {*createmark elements 1 "all"} _
set eids [hm_getmark elements 1]
logit "elems=[llength $eids] first5=[lrange $eids 0 4]"
close $f
*quit 1

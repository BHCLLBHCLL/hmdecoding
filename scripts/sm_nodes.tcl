
set f [open "output/ground_truth/sm_nodes.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm" 1} rerr
logit "read: $rerr"
*createmark nodes 1 "all"
logit "nodecount=[llength [hm_getmark nodes 1]]"
foreach id {1 2 3 48 34296} {
    set x [hm_getvalue nodes id=$id dataname=x]
    set y [hm_getvalue nodes id=$id dataname=y]
    set z [hm_getvalue nodes id=$id dataname=z]
    logit "N $id $x $y $z"
}
close $f
*quit 1

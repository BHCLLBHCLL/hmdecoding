set f [open "output/ground_truth/seat_nodes.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm" 1} rerr
logit "read: $rerr"
catch {*createmark nodes 1 "all"} _
set ids [hm_getmark nodes 1]
logit "nodes=[llength $ids]"
logit "max=[lindex [lsort -integer $ids] end]"
logit "has 1668: [expr {[lsearch -exact $ids 1668]>=0}]"
logit "has 1667: [expr {[lsearch -exact $ids 1667]>=0}]"
close $f
*quit 1
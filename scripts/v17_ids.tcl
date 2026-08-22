
set f [open "output/ground_truth/v17_ids.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/dummy_positioner.hm" 1} rerr
logit "read: $rerr"
catch {*createmark nodes 1 "all"} _
set ids [hm_getmark nodes 1]
set sorted [lsort -integer $ids]
logit "nodes=[llength $ids] min=[lindex $sorted 0] max=[lindex $sorted end]"
logit "mid5=[lrange $sorted 150000 150004]"
close $f
*quit 1

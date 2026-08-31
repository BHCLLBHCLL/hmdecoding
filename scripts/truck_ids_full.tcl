
set f [open "output/ground_truth/truck_ids_full.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/truck.hm" 1} rerr
logit "read: $rerr"
catch {*createmark elements 1 "all"} _
set ids [hm_getmark elements 1]
set sorted [lsort -integer $ids]
logit "elems=[llength $sorted] min=[lindex $sorted 0] max=[lindex $sorted end]"
foreach x $sorted { logit $x }
close $f
*quit 1

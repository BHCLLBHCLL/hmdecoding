set f [open "output/ground_truth/seat_start_nodes_all.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_start.hm" 1} rerr
puts $f "read: $rerr"
catch {*createmark nodes 1 "all"} _
set ids [hm_getmark nodes 1]
puts $f "count=[llength $ids]"
set s [lsort -integer $ids]
foreach id $s { puts $f $id }
close $f
*quit 1
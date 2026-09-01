set f [open "output/ground_truth/solid_nodes.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm" 1} rerr
logit "read: $rerr"
catch {*createmark nodes 1 "all"} _
set ids [hm_getmark nodes 1]
logit "nodes=[llength $ids] ids=$ids"
close $f
*quit 1
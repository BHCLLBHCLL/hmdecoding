
set f [open "output/ground_truth/truck_ids2.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/truck.hm" 1} rerr
logit "read: $rerr"
foreach probe {2000006 2000193 2213712 2213713 228633} {
    set hit [catch {hm_getvalue elements id=$probe dataname=config} res]
    logit "E$probe exists=$hit cfg=$res"
}
close $f
*quit 1

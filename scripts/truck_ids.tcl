
set f [open "output/ground_truth/truck_ids.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/truck.hm" 1} rerr
logit "read: $rerr"
catch {*createmark elements 1 "all"} _
set ids [hm_getmark elements 1]
logit "elems=[llength $ids]"
logit "min=[lindex [lsort -integer $ids] 0] max=[lindex [lsort -integer $ids] end]"
foreach probe {2212616 2213712 2215711 2214615} {
    set hit [catch {hm_getvalue elements id=$probe dataname=config} res]
    logit "E$probe exists=$hit cfg=$res"
}
close $f
*quit 1

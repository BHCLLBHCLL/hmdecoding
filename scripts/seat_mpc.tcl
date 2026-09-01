set f [open "output/ground_truth/seat_mpc.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm" 1} rerr
logit "read: $rerr"
catch {*createmark elements 1 "all"} _
set ids [hm_getmark elements 1]
logit "elems=[llength $ids]"
# list all config-55 elements (MPC) and high-eid
set mpc [list]
foreach id $ids {
    set cfg [hm_getvalue elements id=$id dataname=config]
    if {$cfg == 55 || $id > 1500} { lappend mpc [list $id $cfg] }
}
logit "cfg55_or_high=[llength $mpc]"
foreach pair $mpc {
    set id [lindex $pair 0]; set cfg [lindex $pair 1]
    set nds ""
    foreach dn {node1 node2 node3 node4 node5 node6 node7 node8 node9 node10 node11 node12 node13 node14 node15 node16 node17 node18 node19 node20} {
        set v [hm_getvalue elements id=$id dataname=$dn]
        if {$v eq ""} { break }
        append nds " $v"
    }
    logit "E id=$id cfg=$cfg nodes=$nds"
}
close $f
*quit 1

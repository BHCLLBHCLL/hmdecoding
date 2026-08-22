
set f [open "output/ground_truth/body_side_elem.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/body_side.hm" 1} rerr
logit "readfile: $rerr"
catch {*createmark elements 1 "all"} _
set ids [hm_getmark elements 1]
logit "count=[llength $ids] first20=[lrange $ids 0 19]"
foreach id [lrange $ids 0 19] {
    set cfg [hm_getvalue elements id=$id dataname=config]
    set nds ""
    foreach dn {node1 node2 node3 node4 node5 node6 node7 node8 node9 node10} {
        set v [hm_getvalue elements id=$id dataname=$dn]
        if {$v eq ""} { break }
        append nds " $v"
    }
    logit "E $id cfg=$cfg nodes=$nds"
}
close $f
*quit 1

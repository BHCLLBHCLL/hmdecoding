
set f [open "output/ground_truth/wing_mid.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/wing_section_complete.hm" 1} rerr
logit "read: $rerr"
foreach id {1739 1740 1741 1742 1818 1819} {
    set cfg [hm_getvalue elements id=$id dataname=config]
    set nds ""
    foreach dn {node1 node2 node3 node4 node5 node6 node7 node8} {
        set v [hm_getvalue elements id=$id dataname=$dn]
        if {$v eq ""} { break }
        append nds " $v"
    }
    logit "E $id cfg=$cfg nodes=$nds"
}
close $f
*quit 1

set f [open "output/ground_truth/seat2_elems_all.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm" 1} rerr
puts $f "read: $rerr"
catch {*createmark elements 1 "all"} _
set ids [hm_getmark elements 1]
puts $f "count=[llength $ids]"
foreach id $ids {
    set cfg [hm_getvalue elements id=$id dataname=config]
    set nds ""
    foreach dn {node1 node2 node3 node4 node5 node6 node7 node8 node9 node10 node11 node12} {
        set v [hm_getvalue elements id=$id dataname=$dn]
        if {$v eq ""} { break }
        append nds " $v"
    }
    puts $f "E $id cfg=$cfg nodes=$nds"
}
close $f
*quit 1
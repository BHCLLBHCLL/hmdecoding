# 查 molding1 元素 eid + nodes
set f [open "output/ground_truth/molding1_q.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/molding1.hm" 1} rr
puts $f "readfile: $rr"
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
puts $f "total: [llength $elist]"
set n 0
foreach eid $elist {
    if {$n >= 8} break
    set cfg "?"; set nds "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
    puts $f "E eid=$eid config=$cfg nodes=$nds"
    incr n
}
puts $f "first eid: [lindex $elist 0]  last: [lindex $elist end]"
close $f
*quit 1

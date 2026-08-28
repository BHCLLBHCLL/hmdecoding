# 查 wing_section_complete 元素 eid
set f [open "output/ground_truth/wing_eids.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/wing_section_complete.hm" 1} rr
puts $f "readfile: $rr"
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
puts $f "total: [llength $elist]"
set n 0
foreach eid $elist {
    if {$n >= 12} break
    set cfg "?"; set nds "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
    puts $f "E eid=$eid config=$cfg nodes=$nds"
    incr n
}
set last [lindex $elist end]
puts $f "last eid: $last"
close $f
*quit 1

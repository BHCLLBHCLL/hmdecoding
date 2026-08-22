# v17 导出全部缺失元素 (359) 的 config 与 nodes
set log [open "output/ground_truth/v17_missing_full.txt" w]
set count 0
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/dummy_positioner.hm" 1} rr
puts $log "readfile: $rr"
flush $log

# 4 个 ID 区间
set ranges [list {131508 131683} {131764 131767} {589001 589136} {589664 589706}]
foreach r $ranges {
    set a [lindex $r 0]
    set b [lindex $r 1]
    for {set eid $a} {$eid <= $b} {incr eid} {
        set cfg "?"
        set nds "?"
        catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
        catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
        puts $log "E eid=$eid config=$cfg nodes=$nds"
        incr count
    }
}
puts "exported $count elements"
close $log

# 验证 truck face 段 eid 是否存在
set f [open "output/ground_truth/truck_face_check.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/truck.hm" 1} rr
puts $f "readfile: $rr"
# 查重叠区段的 eid 是否存在
foreach eid {2000261 2000310 2000323 2000426 2000522 2000656 2000802 2000963 2000999} {
    set ok "?"
    catch {set ok [hm_getvalue elements id=$eid dataname=config]} _
    puts $f "eid=$eid config=$ok"
}
# 元素 eid 范围
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
puts $f "total: [llength $elist]"
puts $f "min: [lindex $elist 0]"
puts $f "max: [lindex $elist end]"
close $f
*quit 1

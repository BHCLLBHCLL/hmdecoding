# 导出 frame_assembly_1 元素 eid
set f [open "output/ground_truth/fa1_elemids.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/frame_assembly_1.hm" 1} rr
puts $f "readfile: $rr"
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
puts $f "total: [llength $elist]"
foreach eid $elist { puts $f $eid }
close $f
*quit 1

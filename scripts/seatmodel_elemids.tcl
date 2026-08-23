# 导出 SEAT_MODEL 元素 eid
set f [open "output/ground_truth/seatmodel_elemids.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm" 1} rr
puts $f "readfile: $rr"
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
puts $f "total: [llength $elist]"
foreach eid $elist {
    puts $f $eid
}
close $f
*quit 1

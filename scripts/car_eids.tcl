set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/car_eids.log" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/car_section.hm" 1} rr
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
puts $log "count=[llength $elist]"
foreach eid $elist {
  puts $log $eid
}
close $log
*quit 1

# v17 ground truth dump: full node/element ID lists for gap analysis.
proc dump_file {path tag} {
  set nf [open "output/ground_truth/v17gt_${tag}_nodeids.txt" w]
  set ef [open "output/ground_truth/v17gt_${tag}_elemids.txt" w]
  catch {*readfile $path 1} rr
  puts $nf "readfile: $rr"
  puts $ef "readfile: $rr"
  catch {*createmark nodes 1 "all"} _
  set nids [hm_getmark nodes 1]
  puts $nf "count [llength $nids]"
  foreach id [lsort -integer $nids] { puts $nf $id }
  catch {*createmark elements 1 "all"} _
  set eids [hm_getmark elements 1]
  puts $ef "count [llength $eids]"
  foreach id [lsort -integer $eids] { puts $ef $id }
  close $nf
  close $ef
}
dump_file "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/dummy_positioner.hm" dummy
dump_file "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_deformer.hm" seat
*quit 1

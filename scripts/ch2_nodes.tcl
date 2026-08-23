# 查 chapter2_2 节点
set f [open "output/ground_truth/ch2_nodes.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/chapter2_2.hm" 1} rr
puts $f "readfile: $rr"
set nlist ""
catch {*createmark nodes 1 "all"} _
catch {set nlist [hm_getmark nodes 1]} _
puts $f "total: [llength $nlist]"
set n 0
foreach nid $nlist {
    if {$n >= 5} break
    set x "?"; set y "?"; set z "?"
    catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
    catch {set y [hm_getvalue nodes id=$nid dataname=y]} _
    catch {set z [hm_getvalue nodes id=$nid dataname=z]} _
    puts $f "N nid=$nid x=$x y=$y z=$z"
    incr n
}
puts $f "first: [lindex $nlist 0] last: [lindex $nlist end]"
close $f
*quit 1

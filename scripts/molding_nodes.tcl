
set f [open "output/ground_truth/molding_nodes.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/molding1.hm" 1} rerr
logit "read: $rerr"
foreach id {1 2 3 4 5 100 7279} {
    set x [hm_getvalue nodes id=$id dataname=x]
    set y [hm_getvalue nodes id=$id dataname=y]
    set z [hm_getvalue nodes id=$id dataname=z]
    logit "N $id $x $y $z"
}
close $f
*quit 1


set f [open "output/ground_truth/mgr_ncoord.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/hm-ansys_contact_manager_2-d_tutorial.hm" 1} rerr
logit "read: $rerr"
foreach id {232 233 300 323 168 169} {
    set x [hm_getvalue nodes id=$id dataname=x]
    set y [hm_getvalue nodes id=$id dataname=y]
    set z [hm_getvalue nodes id=$id dataname=z]
    logit "N $id x=$x y=$y z=$z"
}
close $f
*quit 1

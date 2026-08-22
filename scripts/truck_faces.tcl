
set f [open "output/ground_truth/truck_faces.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/truck.hm" 1} rerr
logit "read: $rerr"
foreach ent {edges faces} {
    set n -1
    catch {*createmark $ent 1 "all"} _
    catch {set n [llength [hm_getmark $ent 1]]} _
    logit "$ent: $n"
}
# check element 2212616 one more time + a nearby id
foreach probe {2212616 2212620 228632 228631} {
    set hit [catch {hm_getvalue elements id=$probe dataname=config} res]
    logit "E$probe exists=$hit cfg=$res"
}
close $f
*quit 1

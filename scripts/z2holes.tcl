
set f [open "output/ground_truth/z2holes.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/2_holes.hm" 1} rerr
logit "read: $rerr"
foreach ent {nodes elements} {
    set n -1
    catch {*createmark $ent 1 "all"} _
    catch {set n [llength [hm_getmark $ent 1]]} _
    logit "$ent: $n"
}
close $f
*quit 1

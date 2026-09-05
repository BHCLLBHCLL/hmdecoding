set pf "output/m33_oracle.path"
set fp [open $pf r]
set hmfile [string trim [read $fp]]
close $fp
set outp "output/m33_oracle/[file tail $hmfile].oracle2.txt"
set f [open $outp w]
proc logit {msg} { global f; puts $f $msg; flush $f }
logit "FILE $hmfile"
catch {*readfile $hmfile 1} rerr
logit "read: $rerr"
foreach etype {curves surfaces contacts rigidwalls superelements equations ellipsoids mbplanes joints blocks tags loadsteps outputblocks} {
    if {[catch {*createmark $etype 1 all} me]} {
        logit "== $etype MARK-ERR =="
        continue
    }
    if {[catch {set ids [hm_getmark $etype 1]} err]} {
        logit "== $etype GETMARK-ERR =="
        continue
    }
    logit "== $etype [llength $ids] =="
    foreach id [lsort -integer -unique $ids] {
        if {[catch {set nm [hm_getentityvalue $etype $id "name" "" -byid]} e2]} { set nm "?" }
        logit "$etype $id $nm"
    }
}
close $f
*quit 1

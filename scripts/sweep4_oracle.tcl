set logf [open "D:/training/caedecoder/hmdecoding/output/sweep4_oracle.log" w]
proc logit {msg} { global logf; puts $logf $msg; flush $logf }

set fh [open "D:/training/caedecoder/hmdecoding/output/sweep4_files.txt" r]
set ents {nodes elems comps mats props loads loadcols systems groups sets points lines surfs solids titles}
set n 0
while {[gets $fh f] >= 0} {
  if {$f eq ""} { continue }
  incr n
  set bname [file tail $f]
  if {[catch {*readfile $f 1} res]} {
    logit "== $bname | READ-ERR | $res"
    logit "   $f"
    continue
  }
  set line "== $bname | OK"
  foreach ent $ents {
    set cnt -1
    if {[catch {*createmark $ent 1 "all"} _] == 0} {
      if {[catch {set ids [hm_getmark $ent 1]} _] == 0} {
        set cnt [llength $ids]
      }
    }
    append line " | $ent=$cnt"
  }
  logit $line
  if {$n % 20 == 0} { logit "-- progress $n" }
}
close $fh
logit "DONE $n files"
close $logf
*quit 1

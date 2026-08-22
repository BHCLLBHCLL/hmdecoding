set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/geom_probe.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
proc save {name} {
  set w ""
  catch {*writefile "D:/training/caedecoder/hmdecoding/corpus/synthetic/$name.hm" 1} w
  logit "saved $name write=$w"
}
save "v1913_geom00_empty"
catch {*createpoint 1 2 3} e1
logit "createpoint 1 2 3: $e1"
save "v1913_geom01_p1"
catch {*createpoint 4 5 6} e2
logit "createpoint 4 5 6: $e2"
save "v1913_geom02_p2"
catch {*createline 1 2} e3
logit "createline 1 2: $e3"
save "v1913_geom03_l1"
close $log
*quit 1

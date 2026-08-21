# Synthetic corpus generator: cumulative model chain, each step +1 entity type.
# Writes v19.13-format .hm files into corpus/synthetic/ for differential analysis.
set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/synth_gen.log" w]
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
proc mknode {x y z} {
  *createnode $x $y $z  0 0 0 0
  return [hm_latestentityid nodes]
}
# 0) empty default state
save "v1913_00_empty"
# 1) one node
mknode 1 2 3
save "v1913_01_n1"
# 2) four nodes (cumulative: nodes 1..4)
mknode 10 0 0
mknode 0 10 0
mknode 0 0 10
save "v1913_02_n4a"
save "v1913_02_n4b"
# 3) one tetra4 (cfg 103)
*createlist nodes 1 1 2 3 4
catch {*createelement 103 1 1 1} e1
logit "elem1 err=$e1"
save "v1913_03_t1"
# 4) second tetra + fifth node
mknode 5 5 5
*createlist nodes 1 2 3 4 5
catch {*createelement 103 1 1 1} e2
logit "elem2 err=$e2"
save "v1913_04_t2"
# 5) named component
catch {*createcollector comps 2 "c2" 2} ce
logit "collector err=$ce"
save "v1913_05_c2"
# 6) one more collector
catch {*createcollector comps 3 "c3" 3} ce2
logit "collector2 err=$ce2"
save "v1913_06_c3"
close $log
*quit 1

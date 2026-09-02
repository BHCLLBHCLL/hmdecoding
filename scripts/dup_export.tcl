# dup_export.tcl — 用父目录前缀避免同名覆盖; 路径+输出名经环境变量
set path $::env(HMEXPORT_PATH)
set out $::env(HMEXPORT_OUT)
catch {*readfile $path 1} rr
catch {*createmark elements 1 "all"} _
set ids [hm_getmark elements 1]
set of [open $out w]
set n [llength $ids]
puts $of "count=$n"
foreach id $ids {
  set cfg [hm_getvalue elements id=$id dataname=config]
  set nds ""
  foreach dn {node1 node2 node3 node4 node5 node6 node7 node8 node9 node10 node11 node12 node13 node14 node15 node16} {
    set v [hm_getvalue elements id=$id dataname=$dn]
    if {$v eq ""} { break }
    append nds " $v"
  }
  puts $of "E $id cfg=$cfg nodes=$nds"
}
close $of
puts "DONE"
*quit 1
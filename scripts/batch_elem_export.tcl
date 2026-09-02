# batch_elem_export.tcl — 批量导出元素列表 (eid/config/nodes) 到独立 txt
# 用法: hmbatch -tcl batch_elem_export.tcl <路径列表文件> <输出目录> <起始行> <结束行>
set plist [lindex $argv 0]
set outdir [lindex $argv 1]
set from [lindex $argv 2]
set to   [lindex $argv 3]
set f [open $plist r]
set lines {}
while {[gets $f line] >= 0} {
  if {$line ne ""} { lappend lines $line }
}
close $f
set idx 0
foreach path $lines {
  if {$idx < $from || ($to != "" && $idx >= $to)} { incr idx; continue }
  incr idx
  set base [file tail $path]
  set out [file join $outdir "${base}.elems.txt"]
  set of [open $out w]
  puts $of "file: $path"
  catch {*readfile $path 1} rr
  puts $of "read: $rr"
  catch {*createmark elements 1 "all"} _
  set ids [hm_getmark elements 1]
  puts $of "count=[llength $ids]"
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
  puts "DONE $base elements=[llength $ids]"
}
*quit 1
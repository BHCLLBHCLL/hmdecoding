# 严格关联语法测试矩阵: 每次查询前 unset 结果变量, 避免残留误判.
# 对每个 (源实体, 目标实体, 关联方法) 组合, 用若干样本 id 测试, 统计命中率.
set log [open "output/ground_truth/m4_assoc_matrix.log" w]
proc logit {m} { global log; puts $log $m; flush $log }

# 干净查询: 失败返回 "" 且不留残值
proc assoc {tgt method srcs} {
  # HyperMesh 仅保证 mark 1/2 有效; 高级 mark id 会静默失败
  catch {*createmark $tgt 2 $method $srcs} err
  set r ""
  if {[catch {set r [hm_getmark $tgt 2]} e2]} { return "" }
  return $r
}

set fp ""
catch {set f [open "output/m4_geom.path" r]; set fp [string trim [read $f]]; close $f}
catch {*readfile $fp 1} _
logit "FILE $fp"

# 采集各实体 id 样本
proc ids_of {ent} {
  catch {*createmark $ent 1 "all"} _
  set r ""; catch {set r [hm_getmark $ent 1]} _
  return $r
}
set P [ids_of points]; set L [ids_of lines]
set S [ids_of surfaces]; set SO [ids_of solids]
logit "counts: P=[llength $P] L=[llength $L] S=[llength $S] SO=[llength $SO]"

# 测试矩阵: {目标实体 方法 源实体列表 源实体名}
set tests {}
lappend tests [list points "by lines"    $L lines]
lappend tests [list points "by surfaces"  $S surfaces]
lappend tests [list points "by solids"    $SO solids]
lappend tests [list lines  "by surfaces"  $S surfaces]
lappend tests [list lines  "by solids"    $SO solids]
lappend tests [list lines  "by points"    $P points]
lappend tests [list surfaces "by lines"   $L lines]
lappend tests [list surfaces "by solids"  $SO solids]
lappend tests [list surfaces "by points"  $P points]
lappend tests [list solids  "by surfaces" $S surfaces]
lappend tests [list solids  "by lines"    $L lines]

foreach t $tests {
  set tgt [lindex $t 0]; set meth [lindex $t 1]
  set srcs [lindex $t 2]; set srcname [lindex $t 3]
  set ns [llength $srcs]
  if {$ns == 0} { logit "SKIP $tgt <- $meth ($srcname): no source entities"; continue }
  set samples [expr {$ns > 8 ? 8 : $ns}]
  set hit 0; set total 0; set ex ""
  for {set i 0} {$i < $samples} {incr i} {
    set sid [lindex $srcs $i]
    set r [assoc $tgt $meth [list $sid]]
    incr total
    if {$r ne ""} { incr hit; if {$ex eq ""} {set ex "src=$sid -> $r"} }
  }
  logit "RESULT $tgt <- \"$meth\" ($srcname): hit=$hit/$total  ex: $ex"
}
close $log
exit 0

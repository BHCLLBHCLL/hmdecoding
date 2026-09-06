# M4 语法试探 v2: 专攻 surface -> lines 边界拓扑 (多文件 / 多变体).
# 输入: output/m4_geom.path   输出: output/ground_truth/m4_syntax_probe2.log
set log [open "output/ground_truth/m4_syntax_probe2.log" a]
proc logit {msg} { global log; puts $log $msg; flush $log }

set fp ""
catch {set f [open "output/m4_geom.path" r]; set fp [string trim [read $f]]; close $f}
catch {*readfile $fp 1} rr
logit "==FILE== $fp readfile=$rr"

catch {*createmark surfaces 1 "all"} _
set sids [hm_getmark surfaces 1]
catch {*createmark lines 1 "all"} _
set lids [hm_getmark lines 1]
logit "nS=[llength $sids] nL=[llength $lids]"

# 对前 N 个 surface 逐个试探多种变体, 记录首个非空者
set tried 0
foreach sid $sids {
  if {$tried >= 5} break
  incr tried
  foreach variant {
    {*createmark lines 2 "by surfaces" [list $sid]}
    {*createmark lines 2 "by surface" [list $sid]}
    {*createmark lines 2 "on surface" [list $sid]}
    {*createmark lines 2 "by surfs" [list $sid]}
    {*createmark lines 2 "by faces" [list $sid]}
    {*createmark lines 2 "attached" [list $sid]}
    {*createmark lines 2 "by surfaces" $sid}
    {*createmark lines 2 "by adjacent surfaces" [list $sid]}
  } {
    if {![catch {eval $variant} e]} {
      catch {set m [hm_getmark lines 2]} _
      if {[info exists m] && $m ne ""} {
        logit "   sid=$sid HIT [lindex $variant 2] -> $m"
        unset m
        break
      }
      catch {unset m}
    }
  }
}
# 反向: lines -> surfaces (线属于哪些面)
set tried 0
foreach lid $lids {
  if {$tried >= 5} break
  incr tried
  foreach variant {
    {*createmark surfaces 2 "by lines" [list $lid]}
    {*createmark surfaces 2 "by line" [list $lid]}
    {*createmark surfaces 2 "on line" [list $lid]}
  } {
    if {![catch {eval $variant} e]} {
      catch {set m [hm_getmark surfaces 2]} _
      if {[info exists m] && $m ne ""} {
        logit "   lid=$lid REV-HIT [lindex $variant 2] -> $m"
        unset m
        break
      }
      catch {unset m}
    }
  }
}
# 面/线自身属性: 用 hm_getvalue 数字 dataname 扫描
if {[llength $sids] > 0} {
  set sid [lindex $sids 0]
  for {set d 1} {$d <= 24} {incr d} {
    if {![catch {set v [hm_getvalue surfaces id=$sid dataname=$d]} e]} {
      if {$v ne ""} { logit "   surf dataname=$d -> $v" }
    }
  }
}
close $log
exit 0

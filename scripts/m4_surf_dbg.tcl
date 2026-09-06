# 诊断: surfaces -> lines 在有无前置采集两种情况下的差异
set log [open "output/ground_truth/m4_surf_dbg.log" w]
proc logit {m} { global log; puts $log $m; flush $log }
proc markget {ent sel} {
  catch {*createmark $ent 2 {*}$sel} _
  set r ""; catch {set r [hm_getmark $ent 2]} _
  return $r
}
set fp ""
catch {set f [open "output/m4_geom.path" r]; set fp [string trim [read $f]]; close $f}
catch {*readfile $fp 1} _
logit "FILE $fp"

# --- 情形 1: 直接查 (无前置) ---
set sids [markget surfaces "all"]
set s1 [lindex $sids 0]
set r1 [markget lines [list "by surfaces" [list $s1]]]
logit "CASE1 (direct)     sid=$s1 -> $r1"

# --- 情形 1b: 带错误捕获的直接 eval ---
if {[catch {*createmark lines 2 "by surfaces" [list $s1]} err]} {
  logit "CASE1b eval ERR: $err"
} else {
  logit "CASE1b eval OK -> [hm_getmark lines 2]"
}

# --- 情形 2: 先跑一轮 lines->points 再查 ---
set lids [markget lines "all"]
set l1 [lindex $lids 0]
set rp [markget points [list "by lines" [list $l1]]]
logit "CASE2 pre lines->points lid=$l1 -> $rp"
set r2 [markget lines [list "by surfaces" [list $s1]]]
logit "CASE2 (after lines)  sid=$s1 -> $r2"

# --- 情形 3: 先查 points 坐标再查 ---
catch {set px [hm_getvalue points id=[lindex [markget points "all"] 0] dataname=x]} _
logit "CASE3 pre point x=$px"
set r3 [markget lines [list "by surfaces" [list $s1]]]
logit "CASE3 (after points) sid=$s1 -> $r3"

# --- 情形 4: 用 mark 3 试 ---
catch {*createmark lines 3 "by surfaces" [list $s1]} e4
logit "CASE4 mark3 -> [hm_getmark lines 3]  err=$e4"

# --- 情形 5: 换实体顺序 (先 createmark all 再 by surfaces) ---
catch {*createmark lines 4 "all"} _
catch {*createmark lines 4 "by surfaces" [list $s1]} e5
logit "CASE5 mark4(all then by) -> [hm_getmark lines 4] err=$e5"
close $log
exit 0

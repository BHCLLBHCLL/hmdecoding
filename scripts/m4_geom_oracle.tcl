# M4 几何实体 oracle 采集 (v2): 一次 hmbatch 会话批量采集多文件的完整 BREP 真值.
#
# 关联语法实测结论 (mark 必须为 1/2; 高级 mark id 静默失败):
#   points   <- "by lines"    OK   线端点
#   surfaces <- "by lines"    OK   线所属的面 (相邻面共享边)
#   lines    <- "by points"   OK   点上的线
#   surfaces <- "by solids"   OK   体的面
#   solids   <- "by surfaces" OK   面所属的体
#   points   <- "by surfaces" 不支持
#   lines    <- "by surfaces" 不支持  -> 面边界线改用反向构建: 遍历所有线,
#                                        用 "surfaces by lines" 累加反建 surf->lines
#
# 输入: output/m4_geom_files.txt (每行一个 .hm 绝对路径)
# 输出: output/ground_truth/m4_geom_oracle.log (追加)
proc logit {msg} { global log; puts $log $msg; flush $log }

set log [open "output/ground_truth/m4_geom_oracle.log" a]

set paths {}
if {[catch {set f [open "output/m4_geom_files.txt" r]; set paths [split [string trim [read $f]] "\n"]; close $f}]} {
  logit "ERROR: cannot read output/m4_geom_files.txt"; close $log; exit 1
}

proc reset_model {} {
  catch {*newmodel} _
  catch {*clearmodel} _
}

# 干净关联查询: 成功返回 id 列表, 失败返回空串 (不留残值)
proc assoc {tgt method srcs} {
  catch {*createmark $tgt 2 $method $srcs} _
  set r ""
  catch {set r [hm_getmark $tgt 2]} _
  return $r
}
proc ids_of {ent} {
  catch {*createmark $ent 1 "all"} _
  set r ""; catch {set r [hm_getmark $ent 1]} _
  return $r
}

foreach fp0 $paths {
  set fp [string trim $fp0]
  if {$fp eq ""} { continue }
  reset_model
  logit "==FILE== $fp"
  if {[catch {*readfile $fp 1} rr]} {
    logit "readfile: ERR $rr"; logit "==ENDFILE=="; continue
  }
  logit "readfile: $rr"

  set P [ids_of points]; set L [ids_of lines]
  set S [ids_of surfaces]; set SO [ids_of solids]
  logit "count points: [llength $P]"
  logit "count lines: [llength $L]"
  logit "count surfaces: [llength $S]"
  logit "count solids: [llength $SO]"

  # --- points: 坐标 ---
  foreach pid $P {
    set x ""; set y ""; set z ""
    catch {set x [hm_getvalue points id=$pid dataname=x]} _
    catch {set y [hm_getvalue points id=$pid dataname=y]} _
    catch {set z [hm_getvalue points id=$pid dataname=z]} _
    logit "point id=$pid x=$x y=$y z=$z"
  }

  # --- lines: 端点 points (正向: points by lines) ---
  foreach lid $L {
    logit "line id=$lid pts=[assoc points "by lines" [list $lid]]"
  }

  # --- surfaces: 边界 lines (反向构建: surfaces by lines 累加) ---
  array unset s2l
  foreach lid $L {
    foreach sid [assoc surfaces "by lines" [list $lid]] {
      lappend s2l($sid) $lid
    }
  }
  foreach sid $S {
    set ls ""
    if {[info exists s2l($sid)]} { set ls $s2l($sid) }
    logit "surf id=$sid lines=$ls"
  }
  array unset s2l

  # --- solids: 面 (正向: surfaces by solids) ---
  foreach soid $SO {
    logit "solid id=$soid surfs=[assoc surfaces "by solids" [list $soid]]"
  }

  logit "==ENDFILE=="
}
close $log
exit 0

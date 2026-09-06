# M4 几何实体探针 v2:
#   1) 用 mark 关联语法采集拓扑 (points by lines / lines by surfaces / surfaces by solids)
#   2) 试探 dataname 并记录 catch 错误信息, 用于发现正确字段名
# 输入: output/m4_geom.path   输出: output/ground_truth/m4_geom_probe.log
set log [open "output/ground_truth/m4_geom_probe.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
proc mark_ids {ent sel} {
  catch {*createmark $ent 1 $sel} _
  set ids ""
  catch {set ids [hm_getmark $ent 1]} _
  return $ids
}

set fp ""
if {[catch {set f [open "output/m4_geom.path" r]; set fp [string trim [read $f]]; close $f}]} {
  logit "ERROR: cannot read output/m4_geom.path"; close $log; exit 1
}
logit "==FILE== $fp"
catch {*readfile $fp 1} rr
logit "readfile: $rr"

foreach ent {points lines surfaces solids} {
  set ids [mark_ids $ent "all"]
  logit "-- entity=$ent count=[llength $ids] ids=$ids"
}

# --- dataname 试探 (带错误信息) ---
set pids [mark_ids points "all"]
if {[llength $pids] > 0} {
  set pid [lindex $pids 0]
  foreach dn {x y z name color comp} {
    if {[catch {set v [hm_getvalue points id=$pid dataname=$dn]} e]} {
      logit "   points dn=$dn ERR: $e"
    } else {
      logit "   points dn=$dn OK: $v"
    }
  }
}
set lids [mark_ids lines "all"]
if {[llength $lids] > 0} {
  set lid [lindex $lids 0]
  foreach dn {points point1 point2 nodes length name color comp type} {
    if {[catch {set v [hm_getvalue lines id=$lid dataname=$dn]} e]} {
      logit "   lines dn=$dn ERR: $e"
    } else {
      logit "   lines dn=$dn OK: $v"
    }
  }
  # 关联语法: 线上的点
  set assoc [mark_ids points "by lines $lid"]
  logit "   ASSOC points by lines $lid -> $assoc"
}
set sids [mark_ids surfaces "all"]
if {[llength $sids] > 0} {
  set sid [lindex $sids 0]
  foreach dn {lines area name color comp type} {
    if {[catch {set v [hm_getvalue surfaces id=$sid dataname=$dn]} e]} {
      logit "   surfaces dn=$dn ERR: $e"
    } else {
      logit "   surfaces dn=$dn OK: $v"
    }
  }
  set assoc [mark_ids lines "by surfaces $sid"]
  logit "   ASSOC lines by surfaces $sid -> $assoc"
  set assoc2 [mark_ids points "by surfaces $sid"]
  logit "   ASSOC points by surfaces $sid -> $assoc2"
}
set soids [mark_ids solids "all"]
if {[llength $soids] > 0} {
  set soid [lindex $soids 0]
  foreach dn {surfaces volume name color comp type} {
    if {[catch {set v [hm_getvalue solids id=$soid dataname=$dn]} e]} {
      logit "   solids dn=$dn ERR: $e"
    } else {
      logit "   solids dn=$dn OK: $v"
    }
  }
  set assoc [mark_ids surfaces "by solids $soid"]
  logit "   ASSOC surfaces by solids $soid -> $assoc"
}
close $log
exit 0

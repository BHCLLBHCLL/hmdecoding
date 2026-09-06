# M4 语法试探: 批量验证几何拓扑查询的可用接口 (关联选择 / Ext API / 专用查询命令).
# 只输出成功的语法, 供后续 oracle 采集选用.
# 输入: output/m4_geom.path   输出: output/ground_truth/m4_syntax_probe.log
set log [open "output/ground_truth/m4_syntax_probe.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
proc try {label script} {
  global log
  if {[catch {uplevel 1 $script} err]} {
    logit "FAIL $label :: $err"
    return ""
  }
  set r [uplevel 1 $script]
  logit "OK   $label :: $r"
  return $r
}

set fp ""
catch {set f [open "output/m4_geom.path" r]; set fp [string trim [read $f]]; close $f}
logit "==FILE== $fp"
catch {*readfile $fp 1} rr
logit "readfile: $rr"

# 取第一个有实体可参考的 id
catch {*createmark lines 1 "all"} _
set lids [hm_getmark lines 1]
set L1 [lindex $lids 0]
catch {*createmark surfaces 1 "all"} _
set sids [hm_getmark surfaces 1]
set S1 [lindex $sids 0]
catch {*createmark solids 1 "all"} _
set soids [hm_getmark solids 1]
set SO1 [lindex $soids 0]
catch {*createmark points 1 "all"} _
set pids [hm_getmark points 1]
set P1 [lindex $pids 0]
logit "refs: L1=$L1 S1=$S1 SO1=$SO1 P1=$P1  (nL=[llength $lids] nS=[llength $sids] nSO=[llength $soids] nP=[llength $pids])"

# --- 1. 关联选择语法 (多种变体) ---
if {$L1 ne ""} {
  try {A1 points by-lines-plain} {*createmark points 2 "by lines $L1"; hm_getmark points 2}
  try {A2 points by-lines-brace} {*createmark points 2 "by lines" [list $L1]; hm_getmark points 2}
  try {A3 points on-line}        {*createmark points 2 "on line $L1"; hm_getmark points 2}
  try {A4 lines by-points}       {*createmark points 2 "by id $P1"; *createmark lines 2 "by points"; hm_getmark lines 2}
}
if {$S1 ne ""} {
  try {B1 lines by-surfaces-plain} {*createmark lines 2 "by surfaces $S1"; hm_getmark lines 2}
  try {B2 lines by-surfaces-brace} {*createmark lines 2 "by surfaces" [list $S1]; hm_getmark lines 2}
  try {B3 points by-surfaces}      {*createmark points 2 "by surfaces" [list $S1]; hm_getmark points 2}
  try {B4 surfaces by-lines}       {*createmark lines 2 "by id $L1"; *createmark surfaces 2 "by lines"; hm_getmark surfaces 2}
}
if {$SO1 ne ""} {
  try {C1 surfaces by-solids} {*createmark surfaces 2 "by solids" [list $SO1]; hm_getmark surfaces 2}
  try {C2 solids by-surfaces} {*createmark surfaces 2 "by id $S1"; *createmark solids 2 "by surfaces"; hm_getmark solids 2}
}

# --- 2. Ext API 几何拓扑 (若 hmbatch 可用) ---
if {$L1 ne ""} {
  try {D1 extapi-line-points} {hm_extapigeomlinegetpoints $L1}
  try {D2 extapi-line-coedges} {hm_extapigeomlinegetcoedges $L1}
}
if {$S1 ne ""} {
  try {D3 extapi-surf-coedges} {hm_extapigeomfacegetcoedges $S1}
}

# --- 3. 专用查询命令 ---
if {$L1 ne ""} {
  try {E1 hm_getlinepoints}   {hm_getlinepoints $L1}
  try {E2 hm_getlineendpoints} {hm_getlineendpoints $L1}
}
# --- 4. 数值 dataname id 扫描 (lines 的 dataname 可能用数字 id) ---
if {$L1 ne ""} {
  logit "-- numeric dataname scan for lines id=$L1"
  for {set d 1} {$d <= 40} {incr d} {
    if {![catch {set v [hm_getvalue lines id=$L1 dataname=$d]} e]} {
      if {$v ne ""} { logit "   lines dataname=$d -> $v" }
    }
  }
}
# --- 5. hm_info / 元查询 ---
try {F1 hm_info-datanames} {hm_info -datanames lines}
try {F2 hm_getvaluedatanames} {hm_getvaluedatanames lines}
try {F3 hm_entityinfo} {hm_entityinfo lines}

close $log
exit 0

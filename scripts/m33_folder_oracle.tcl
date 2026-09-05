# M3.3 验收门禁: HM 侧 Model Browser 逐文件夹 oracle 探针
# 用法: hmbatch.exe -tcl m33_folder_oracle.tcl  (hm 路径由 output/m33_oracle.path 传入)
set pf "output/m33_oracle.path"
set fp [open $pf r]
set hmfile [string trim [read $fp]]
close $fp

set outp "output/m33_oracle/[file tail $hmfile].oracle.txt"
set f [open $outp w]
proc logit {msg} { global f; puts $f $msg; flush $f }

logit "FILE $hmfile"
catch {*readfile $hmfile 1} rerr
logit "read: $rerr"

# Model Browser 文件夹 -> HM 实体类型 (TCL 名)
foreach etype {components mats props groups sets loadcols assemblies systems vectors titles blocks connectors} {
    if {[catch {*createmark $etype 1 all} me]} {
        logit "== $etype MARK-ERR $me =="
        continue
    }
    if {[catch {set ids [hm_getmark $etype 1]} err]} {
        logit "== $etype GETMARK-ERR $err =="
        continue
    }
    logit "== $etype [llength $ids] =="
    foreach id [lsort -integer -unique $ids] {
        if {[catch {set nm [hm_getentityvalue $etype $id "name" "" -byid]} e2]} {
            set nm "?$e2"
        }
        logit "$etype $id $nm"
    }
}
close $f
*quit 1

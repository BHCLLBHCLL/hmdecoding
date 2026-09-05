set pf "output/m33_oracle.path"
set fp [open $pf r]
set hmfile [string trim [read $fp]]
close $fp
set outp "output/m33_oracle/[file tail $hmfile].idprobe.txt"
set f [open $outp w]
catch {*readfile $hmfile 1} rerr
foreach etype {sets loadcols rigidwalls curves airbags seatbelts contacts groups tags blocks titles vectors systems assemblies components mats props surfaces} {
    foreach id {2000010 2000020 2000030 2000046 3 4} {
        if {[catch {*createmark $etype 1 $id} err]} { continue }
        if {[catch {set ids [hm_getmark $etype 1]} err]} { continue }
        if {[lsearch -exact $ids $id] >= 0} {
            if {[catch {set nm [hm_getentityvalue $etype $id "name" "" -byid]} e2]} { set nm "?" }
            puts $f "EXISTS $etype $id '$nm'"
        }
    }
}
close $f
*quit 1

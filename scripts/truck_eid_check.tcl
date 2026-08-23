# 查 truck eid 2000001-2000012 是否存在 + nodes
set f [open "output/ground_truth/truck_eid_check.txt" w]
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/truck.hm" 1} rr
puts $f "readfile: $rr"
foreach eid {2000001 2000002 2000006 2000007 2000008 2000009 2000010 2000011 2000012} {
    set cfg "?"; set nds "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
    puts $f "E eid=$eid config=$cfg nodes=$nds"
}
# 2314 附近 eid 检查
foreach eid {2314 2315 2320 38653} {
    set cfg "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    puts $f "E2 eid=$eid config=$cfg"
}
close $f
*quit 1

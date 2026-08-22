set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/gt_extended.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
proc probe_file {path} {
  global log
  logit "==FILE== $path"
  catch {*readfile $path 1} rr
  foreach ent {comps mats props systems groups loads assemblies} {
    set n -1
    catch {*createmark $ent 1 "all"} mk
    catch {set n [llength [hm_getmark $ent 1]]} e2
    logit "count $ent: $n"
    if {$n > 0 && $n < 200} {
      set idlist ""
      catch {set idlist [hm_getmark $ent 1]} _
      foreach id $idlist {
        set nm "?"
        catch {set nm [hm_getvalue $ent id=$id dataname=name]} _
        logit "  $ent id=$id name=$nm"
      }
    }
  }
}
probe_file "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm"
probe_file "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm"
probe_file "C:/Program Files/Altair/2019/tutorials/hm/spring.hm"
probe_file "C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm"
probe_file "C:/Program Files/Altair/2019/tutorials/hm/bumper.hm"
probe_file "C:/Program Files/Altair/2019/tutorials/hm/frame_assembly.hm"
close $log
*quit 1

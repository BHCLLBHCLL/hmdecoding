$todo = Get-Content 'output/ground_truth/paths_todo.txt'
$outdir = 'D:/training/caedecoder/hmdecoding/output/ground_truth/elems'
$hm = 'C:\Program Files\Altair\2019\hm\bin\win64\hmbatch.exe'
$i = 0
foreach ($p in $todo) {
  $b = Split-Path $p -Leaf
  $out = Join-Path $outdir ($b + '.elems.txt')
  if (Test-Path $out) { $i++; continue }
  $env:HMEXPORT_PATH = $p
  $env:HMEXPORT_OUT = $out
  & $hm -tcl 'scripts/single_elem_export.tcl' 2>&1 | Out-Null
  $i++
  if ($i % 5 -eq 0) { Write-Output "progress $i" }
}
Write-Output "ALL DONE $i files"
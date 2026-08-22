
import re, html, glob, os
os.makedirs("output/ground_truth/help_entities", exist_ok=True)
src = r"C:/Program Files/Altair/2019/help/hm/topics/pre_processing/entities"
outdir = "output/ground_truth/help_entities"
for f in glob.glob(os.path.join(src, "*.htm*")):
    name = os.path.basename(f)
    raw = open(f, encoding="utf-8", errors="ignore").read()
    raw = re.sub(r"<script.*?</script>", " ", raw, flags=re.S)
    raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", raw)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    txt = re.sub(r"\s*\n\s*", "\n", txt).strip()
    open(os.path.join(outdir, name + ".txt"), "w", encoding="utf-8").write(txt)
print("converted:", len(glob.glob(os.path.join(src, "*.htm*"))))

import json
rows = json.load(open("corpus/corpus_index.json", encoding="utf-8"))
with open("corpus/corpus_paths.txt", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(r["abs"].replace("/", "\\") + "\n")
print("paths written:", len(rows))

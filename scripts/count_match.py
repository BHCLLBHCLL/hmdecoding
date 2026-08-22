import json
d = json.load(open("output/ground_truth/ws_pt_positions.json"))
print("matched points:", len(d))
print("sample:", list(d.items())[:5])

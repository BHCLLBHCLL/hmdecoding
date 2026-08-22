def iges_line_entities():
    lines = []
    def add(section_char, seq, text):
        for i in range(0, len(text), 72):
            chunk = text[i:i+72]
            lines.append((chunk.ljust(72) + section_char + str(seq).rjust(7)))
            seq += 1
        return seq
    seq = add("S", 1, "MINIMAL IGES: 2 POINTS + 1 LINE")
    g = "1H,,1H;,4H    ,,8HMINIMAL,32,38,64,6,99,2,2Hmm,1.0,1.0,15H20260101.000000,1.0E-06,1.0E+07,8Hhmdecode,8Hhmdecode,8H2019.0.0,1.0E-06,8Hminimal,1,1,15H20260101.000000,15H20260101.000000;"
    seq = add("G", seq, g)
    dstart = seq
    entities = [(116, 1, 1, "P1"), (116, 2, 1, "P2"), (110, 3, 1, "L1")]
    pd = 1
    for typ, pptr, plines, label in entities:
        r1 = f"{typ:>8}{pd:>8}{0:>8}{0:>8}{1:>8}{0:>8}{0:>8}{0:>8}{0:>8}"
        r2 = f"{typ:>8}{1:>8}{1:>8}{plines:>8}{0:>8}{0:>8}{0:>8}{label:>8}{0:>8}"
        seq = add("D", seq, r1)
        seq = add("D", seq, r2)
        pd += plines
    pstart = seq
    for p in ["0.,0.,0.;", "10.,0.,0.;", "0.,0.,0.,10.,0.,0.;"]:
        seq = add("P", seq, p)
    t = f"S{1:>7}G{2:>7}D{dstart-1:>7}P{pstart-1:>7}      T{1:>7}"
    lines.append((t.ljust(72) + "T" + str(seq).rjust(7)))
    return "\n".join(l[0] for l in lines)

data = iges_line_entities()
with open("corpus/synthetic/minimal.iges", "w") as f:
    f.write(data)
print("IGES written, lines:", len(data.splitlines()))

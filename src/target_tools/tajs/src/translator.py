import copy
import json
import os
import re
import glob

CNT = 1
EDGEREGEX = re.compile(r".* -> .*")
FILTER = re.compile(r".*:.*:.* -> .*:.*:.*")
NODE_POS = re.compile(r".*\.js\[(.*)\]$")


def create_schema():
    json_graph = {"directed": True, "nodes": list(), "links": list()}

    return copy.deepcopy(json_graph)


def add_node(j, label, pos, entry=False, final=True):
    for node in j.get("nodes"):
        if node.get("pos") == pos:
            return
    global CNT

    if pos == "GUESS":
        pos_match = NODE_POS.match(label)
        pos = pos_match.group(1)

    if entry:
        j.get("nodes").insert(
            0, {"id": 0, "label": label, "pos": pos, "entry": entry, "final": final}
        )
    else:
        j.get("nodes").append(
            {"id": CNT, "label": label, "pos": pos, "entry": entry, "final": final}
        )
        CNT += 1


def add_pos_node(j, label, entry=False, final=True):
    for node in j.get("nodes"):
        if node.get("label") == label:
            return
    global CNT

    pos = NODE_POS.match(label)

    j.get("nodes").append(
        {"id": CNT, "label": label, "entry": entry, "final": final, "pos": pos.group(1)}
    )
    CNT += 1


def add_link(j, from_name, to_name, nomod=False):
    target_id = 0
    source_id = 0
    for node in j.get("nodes"):
        if node.get("pos") == from_name:
            source_id = node.get("id")
            node["final"] = False
        if node.get("pos") == to_name:
            target_id = node.get("id")
    if nomod:
        label = from_name + "->" + to_name
    else:
        label = (
            ":".join(from_name.split(":")[:-2])
            + "@"
            + (
                from_name.split(":")[-2]
                if not from_name.startswith("toplevel")
                else "[toplevel]"
            )
            + " -> "
            + ":".join(to_name.split(":")[:-2])
            + "@"
            + (
                to_name.split(":")[-2]
                if not to_name.startswith("toplevel")
                else "[toplevel]"
            )
        )
    if {"target": target_id, "source": source_id, "label": label} not in j.get("links"):
        j.get("links").append(
            {"target": target_id, "source": source_id, "label": label}
        )


def convert_tajs(wd):
    NODEREGEX = re.compile(r".* \[.*\]")
    nodes = {}
    for f in glob.glob(os.path.join(wd, "*.dot")):
        edges = set()
        j = create_schema()
        with open(f, "r") as fp:
            lines = fp.readlines()

        for line in lines:
            if NODEREGEX.match(line) and ("HOST" not in line):
                node = {"file": None, "line": None, "column": None}
                matches = re.compile(r"(?P<alias>f\d+).*label=\"(?P<label>.*)\"")
                search = matches.search(line)
                alias = search.group("alias")

                label = search.group("label")
                if label == "<main>":
                    node["file"] = "toplevel"
                    node["line"] = "1"
                    node["column"] = "1"
                    nodes[alias] = node
                    continue
                c = label.split("\\n")
                s = c[1].split(":")
                node["line"] = s[1]
                node["column"] = s[2]

                detect_function = re.compile(r".*\((?P<filename>.*)\).*")
                search_function = detect_function.search(s[0])
                if search_function != None:
                    node["file"] = os.path.basename(search_function.group("filename"))
                else:
                    node["file"] = os.path.basename(s[0])
                nodes[alias] = node
                continue

        for line in lines:
            if EDGEREGEX.match(line):
                line = line.strip()
                line = line.replace('"', "")
                c = line.split("->")
                src = c[0].strip()
                tgt = c[1].strip()
                if src + "->" + tgt in edges:
                    continue
                if src not in nodes.keys() or tgt not in nodes.keys():
                    continue
                node_src = nodes.get(src)
                add_node(
                    j,
                    (
                        node_src.get("file") + "@" + node_src.get("line")
                        if node_src.get("file") != "toplevel"
                        else "[toplevel]"
                    ),
                    node_src.get("file")
                    + ":"
                    + node_src.get("line")
                    + ":"
                    + node_src.get("column"),
                )
                node_tgt = nodes.get(tgt)
                add_node(
                    j,
                    (
                        node_tgt.get("file") + "@" + node_tgt.get("line")
                        if node_tgt.get("file") != "toplevel"
                        else "[toplevel]"
                    ),
                    node_tgt.get("file")
                    + ":"
                    + node_tgt.get("line")
                    + ":"
                    + node_tgt.get("column"),
                )
                add_link(
                    j,
                    node_src.get("file")
                    + ":"
                    + node_src.get("line")
                    + ":"
                    + node_src.get("column"),
                    node_tgt.get("file")
                    + ":"
                    + node_tgt.get("line")
                    + ":"
                    + node_tgt.get("column"),
                    False,
                )
                edges.add(src + "->" + tgt)

        with open(
            os.path.join(
                os.path.dirname(f),
                "output_" + os.path.basename(f).replace(".dot", ".json"),
            ),
            "w",
        ) as fp:
            json.dump(j, fp, indent=2)


def stats_for_json(wd):
    stats = []
    for f in glob.glob(os.path.join(wd, "*.json")):
        with open(f, "r") as fp:
            j = json.load(fp)
            stats.append(
                {"file": f, "nodes": len(j.get("nodes")), "links": len(j.get("links"))}
            )

        with open(
            os.path.join(os.path.dirname(f), "stats_" + os.path.basename(wd)) + ".txt",
            "w",
        ) as fw:
            fw.write("file;nodes;links\n")
            for stat in stats:
                fw.write("%s;%d;%d\n" % (stat["file"], stat["nodes"], stat["links"]))

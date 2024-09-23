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
    # NNODEREGEX matches lines representing nodes
    # EDGEREGEX matches lines representing edges
    NODEREGEX = re.compile(r".* \[.*\]")
    EDGEREGEX = re.compile(r".*->.*")

    for f in glob.glob(os.path.join(wd, "*.dot")):
        nodes = {}
        callgraph = {}
        edges = set()

        # Read the TAJS dot file
        with open(f, "r") as fp:
            lines = fp.readlines()
            content = fp.read()
        print(content)
        # Process nodes and assign names
        for line in lines:
            if NODEREGEX.match(line):
                matches = re.search(r"(?P<alias>f\d+).*label=\"(?P<label>.*)\"", line)
                alias = matches.group("alias")
                label = matches.group("label")

                if label == "<main>":
                    func_name = "main"
                else:
                    # Extract the function name and file path
                    parts = label.split("\\n")
                    function_name = parts[0].split("(")[0].strip()
                    file_info = parts[1]

                    # Only process benchmark files
                    # TODO: Verify this
                    if "HOST" in file_info:
                        continue  # Skip nodes that aren't part of the benchmark

                    # Get just the function name without adding file suffix
                    # TODO: multi-file testcases needs to be handled
                    func_name = "main." + function_name

                nodes[alias] = func_name
                if func_name not in callgraph:
                    callgraph[func_name] = []

        # Process edges and construct the callgraph
        for line in lines:
            if EDGEREGEX.match(line):
                c = line.replace('"', "").split("->")
                src = c[0].strip()
                tgt = c[1].strip()

                if src in nodes and tgt in nodes:
                    src_func = nodes[src]
                    tgt_func = nodes[tgt]

                    # Add the target function to the source function's list of callees
                    if tgt_func not in callgraph[src_func]:
                        callgraph[src_func].append(tgt_func)
                    edges.add(src + "->" + tgt)
    # Write output to JSON
    with open(
        os.path.join(
            os.path.dirname(f),
            "output_" + os.path.basename(f).replace(".dot", ".json"),
        ),
        "w",
    ) as fp:
        json.dump(callgraph, fp, indent=2)


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

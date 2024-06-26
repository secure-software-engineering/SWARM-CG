// rc/Class.java
package rc;

import lib.annotations.callgraph.DirectCall;

record Thing (String attr1) {
    public Thing(String attr1) {
        this.attr1 = attr1;
        }
    }

class Class {
    @DirectCall(name = "Thing", line = 14, resolvedTargets = "Lrc/Thing;")
    public static void main(String[] args) {
        Thing thing = new Thing("attribute");
    }
}

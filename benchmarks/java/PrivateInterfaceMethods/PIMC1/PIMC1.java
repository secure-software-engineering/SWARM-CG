// pimc/Class.java
package pimc;

import lib.annotations.callgraph.DirectCall;
interface Interface {
    @DirectCall(name = "privateMethod", line = 7, resolvedTargets = "Lpimc/Interface;")
    default void method() {
        privateMethod();
    }
    private void privateMethod () {
        //do something
    }
}

class Class implements Interface {
    public static void main(String[] args) {
        Class obj = new Class();
        obj.method();
    }
}

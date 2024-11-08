// pimc/Class.java
package pimc;

import lib.annotations.callgraph.DirectCall;
interface Interface {
    @DirectCall(name = "privateMethod", line = 8, resolvedTargets = "Lpimc/Interface;",
            prohibitedTargets = "Lpimc/Interface", ptParameterTypes = { int.class })
    default void method() {
        privateMethod();
    }
    private void privateMethod () {
        //do something
    }
    private void privateMethod (int i) {
        //do something
    }
}

class Class implements Interface {
    public static void main(String[] args) {
        Class obj = new Class();
        obj.method();
    }
}

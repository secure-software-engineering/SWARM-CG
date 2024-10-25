// id/Class.java
package id;


class Class implements Interface {

    @FunctionalInterface public interface FIBoolean {
        boolean get();
    }

    public static void main(String[] args){
        Class cls = new Class();
        FIBoolean bc = cls::method;
        bc.get();
    }
}

interface Interface {
    default boolean method() {
        return true;
    }
}

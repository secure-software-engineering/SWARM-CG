// tr/Demo.java
package tr;


class Demo {
    public static void verifyCall(){ /* do something */ }

    public Demo(String s) { Demo.verifyCall(); }

    public static void main(String[] args) throws Exception {
        Demo.class.getConstructor(String.class).newInstance("42");
    }
}

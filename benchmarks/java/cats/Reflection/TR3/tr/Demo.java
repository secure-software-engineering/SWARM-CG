// tr/Demo.java
package tr;


public class Demo {
    public String target() { return "Demo"; }

    void caller() throws Exception {
        Demo.class.getMethod("target").invoke(this);
    }

    public static void main(String[] args) throws Exception { new Demo().caller(); }
}

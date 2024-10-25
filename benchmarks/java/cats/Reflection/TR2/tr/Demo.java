// tr/Demo.java
package tr;


class Demo {
    public String target() { return "Demo"; }

    void caller() throws Exception {
        Demo.class.getDeclaredMethod("target").invoke(this);
    }

    public static void main(String[] args) throws Exception {
        new Demo().caller();
    }
}

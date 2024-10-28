// reflection/TrivialReflectionDemo.java
package reflection;

class TrivialReflectionDemo {
    static String targetMethod() { return "42"; }

    public static void main(String[] args) throws Exception {
        TrivialReflectionDemo.class.getDeclaredMethod("targetMethod").invoke(null);
    }
}
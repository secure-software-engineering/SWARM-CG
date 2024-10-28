// reflections/ContextSensitiveDemo.java
package reflections;

class ContextSensitiveDemo {
    public static void triggerVerification() { /* do something */ }

    static void loadClassByName(String className) throws Exception {
        Class.forName(className);
    }

    public static void main(String[] args) throws Exception {
        ContextSensitiveDemo.loadClassByName("reflections.StaticInitializerClass");
    }
}

class StaticInitializerClass {

    static {
        callStaticInitializer();
    }

    static private void callStaticInitializer() {
        ContextSensitiveDemo.triggerVerification();
    }
}
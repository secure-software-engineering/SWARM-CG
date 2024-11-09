// tr/Demo.java
package tr;

class Demo {
    public static void verifyCall(){ /* do something */ }

    public static void main(String[] args) throws Exception {
        Class.forName("tr.InitializedClass");
    }
}

class InitializedClass {
    
    static {
        staticInitializerCalled();
    }

    static private void staticInitializerCalled(){
        Demo.verifyCall();
    }
}

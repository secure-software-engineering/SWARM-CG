// csr/Demo.java
package csr;

class Demo {
    public static String className;

    public static void verifyCall(){ /* do something */ }

    static void callForName() throws Exception {
        Class.forName(Demo.className);
    }

    public static void main(String[] args) throws Exception {
        Demo.className = "csr.CallTarget";
        Demo.callForName();
    }
}

class CallTarget {
    
     static {
         staticInitializerCalled();
     }

     static private void staticInitializerCalled(){
         Demo.verifyCall();
     }
 }

// lrr/Demo.java
package lrr;


class Demo {
    private String className;

    public static void verifyCall(){ /* do something */ }

    public static void main(String[] args) throws Exception {
        Demo demo = new Demo();
        demo.className = "lrr.TargetClass";
        Class.forName(demo.className);
    }
}

class TargetClass {
    
     static {
         staticInitializerCalled();
     }

     static private void staticInitializerCalled(){
         Demo.verifyCall();
     }
 }

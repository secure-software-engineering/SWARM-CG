// lib5/collude/Demo.java
package lib5.collude;


public class Demo {
    
    public static void interfaceCallSite(PotentialInterface pi){
        pi.method();
    }
}

interface PotentialInterface {
    
    void method();
}

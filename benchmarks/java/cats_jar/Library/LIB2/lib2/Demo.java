// lib2/Demo.java
package lib2;


public class Demo {
    
    public Type field = new Subtype();
    
    public void callOnField(){
        field.method();
    }
}

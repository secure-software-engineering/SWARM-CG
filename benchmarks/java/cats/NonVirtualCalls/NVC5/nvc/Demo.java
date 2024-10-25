// nvc/Demo.java
package nvc;


public class Demo {
    
    public static void main(String[] args){
      new Sub().method();
    }
}

class Super { 
    
    void method() { /* doSomething */ } 
}

class Middle extends Super {
    
    void method() { /* doSomething */ }
}

class Sub extends Middle {

    void method() { 
        super.method(); 
    }
}

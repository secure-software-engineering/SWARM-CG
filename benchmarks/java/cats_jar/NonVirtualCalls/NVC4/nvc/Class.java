// nvc/Class.java
package nvc;


class Class extends Superclass {

    protected void method(){
        super.method();
    }

    public static void main(String[] args){
        Class cls = new Class();
        cls.method();
    }
}

class Superclass extends Rootclass {
    
}

class Rootclass {
    protected void method(){ /* do something relevant */ }
}

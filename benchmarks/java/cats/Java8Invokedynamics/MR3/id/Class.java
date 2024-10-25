// id/Class.java
package id;


class Class extends SuperClass {

    public void callViaMethodReference(){
        java.util.function.Supplier<String> stringSupplier = super::getTypeName;
        stringSupplier.get();
    }

    public static void main(String[] args){
        Class cls = new Class();
        cls.callViaMethodReference();
    }
}

class SuperClass{
    protected String getTypeName() { return "Lid/SuperClass;";}
}

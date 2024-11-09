// id/Class.java
package id;


class Class {

    private String getTypeName() { return "Lid/Class;";}

    public void callViaMethodReference(){
        java.util.function.Supplier<String> stringSupplier = this::getTypeName;
        stringSupplier.get();
    }

    public static void main(String[] args){
        Class cls = new Class();
        cls.callViaMethodReference();
    }
}

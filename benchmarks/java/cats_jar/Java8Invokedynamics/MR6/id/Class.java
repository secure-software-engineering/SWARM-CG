// id/Class.java
package id;

import java.util.function.Supplier;

class Class {

    public Class(){}

    public static void main(String[] args){
        Supplier<Class> classSupplier = Class::new;
        classSupplier.get();
    }
}

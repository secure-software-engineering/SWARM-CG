// id/Class.java
package id;

import java.util.function.Supplier;

class Class {

    public static void main(String[] args){
        Supplier<String> stringSupplier = Class::getTypeName;
        stringSupplier.get();
    }

    static String getTypeName() { return "Lid/Class"; }
}

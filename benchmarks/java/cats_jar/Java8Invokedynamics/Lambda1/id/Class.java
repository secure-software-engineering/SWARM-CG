// id/Class.java
package id;

import java.util.function.Function;

class Class {
    public static void main(String[] args){
        Function<Integer, Boolean> isEven = (Integer a) -> {
            doSomething();
            return a % 2 == 0;
        };
        isEven.apply(2);
    }

    private static void doSomething(){
        // call in lambda
    }
}

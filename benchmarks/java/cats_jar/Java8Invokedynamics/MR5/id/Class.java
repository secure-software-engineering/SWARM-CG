// id/Class.java
package id;

import java.util.function.Supplier;


class Class {

    public static double sum(double a, double b) { return a + b; }

    @FunctionalInterface public interface FIDoubleDouble {
        double apply(double a, double b);
    }

    public static void main(String[] args){
        FIDoubleDouble fidd = Class::sum;
        fidd.apply(1d,2d);
    }
}

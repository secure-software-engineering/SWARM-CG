// id/Class.java
package id;

class Class {

    public interface MyMarkerInterface1 {}
    public interface MyMarkerInterface2 {}

    public @FunctionalInterface interface Runnable {
        void run();
    }

    public static void doSomething(){
        /* do something */
    }

    public static void main(String[] args) {
        Runnable run = (Runnable & MyMarkerInterface1 & MyMarkerInterface2) () -> doSomething();
        run.run();
    }
}

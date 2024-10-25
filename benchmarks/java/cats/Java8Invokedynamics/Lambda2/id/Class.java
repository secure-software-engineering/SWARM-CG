// id/Class.java
package id;


class Class {

    public static void doSomething(){ }

    //
    public static void main(String[] args) {
        Runnable lambda = LambdaProvider.getRunnable();
        lambda.run();
    }
}

class LambdaProvider {

    public static void doSomething(){
        /* do something */
    }

    public static id.Runnable getRunnable(){
        return () -> LambdaProvider.doSomething();
    }
}

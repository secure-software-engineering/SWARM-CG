// jvmc/Demo.java
package jvmc;

public class Demo {

	public static void main(String[] args) throws InterruptedException {
        Runnable r = new TargetRunnable();
        Thread t = new Thread(r);
        t.setUncaughtExceptionHandler(new ExceptionalExceptionHandler());
        t.start();
        t.join();
	}
}

class TargetRunnable implements Runnable {
    
    public void run(){
        throw new IllegalArgumentException("We don't want this thread to work!");
    }   
}

class ExceptionalExceptionHandler implements Thread.UncaughtExceptionHandler {
 
    private static void callback() { /* do something */ }
    
    public void uncaughtException(Thread t, Throwable e){
        callback();
        // Handle the uncaught Exception (IllegalArgumentException)
    }
}

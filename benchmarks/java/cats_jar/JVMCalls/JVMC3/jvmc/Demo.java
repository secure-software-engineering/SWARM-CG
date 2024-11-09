// jvmc/Demo.java
package jvmc;


public class Demo {

	public static void main(String[] args) throws InterruptedException {
        Runnable r = new TargetRunnable();
        Thread t = new Thread(r);
        t.start();
        t.join();
	}
}

class TargetRunnable implements Runnable {
    
    public void run(){
        verifyReachability();
        /* Do the hard work */
    }
    
    static void verifyReachability(){ }
}

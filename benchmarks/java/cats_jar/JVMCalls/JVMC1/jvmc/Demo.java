// jvmc/Demo.java
package jvmc;

import java.lang.System;
import java.lang.Runtime;


public class Demo {

    public static void callback(){ /* do something */ }

	public static void main(String[] args){
        Runnable r = new TargetRunnable();
        Runtime.getRuntime().addShutdownHook(new Thread(r));
	}
}

class TargetRunnable implements Runnable {
    
    public void run(){
        Demo.callback();
    }
}

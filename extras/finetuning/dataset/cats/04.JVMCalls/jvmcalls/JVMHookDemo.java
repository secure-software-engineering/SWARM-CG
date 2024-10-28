// jvmcalls/JVMHookDemo.java
package jvmcalls;

import java.lang.System;
import java.lang.Runtime;

public class JVMHookDemo {

    public static void onShutdownCallback() { /* do something */ }

    public static void main(String[] args) {
        Runnable runnableTask = new ShutdownTask();
        Runtime.getRuntime().addShutdownHook(new Thread(runnableTask));
    }
}

class ShutdownTask implements Runnable {

    public void run() {
        JVMHookDemo.onShutdownCallback();
    }
}
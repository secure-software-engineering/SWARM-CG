// jvmc/Demo.java
package jvmc;

public class Demo {

    public static void callback(){};

	public static void main(String[] args){
          for(int i = -1; i < args.length; i++){
              new Demo();
          }
	}
	
    public void finalize() throws java.lang.Throwable {
        callback();
        super.finalize();
    }	
}

// serlam/DoSerialization.java
package serlam;

import java.io.Serializable;
import java.lang.invoke.SerializedLambda;
import java.lang.reflect.Method;
import java.util.function.Function;

import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.FileInputStream;
import java.io.ObjectInputStream;

public class DoSerialization {

    @FunctionalInterface interface Test extends Serializable{
        String concat(Integer seconds);
    }

    public static void main(String[] args) throws Exception {
        float y = 3.13f;
        String s = "bar";
        
        Test lambda = (Integer x) -> "Hello World " + x + y + s;
        
        FileOutputStream fos = new FileOutputStream("serlam1.ser");
        ObjectOutputStream out = new ObjectOutputStream(fos);
        out.writeObject(lambda);
        out.close();
        
        
    }
}

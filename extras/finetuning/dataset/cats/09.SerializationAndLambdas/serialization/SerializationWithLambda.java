// serialization/SerializationWithLambda.java
package serialization;

import java.io.Serializable;
import java.lang.invoke.SerializedLambda;
import java.lang.reflect.Method;
import java.util.function.Function;

import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.FileInputStream;
import java.io.ObjectInputStream;

public class SerializationWithLambda {

    @FunctionalInterface
    interface Test extends Serializable {
        String concatenate(Integer seconds);
    }

    public static void main(String[] args) throws Exception {
        float value = 3.13f;
        String text = "bar";

        Test lambdaFunction = (Integer x) -> "Hello World " + x + value + text;

        FileOutputStream fos = new FileOutputStream("serializationLambda.ser");
        ObjectOutputStream out = new ObjectOutputStream(fos);
        out.writeObject(lambdaFunction);
        out.close();
    }
}
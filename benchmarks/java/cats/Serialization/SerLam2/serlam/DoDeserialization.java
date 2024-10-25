// serlam/DoDeserialization.java
package serlam;

import java.io.FileInputStream;
import java.io.ObjectInputStream;


public class DoDeserialization {

    public static void main(String[] args) throws Exception {
        DoSerialization.main(args);
        FileInputStream fis = new FileInputStream("serlam2.ser");
        ObjectInputStream in = new ObjectInputStream(fis);
        Object obj = in.readObject();
        in.close();
    }
}
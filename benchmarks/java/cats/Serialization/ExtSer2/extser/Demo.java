// extser/Demo.java
package extser;

import java.io.Externalizable;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.ObjectOutput;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.io.ObjectInput;
import java.io.IOException;


public class Demo implements Externalizable {
    
    public void readExternal(ObjectInput in) throws IOException, ClassNotFoundException {
        callback();
    }

    public void writeExternal(ObjectOutput out) throws IOException {
        callback();
    }

    public void callback() { }

    public static void main(String[] args) throws Exception {
        FileInputStream fis = new FileInputStream("test.ser");
        ObjectInputStream in = new ObjectInputStream(fis);
        Demo obj = (Demo) in.readObject();
        in.close();
    }
}

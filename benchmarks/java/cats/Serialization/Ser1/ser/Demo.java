// ser/Demo.java
package ser;

import java.io.Serializable;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.IOException;


public class Demo implements Serializable {
    
    static final long serialVersionUID = 42L;

    private void writeObject(java.io.ObjectOutputStream out) throws IOException {
    	out.defaultWriteObject();
    }

    public static void main(String[] args) throws Exception {
    	Demo serialize = new Demo();
    	FileOutputStream fos = new FileOutputStream("test.ser");
    	ObjectOutputStream out = new ObjectOutputStream(fos);
    	out.writeObject(serialize); // triggers serialization
    	out.close();
    }
}

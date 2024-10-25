// ser/Demo.java
package ser;

import java.io.Serializable;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.IOException;
import java.io.ObjectStreamException;


public class Demo implements Serializable {
    
    static final long serialVersionUID = 42L;
    
    public Object replace() { return this; }

    private Object writeReplace() throws ObjectStreamException {
    	return replace();
    }

    public static void main(String[] args) throws Exception {
    	Demo serialize = new Demo();
    	FileOutputStream fos = new FileOutputStream("test.ser");
    	ObjectOutputStream out = new ObjectOutputStream(fos);
    	out.writeObject(serialize);
    	out.close();
    }
}

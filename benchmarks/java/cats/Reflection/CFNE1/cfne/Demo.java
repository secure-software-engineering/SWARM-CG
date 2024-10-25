// cfne/Demo.java
package cfne;


public class Demo {

    public static void verifyCall(){ /* do something */ }

	public static void main(String[] args){
	    try {
	        Class cls = Class.forName("cfne.DeceptiveClass");
	        LoadedClass lCls = (LoadedClass) cls.newInstance();
	    } catch(ClassCastException cce){
	        verifyCall();
	    } catch(ClassNotFoundException cnfe){
	        // DEAD CODE
	    } catch(Exception rest){
            // DEAD CODE
        }
	}
}

class DeceptiveClass {

}

class LoadedClass {

}

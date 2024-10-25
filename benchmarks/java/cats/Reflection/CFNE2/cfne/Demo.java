// cfne/Demo.java
package cfne;


public class Demo {

    public static void verifyCall(){ /* do something */ }

	public static void main(String[] args){
	    try {
	        Class cls = Class.forName("cfne.CatchMeIfYouCan");
	        // DEAD CODE
	        LoadedClass lCls = (LoadedClass) cls.newInstance();
	    } catch(ClassCastException cce){
	        /* DEAD CODE */
	    } catch(ClassNotFoundException cnfe){
	        verifyCall();
	    } catch(Exception rest){
	        //DEAD CODE
	    }
	}
}

class LoadedClass {

}

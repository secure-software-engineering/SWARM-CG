// si/Demo.java
package si;

public class Demo {
	public static void main(String[] args) {
		Interface.referenceMe.toString();
	}
}

interface Interface {

    static String testHook = init();
    static final Demo referenceMe = new Demo();

    static String init() {
        callback();
        return "Interface";
    }

    static void callback(){}
}

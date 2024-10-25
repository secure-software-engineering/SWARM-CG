// si/Main.java
package si;

public class Main {

	public static void main(String[] args) {
		new Subclass();
	}
}

class Subclass extends Superclass {
	static String name = init();

	static String init() {
		callback();
		return "Subclass";
	}

	static void callback() {}
}

class Superclass extends RootClass {

    static {
        superInit();
    }

    static void superInit(){
        callback();
    }

    static void callback() {}
}

class RootClass {

    static {
        rootInit();
    }

    static void rootInit(){
      callback();
    }

    static void callback() {}
}

// si/Main.java
package si;

public class Main {

	public static void main(String[] args) {
		Demo.assignMe = 42;
	}
}

class Demo {
	static String name = init();

    static int assignMe;

	static String init() {
		callback();
		return "Demo";
	}

	static void callback() {}
}

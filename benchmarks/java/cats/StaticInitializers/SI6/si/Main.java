// si/Main.java
package si;

public class Main {

	public static void main(String[] args) {
		Demo.callback();
	}
}

class Demo {
	static String name = init();

	static String init() {
		callback();
		return "42";
	}

	static void callback() {}
}

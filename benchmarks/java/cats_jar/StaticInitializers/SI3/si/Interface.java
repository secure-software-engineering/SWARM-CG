// si/Interface.java
package si;

public interface Interface {

	static String name = init();

	static String init() {
		callback();
		return "Demo";
	}

	default String defaultMethod() { return "Demo"; }

	static void callback() {}
}
class Demo implements Interface {
	public static void main(String[] args) {
		new Demo();
	}
}

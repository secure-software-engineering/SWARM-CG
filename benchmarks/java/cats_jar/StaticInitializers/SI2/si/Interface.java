// si/Interface.java
package si;

public interface Interface {

	static String name = init();

	static String init() {
		callback();
		return "Demo";
	}

	static void callback() {}
}
class Demo {
    
	public static void main(String[] args) {
		Interface.callback();
	}
}

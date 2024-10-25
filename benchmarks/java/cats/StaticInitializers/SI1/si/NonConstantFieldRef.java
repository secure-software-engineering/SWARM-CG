// si/NonConstantFieldRef.java
package si;

public interface NonConstantFieldRef {

	static String nonConstantField = init();

	static String init() {
		callback();
		return "Demo";
	}

	static void callback() {}
}

class Main {
	public static void main(String[] args) {
		NonConstantFieldRef.nonConstantField.toString();
	}
}

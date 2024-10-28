// classloading/URLClassLoaderDemo.java
package classloading;

import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.Comparator;

public class URLClassLoaderDemo {


    private static final String DIRECTORY = System.getProperty("user.dir") + "/resources/";
    private static URL classLoaderVersion1;

    static {
        try {
            classLoaderVersion1 = new URL("file://" + DIRECTORY + "classloading-version-1.jar");
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }
    }

    private static final String CLASS_NAME = "lib.IntComparator";

    public static void main(String[] args)
            throws ClassNotFoundException, IllegalAccessException, InstantiationException {
        ClassLoader parentClassLoader = ClassLoader.getSystemClassLoader();
        URL[] urls = new URL[] { classLoaderVersion1 };
        URLClassLoader urlClassLoader = URLClassLoader.newInstance(urls, parentClassLoader);
        Class<?> cls = urlClassLoader.loadClass(CLASS_NAME);
        Comparator<Integer> comparator = (Comparator<Integer>) cls.newInstance();
        Integer one = Integer.valueOf(1);
        comparator.compare(one, one);
    }
}

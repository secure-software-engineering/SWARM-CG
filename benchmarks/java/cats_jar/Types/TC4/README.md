[//]: # (MAIN: instanceofcheck.Demo)
Type narrowing due to Java's built-in ```instanceof``` check of the given object ```o``` and the 
```Target``` class. Within the ```this``` branch of ```Demo.callIfInstanceOfTarget``` it is thus
known that the passed object ```o``` must be of type ```Target```. Hence, ```o.toString``` must only
be resolved to ```Target.toString```.

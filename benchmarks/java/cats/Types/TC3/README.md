[//]: # (MAIN: classeq.Demo)
Type narrowing due to a equality check of two ```java.lang.Class``` objects. Within the ```this```
branch of ```classeq.Demo.callIfInstanceOfTarget``` it is thus known that the passed object ```o```
must be of type ```Target```. Hence, ```o.toString``` must only be resolved to ```Target.toString```.

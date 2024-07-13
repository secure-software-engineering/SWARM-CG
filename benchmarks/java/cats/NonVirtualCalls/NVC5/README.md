[//]: # (MAIN: nvc.Demo)
Tests the resolution of a super call in a larger type hierarchy. In a class hierarchy like below,
with ```nvc.Sub <: nvc.Middle <: nvc.Super```, the super call in ```nvc.Sub.method``` will always invoke
```nvc.Middle.method``` even if ```Sub``` was compiled when ```nvc.Middle``` did not yet have an
implementation of ```method``` and thus the ```invokespecial``` references ```nvc.Super```.

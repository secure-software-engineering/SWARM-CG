[//]: # (MAIN: simplecast.Demo)
This case shows type narrowing due to previous cast. The method ```simplecast.Demo.castToTarget``` takes an
object, casts it to ```simplecast.Target```, and then calls ```target``` on the casted object which
rules out ```simplecast.Demo.target``` as receiver.

function returnFunc() {
    function nestedReturnFunc() {
    }
    return nestedReturnFunc;
}
  
function func() {
    return returnFunc;
}
  
func()();
func()()();
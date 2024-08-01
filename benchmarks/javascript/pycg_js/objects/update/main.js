function func1() {
  }
  
  function func2() {
  }
  
  let d = { "a": func1 };
  
  Object.assign(d, { "a": func2 });
  d["a"]();
  
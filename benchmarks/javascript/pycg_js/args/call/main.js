function param_func() {}

function func(a) {
  a();
}

func(param_func);

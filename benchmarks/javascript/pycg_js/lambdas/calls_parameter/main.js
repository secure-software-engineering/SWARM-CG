const func1 = () => {};
const func2 = () => {};
const x = (x) => {
  x();
};
x(func1);
x(func2);

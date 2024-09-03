import { parent } from "./ext.js";
class A extends parent {
  fn() {
    this.parent_fn();
  }
}
const a = new A();
a.fn();

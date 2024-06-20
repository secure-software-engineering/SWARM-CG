import { key } from "./ext.js";

function func() {}

const d = { a: func };

d[key]();

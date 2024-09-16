import { key } from './ext.js';

function func() {
}

let d = {"a": func};

d[key]();

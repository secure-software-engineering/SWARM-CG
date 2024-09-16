export function ext_change(c, fn) {
    function change() {
        c.fn = fn;
    }

    change();
}

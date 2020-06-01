/*
 * @param {Array} fwcnfs A mapping object holds firewall configurations
 */
function make_firewall_policy_maps(fwcnfs) {
    /*
     * @seealso https://api.jquery.com/jQuery.map/
     */
    /*
     * @seealso src/nof/fortios/views.py
     */
    const keys = ["edit",
                  "srcaddr",
                  "srcintf",
                  "dstaddr",
                  "dstintf",
                  "service",
                  "status",
                  "action",
                  "comments",
                  "srcaddrs",
                  "dstaddrs"]

    let policies = $.map(fwcnfs, function (val, key) {
        console.log(val); // debug

        for (let k in keys) {
            if (! (k in val)) {
                val[k] = 'undef'; // default value
            }
        }
        return val;
    });
    return policies;
}
/* vim:sw=4:ts=4:et:
 */

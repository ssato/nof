/*
 * @param {Array} fwcs A mapping object holds firewall configurations
 */
function make_firewall_policy_maps(fwcs) {
    /*
     * @seealso https://api.jquery.com/jQuery.map/
     */
    const keys = ["name",
                  "srcaddr",
                  "srcintf",
                  "dstaddr",
                  "dstintf",
                  "service",
                  "status",
                  "action",
                  "logtraffic",
                  "comments",
                  "schedule",
                  "uuid"];

    let policies = $.map(fwcs["policy"], function (val, key) {
        val["_id"] = val["name"] = key;
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

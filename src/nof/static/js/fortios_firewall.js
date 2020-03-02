/*
 * @param {Array} fwcs A mapping object holds firewall configurations
 */
function make_firewall_policy_maps(json) {
    /*
     * @seealso https://api.jquery.com/jQuery.map/
     */
    const fwcs = json.data;
    const keys = ["action", "comments", "dstaddr", "dstintf", "logtraffic",
                  "name", "schedule", "service", "srcaddr", "srcintf",
                  "status", "uuid"];

    let policies = $.map(fwcs["policy"], function (val, key) {
        val["_id"] = key;

        for (let k in keys) {
            if (val.get(k) == undefined) {
                val[k] = 'undef'; // default value
            }
        }
        return val;
    });
    return policies;
}
/* vim:sw=4:ts=4:et:
 */

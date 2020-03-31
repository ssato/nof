/*
 * ref. https://observablehq.com/@d3/force-directed-graph
 * ref. https://wizardace.com/d3-bartooltip/
 */
/*
 *
 * globals:
 * - networks :: {'id':, 'addrs': [<ip_addr>], 'label':, ...}
 *
 */
function render_node_link(data, width=700, height=700) {
  console.log(network_addresses);
  console.log(node_path_0_addrs);
  console.log(data); // {nodes, links}

  const radius = function (d) {
    if (d.type == "network") {
      return 16;
    }
    else if (d.type == "firewall" || d.type == "router" || d.type == "switch") {
      return 10;
    }
    else {
      return 7;
    }
  }

  const drag = function (simulation) {
    function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }

    function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return d3.drag()
             .on("start", dragstarted)
             .on("drag", dragged)
             .on("end", dragended);
  }

  const tooltip = d3.select("#node-graph")
                    .append("div")
                    .attr("class", "tooltip rounded");

  let show_tooltip = (d) => {
    tooltip.style("visibility", "visible")
           .html("name: " + d.name + "<br/>addr: " + d.addr);
  };
  let hide_tooltip = () => { tooltip.style("visibility", "hidden"); };
  let move_tooltip = () => {
    tooltip.style("top", (d3.event.pageY - 20) + "px")
           .style("left", (d3.event.pageX + 10) + "px");
  };

  const node_info = d3.select("#node-info");

  let show_node_info = (d) => {
    node_info.html("<div class='row text-primary'>#" + d.id + ": " + d.name + "</div>" +
                   "<ul class='row text-secondary'>" +
                   "  <li>type: " + d.type + "</li>" +
                   "  <li>address: " + d.addrs.join(", ") + "</li>" +
                   "</ul>");
  };

  const links = data.links.map(d => Object.create(d));
  const nodes = data.nodes.map(d => Object.create(d));

  const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id))
      .force("charge", d3.forceManyBody()
                         .strength(-50))
      .force("center", d3.forceCenter(width / 2, height / 2));

  const svg = d3.select("svg")
                .attr("viewBox", "0 0 " + width + " " + height)
                .attr("preserveAspectRatio", "xMidYMid meet");

  const link = svg.append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(links)
    .join("line")
      .attr("stroke-width", d => Math.sqrt(d.value));

  const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(nodes)
    .join("circle")
      .attr("r", radius)
      .attr("class", function (d) {
        if (network_addresses.some(addr => d.addrs.includes(addr)) ||
            node_path_0_addrs.some(addr => d.addrs.includes(addr))) {
          return d.class + " found";
        } else {
          return d.class;
        }
      })
      .call(drag(simulation))
      .on("mouseover", show_tooltip)
      .on("mouseout", hide_tooltip)
      .on("mousemove", move_tooltip)
      .on("click", show_node_info);

  node.append("title")
      .text(d => d.label);

  simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
  });
};
/* vim:sw=2:ts=2:et:
 */

let margin = {top: 200, right: 150, bottom: 200, left: 150},
    width = 1000 - margin.left - margin.right,
    height = 1000 - margin.top - margin.bottom,
    outerRadius = Math.min(width, height) / 2 - 70,
    innerRadius = outerRadius - 30;

let height2 = 460,width2 = 460;


let formatPercent = d3.format(".1%");

let chordChart = d3.select("#myDataViz")
    .append("svg")
    .attr("width",width)
    .attr("height",height)
    .append("g")
    .attr("id","circle").attr("transform",
        "translate("+width/2+","+height/2+")");

let testGraph = d3.select("#testDiv")
    .append("svg")
    .attr("id", "treeGraph")
    .attr("width",width2)
    .attr("height",height2)



/*testGraph.append("rect")
    .attr("width",200)
    .attr("height",100)
    .attr("stroke","black")
    .style("fill","transparent")

testGraph.append("text")
    .attr("class","testText")
    .attr("x",70)
    .attr("y",30)*/


// chordChart.append("circle").attr("r",outerRadius);

//load dataset
const drawChord = async () =>{

  const colorPalette = ["#48bf8e", "#075c62", "#a1def0", "#5e2a96",
    "#e775cc", "#f3c5fa", "#9a76af", "#1c4585",
    "#479abc", "#94ea5b", "#1d6d1f", "#cddb9b",
    "#604020", "#d48f4d", "#f24219", "#8e1023",
    "#8c956d", "#2cf52b", "#ff0087", "#e9d737"]

  let colorScale = d3.scaleOrdinal().range(colorPalette)

  const got = await d3.json("relationships1.json");
  console.log(got);

  let nodes = got.nodes;
  let edges = got.edges;

  let matrix = [];
  let connections = {};

  for (let i=0; i<nodes.length; i++) {
    let row = [];
    for (let j=0; j<nodes.length; j++) { row.push(0); }

    matrix.push(row);
    connections[i] = [i]; // everything connected to itself!
  }
  console.log(matrix);

  edges.forEach( d => {
    if (d["weight"] > 0) {
      matrix[d.source_index][d.target_index] = d["weight"];
      matrix[d.target_index][d.source_index] = d["weight"];

      connections[d.source_index].push(d.target_index);
      connections[d.target_index].push(d.source_index);
    }
  });

  console.log(matrix);
  console.log(connections);

  let arc = d3.arc()
      .innerRadius(innerRadius)
      .outerRadius(outerRadius);

  let layout = d3.chord()
      .padAngle(.04)
      .sortSubgroups(d3.descending)
      .sortChords(d3.ascending);

  let ribbon = d3.ribbon()
      .radius(innerRadius);

  let chords = layout(matrix);
  console.log(chords);

  //Draw the diagram
  chordChart.attr("transform",`translate(${width/2.0},${height/2.0})`);

  let ringContainer = chordChart.append("g");
  let rings = ringContainer.selectAll("g.segment")
      .data(chords.groups)
      .join("g")
      .attr("class","segment");


  rings.append("path")
      .attr("fill", d => colorScale( nodes[ d.index ].name ))
      .attr("stroke", d => colorScale( nodes[ d.index ].name ))
      .attr("d", arc);

  let ribbonContainer = chordChart.append("g");
  let ribbons = ribbonContainer.selectAll("path.ribbon")
      .data(chords)
      .join("path")
      .attr("class","ribbon")
      .attr("fill-opacity", 0.5)
      .attr("stroke", "none")
      .attr("fill", d => colorScale( nodes[ d.source.index ].name ))
      .attr("d", ribbon);


  chords.groups.forEach( d => {
    let transform = '';
    let midpoint = (d.startAngle + d.endAngle) / 2;
    let rotation = ( midpoint ) * ( 180 / Math.PI ) - 90;
    transform = transform + ` rotate(${rotation})`;
    transform = transform + ` translate(${outerRadius}, 0)`;
    if (rotation > 90) {
      transform = transform + ' rotate(180)';
      // Notice text anchor issue that also first
      d.anchor = "end";
    }
    d.trans = transform;
  });

  rings.append("text")
      .attr("transform", d => d.trans)
      .attr("class","text")
      .text(d => nodes[ d.index ].name )
      .attr("x",-1)
      .attr("dy",".5em")
      .attr("text-anchor", d => d.anchor);

  /*chordChart.selectAll("text")
      .data(chords.groups)
      .append("text")
      .attr("dx", 4)
      .attr("dy", ".35em")
      .append("textPath")
      .attr("class", "label")
      .attr("xlink:href", function(d) { return "#group" + d.index; })
      .text(d => nodes[ d.index ].name )
      //.text(function(d) { return "Arc " + d.index; })
      .style("fill", function(d) { return d3.rgb(fill(d.index)).darker(2); });*/


  function restoreHighlights() {
    rings.attr("opacity", 1);   // both text and ring
    ribbons.attr("opacity", 1);
  }
  function lowlightAll() {
    rings.attr("opacity", 0.2); // both text and ring
    ribbons.attr("opacity", 0.2);
  }

  function highlightRings(index) {
    let targetSegments = rings.filter( d => {
      return connections[d.index].includes(index);
    });
    targetSegments.attr("opacity",1);
  }

  function highlightRibbons(index) {
    let targetRibbons = ribbons.filter( d => {
      return d.source.index === index || d.target.index === index;
    });
    targetRibbons.attr("opacity",1);

  }

  rings.on("mouseout", function(event,d){
    restoreHighlights();
    /* testGraph.select("rect").style("fill","transparent");
     testGraph.select("text").text(" ")*/
    //testGraph.style("visibility", "hidden");

    d3.selectAll("#treeGraph > *").remove();



  });


  rings.on("mouseover", function(event, d) {
    lowlightAll();
    highlightRings(d.index);
    highlightRibbons(d.index);

    let targets = edges.filter(edge=>edge.source_index===d.index)

    testGraph.style("visibility", "visible");

    //Tree Graph starts here
    let cluster = d3.cluster().size([height2,width2-100]);

    let root = d3.hierarchy(d, d => {
      return(edges.filter(edge=>edge.source_index===d.index));
    });

    cluster(root);
    console.log(root);



    testGraph.selectAll('path')
        .data(root.descendants().slice(1) )
        .enter()
        .append('path').attr("d", function(d) {
      return "M" + d.y + "," + d.x
          + "C" + (d.parent.y + 50) + "," + d.x
          + " " + (d.parent.y + 150) + "," + d.parent.x // 50 and 150 are coordinates of inflexion, play with it to change links shape
          + " " + d.parent.y + "," + d.parent.x;
    })
        .style("fill", 'none')
        .attr("stroke", '#ccc')

    testGraph.selectAll("g")
        .data(root.descendants())
        .enter()
        .append("g")
        .attr("transform", function(d) {
          return "translate(" + d.y + "," + d.x + ")"
        })
        /*.append("circle")
        .attr("name", d =>  {
            console.log(d.data.target)
            return(d.data.target) })
        .attr("r", 7)
        .style("fill", "#69b3a2")
        .attr("stroke", "black")
        .style("stroke-width", 2)*/
        .append("text")
        .text(d=>d.data.target)




    /* testGraph.select("text")
         .text(nodes[d.index].name)
         .style("fill",colorScale(nodes[d.index].name))*/


  });


  let getGradID = chord => `linkGrad-${chord.source.index}-${chord.target.index}`;

  var grads = d3.select("#chord").append("defs")
      .selectAll("linearGradient")
      .data(chords)
      .join("linearGradient")
      .attr("id", getGradID)
      .attr("gradientUnits", "userSpaceOnUse")  // use the coordinate system of whatever is being filled
      .attr("x1", d => radius * Math.cos((d.source.endAngle-d.source.startAngle) / 2 + d.source.startAngle - Math.PI/2) )
      .attr("y1", d => radius * Math.sin((d.source.endAngle-d.source.startAngle) / 2 + d.source.startAngle - Math.PI/2) )
      .attr("x2", d => radius * Math.cos((d.target.endAngle-d.target.startAngle) / 2 + d.target.startAngle - Math.PI/2) )
      .attr("y2", d => radius * Math.sin((d.target.endAngle-d.target.startAngle) / 2 + d.target.startAngle - Math.PI/2) )
  grads.append("stop")
      .attr("offset", "0%")
      .attr("stop-color", d => colorScale(nodes[ d.source.index ].name) )
  grads.append("stop")
      .attr("offset", "100%")
      .attr("stop-color", d => colorScale(nodes[ d.target.index ].name) )



}

drawChord();

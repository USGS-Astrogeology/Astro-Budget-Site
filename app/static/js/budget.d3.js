function projectBudgetDashboard(id, bData){
    var barColor = 'steelblue';
    var fundingColor = 'green';
    // function segColor(c){ return {low:"#807dba", mid:"#e08214",high:"#41ab5d"}[c]; }
    // function segColor(c){ return {expenses:"firebrick", staffing:"CornFlowerBlue",travel:"purple",equipment:"maroon",overhead:"OliveDrab"}[c]; }
    function segColor(c){ return {expenses:"cadetblue", staffing:"chocolate",travel:"darkseagreen",equipment:"goldenrod",overhead:"OliveDrab"}[c]; }
    
    // compute total for each expense type.
    bData.forEach(function(d){
        d.total = (d.costs.expenses+d.costs.staffing+d.costs.travel+d.costs.overhead+d.costs.equipment).toFixed(3);});
    
    // function to handle histogram.
    function histoGram(fD){
        var hG={},    hGDim = {t: 80, r: 0, b: 30, l: 0};
        // hGDim.w = 500 - hGDim.l - hGDim.r, 
        hGDim.w = (120 * fD.length) - hGDim.l - hGDim.r, 
        hGDim.h = 250 - hGDim.t - hGDim.b;
            
        //create svg for histogram.
        var hGsvg = d3.select(id).append("svg")
            .attr("width", hGDim.w + hGDim.l + hGDim.r)
            .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
            .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

        // create function for x-axis mapping.
        var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
                .domain(fD.map(function(d) { return d[0]; }));

        // Add x-axis to the histogram svg.
        hGsvg.append("g").attr("class", "x axis")
            .attr("transform", "translate(0," + hGDim.h + ")")
            .call(d3.svg.axis().scale(x).orient("bottom"));

        // Create function for y-axis map.
        var y = d3.scale.linear().range([hGDim.h, 0])
                .domain([0, d3.max(fD, function(d) { return d[1]; })]);

        // Create bars for histogram to contain rectangles and costs labels.
        var bars = hGsvg.selectAll(".bar").data(fD).enter()
                .append("g").attr("class", "bar");
        
        //create the expense rectangles.
        bars.append("rect")
            .attr("x", function(d) { return x(d[0]); })
            .attr("y", function(d) { return y(d[1]); })
            .attr("width", x.rangeBand()/2)
            .attr("height", function(d) { return hGDim.h - y(d[1]); })
            .attr('fill',barColor)
            .on("mouseover",mouseover)// mouseover is defined below.
            .on("mouseout",mouseout);// mouseout is defined below.
            
        //Create the costs labels above the rectangles.
        // bars.append("text").text(function(d){ return "-$" + d3.format(",.2f")(d[1])})
        bars.append("text").text(function(d){ return d3.format("$,.3s")(d[1])})
            // .attr("transform", "rotate(90)")
            .attr("x", function(d) { return x(d[0])+x.rangeBand()/4; })
            .attr("y", function(d) { return y(d[1]/2); })
            .style("font-size", "12px")
            .attr('fill',"black")
            .attr('font-weight', "bold")
            .attr("text-anchor", "middle");
        
        //create the funding rectangles.
        bars.append("rect")
            .attr("x", function(d) { return x(d[0])+(x.rangeBand()/2); })
            .attr("y", function(d) { return y(d[2]); })
            .attr("width", x.rangeBand()/2)
            .attr("height", function(d) { return hGDim.h - y(d[2]); })
            .attr('fill', function(d) { if (d[1] > d[2]) { return 'firebrick';} else { return 'darkolivegreen'; }})
            .on("mouseover",mouseover)// mouseover is defined below.
            .on("mouseout",mouseout);// mouseout is defined below.
            
        //Create the funding labels above the rectangles.
        // bars.append("text").text(function(d){ return "+$" + d3.format(",.2f")(d[2])})
        bars.append("text").text(function(d){ return d3.format("$,.3s")(d[2])})
            // .attr("transform", "rotate(90)")
            .attr("x", function(d) { return x(d[0])+(0.75 * x.rangeBand()); })
            .attr("y", function(d) { return y(d[2]/3); })
            .style("font-size", "12px")
            .attr('fill',"black")
            .attr('font-weight', "bold")
            .attr("text-anchor", "middle");
        
        function mouseover(d){  // utility function to be called on mouseover.
            // filter for selected state.
            var st = bData.filter(function(s){ return s.fy == d[0];})[0],
                nD = d3.keys(st.costs).map(function(s){ return {type:s, costs:st.costs[s]};});
               
            // call update functions of pie-chart and legend.    
            pC.update(nD);
            leg.update(nD);
        }
        
        function mouseout(d){    // utility function to be called on mouseout.
            // reset the pie-chart and legend.    
            pC.update(tF);
            leg.update(tF);
        }
        
        // create function to update the bars. This will be used by pie-chart.
        hG.update = function(nD, color){
            // update the domain of the y-axis map to reflect change in costs.
            //y.domain([0, d3.max(nD, function(d) { return d[1]; })]);
            
            // Attach the new data to the bars.
            var bars = hGsvg.selectAll(".bar").data(nD);
            
            // transition the height and color of rectangles.
            bars.select("rect").transition().duration(500)
                .attr("y", function(d) {return y(d[1]); })
                .attr("height", function(d) { return hGDim.h - y(d[1]); })
                .attr("fill", color);

            // transition the frequency labels location and change value.
            bars.select("text").transition().duration(500)
             // .attr("y", function(d) {return y(d[1])-5; });            
                .text(function(d){ return "$" + d3.format(",.3s")(d[1])})
                .attr("y", function(d) { return y(d[1]/3); })
        }        
        return hG;
    }
    
    // function to handle pieChart.
    function pieChart(pD){
        var pC ={},    pieDim ={w:250, h: 250};
        pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;
                
        // create svg for pie chart.
        var piesvg = d3.select(id).append("svg")
            .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
            .attr("transform", "translate("+pieDim.w/2+","+pieDim.h/2+")");
        
        // create function to draw the arcs of the pie slices.
        var arc = d3.svg.arc().outerRadius(pieDim.r - 10).innerRadius(0);

        // create a function to compute the pie slice angles.
        var pie = d3.layout.pie().sort(null).value(function(d) { return d.costs; });

        // Draw the pie slices.
        piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
            .each(function(d) { this._current = d; })
            .style("fill", function(d) { return segColor(d.data.type); })
            .on("mouseover",mouseover).on("mouseout",mouseout);

        // create function to update pie-chart. This will be used by histogram.
        pC.update = function(nD){
            piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
                .attrTween("d", arcTween);
        }        
        // Utility function to be called on mouseover a pie slice.
        function mouseover(d){
            // call the update function of histogram with new data.
            hG.update(bData.map(function(v){ 
                return [v.fy,v.costs[d.data.type]];}),segColor(d.data.type));
        }
        //Utility function to be called on mouseout a pie slice.
        function mouseout(d){
            // call the update function of histogram with all data.
            hG.update(bData.map(function(v){
                return [v.fy,v.total];}), barColor);
        }
        // Animating the pie-slice requiring a custom function which specifies
        // how the intermediate paths should be drawn.
        function arcTween(a) {
            var i = d3.interpolate(this._current, a);
            this._current = i(0);
            return function(t) { return arc(i(t));    };
        }    
        return pC;
    }
    
    // function to handle legend.
    function legend(lD){
        var leg = {};
            
        // create table for legend.
        var legend = d3.select(id).append("table").attr('class','legend');
        
        // create one row per segment.
        var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");
            
        // create the first column for each segment.
        tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
            .attr("width", '16').attr("height", '16')
      .attr("fill",function(d){ return segColor(d.type); });
            
        // create the second column for each segment.
        tr.append("td").text(function(d){ return d.type;});

        // create the third column for each segment.
        tr.append("td").attr("class",'legendCosts')
            .text(function(d){ return "$" + d3.format(",.2f")((d.costs).toFixed(3));});

        // create the fourth column for each segment.
        tr.append("td").attr("class",'legendPerc')
            .text(function(d){ return getLegend(d,lD);});

        // Utility function to be used to update the legend.
        leg.update = function(nD){
            // update the data attached to the row elements.
            var l = legend.select("tbody").selectAll("tr").data(nD);

            // update the costs.
            l.select(".legendCosts").text(function(d){ return "$" + d3.format(",.2f")((d.costs).toFixed(3));});

            // update the percentage column.
            l.select(".legendPerc").text(function(d){ return getLegend(d,nD);});        
        }
        
        function getLegend(d,aD){ // Utility function to compute percentage.
            return d3.format("%")(d.costs/d3.sum(aD.map(function(v){ return v.costs; })));
        }

        return leg;
    }

    function netTable (sF) {
      var tablecontents = "<TABLE>";
      
    }
    
    // calculate total frequency by segment for all state.
    var tF = ['expenses','staffing','travel','overhead','equipment'].map(function(d){ 
        return {type:d, costs: d3.sum(bData.map(function(t){ return t.costs[d];}))}; 
    });    
    
    // calculate total frequency by state for all segment.
    var sF = bData.map(function(d){return [d.fy,d.total,d.funding];});

    var hG = histoGram(sF), // create the histogram.
        pC = pieChart(tF), // create the pie-chart.
        leg= legend(tF);  // create the legend.
}

function deleteProjectBudgetDashboard(id){
  var tF = [];
  var hG = [];
  var pC = [];
  var leg = [];

  d3.select("svg").remove();
  d3.select(id + 'Table').innerHTML = "TEST";

}

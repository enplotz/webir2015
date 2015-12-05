var Container = function (pDiv, clickFunc) {
    var public = this;

    var __div;

    var __nodeData;
    var __nodeString; 
    var __linkData;
    var __nodeVis;
    var __linkVis;

    var __canvas;
    var __colorScale; 
    var __force;
    var tmp1;
    var tmp2;

    function __init() {
        __div = pDiv;
        __nodeData = [];
        __linkData = [];
        __initGraphics()
    }

    function __initGraphics() {
        var rect = d3.select(__div).node().getBoundingClientRect();
        var svg = d3.select(__div).append('svg')
            .attr("preserveAspectRatio", "xMinYMin meet")
            .attr("viewBox", "0 0 " + rect.width + " " + rect.height)
            .attr("class", "svgResponsive");
        __canvas = svg.append('g'); //.attr('transform', 'translate(' + (rect.width / 2) + ',' + (rect.height / 2) + ')');
        __canvas.append('rect').attr('width', '95%').attr('height', '95%').attr('fill', 'white').attr('opacity', 0.2);

        __colorScale = d3.scale.linear().domain([0,50]).range(['#FFCC99', '#FF6600']); 
        __force = d3.layout.force()
            .linkStrength(2)
            .distance(120)
            .charge(-2500)
            .size([rect.width, rect.height])
            .on('tick', __tick);
        __nodeData  = __force.nodes();
        __linkData =  __force.links(); 
        __force.drag()
            .on("dragstart", function (d) {
                __nodeData.forEach(function (di) {
                    di.fixed = false;
                });
                d.fixed = true;
            });



    }

    function __tick() {
        __nodeVis.attr("transform", function (d) {
            return 'translate(' + d.x + ',' + d.y + ')';
        });
        __linkVis.attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

    }

    function __addNodes(newNodes) {
         
         newNodes.forEach(function(n){
             if (n.hasOwnProperty('links')){
                n.links.forEach(function(l){
                    __linkData.push({source: Math.min(l,n.id)-1, target: Math.max(l,n.id)-1})
                }); 
                delete n.links;
             }
             console.log(__linkData); 
             __nodeData.push(n);
         }); 
        
        __linkVis = __canvas.selectAll('.link').data(__linkData)
        var linkEnter = __linkVis.enter().append('line').attr('class', 'link'); 
        __nodeVis = __canvas.selectAll('.nodeContainer').data(__nodeData, function(d){return d.id}); 
        var nodeEnter = __nodeVis
            .enter().append('g').attr('class', 'nodeContainer').call(__force.drag);
        nodeEnter.append('circle').attr('r', 35).attr('fill', function(d){return __colorScale(d.h)}).attr('opacity', 0.5).attr('stroke', 'black')
        nodeEnter.append('rect').attr('width', 68).attr('height', 20).attr('transform', 'translate(-34,-10)').attr('fill', 'white').attr('opacity', 0.9).attr('stroke', 'none');
        nodeEnter.append('text').attr('transform', 'translate(0,4)').text(function (d) {
            return d.name;
        });
        
        
        
       
        __nodeVis.on('click', function (d) {
             if (d3.event.defaultPrevented) return;
                clickFunc({clicked:d.id, all:__nodeString});
        });
        __nodeVis.exit().remove();
        
       __canvas.selectAll('.nodeContainer').each(function(){
           
           this.parentNode.appendChild(this); 
       }); 
        
        __linkVis.exit().remove(); 
         __nodeString = "" 
         __nodeData.forEach(function(el){ __nodeString+=el.id+',';}); 
        __nodeString = __nodeString.slice(0,-1); 
        __force.on('tick', __tick); 
         __force.start();
        //tmp1.exit().transition(700).remove();
    }

    public.addNodes = function (n,src) {
        __addNodes(n,src);
    }
    public.clear = function () {
        __linkVis.remove();
        __nodeVis.remove();

        __linkData = [];
        __nodeData = [];
        __force.nodes([]).links([]);
    };
    __init()


}
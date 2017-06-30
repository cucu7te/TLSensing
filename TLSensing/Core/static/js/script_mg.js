/**
 *
 */

jQuery.fn.extend({
    disable: function(state) {
        return this.each(function() {
            var $this = $(this);
            if($this.is('input, button, textarea, select'))
              this.disabled = state;
            else
              $this.toggleClass('acquiring', state);
              $this.toggleClass('disabled', state);
        });
    }
});

function notifications_handle(msg) {
  console.log("REDIS notifications: " + msg);
  json = $.parseJSON(msg);
  if(json.msg != null){
    notify("Notification for mote '" + json.mote + "': " + json.msg, false)
  }
}

function notify(msg, persistent) {
  if(persistent) {
    toastr.options = {
      "closeButton": true,
      "debug": false,
      "newestOnTop": false,
      "progressBar": false,
      "positionClass": "toast-bottom-full-width",
      "preventDuplicates": false,
      "onclick": null,
      "showDuration": "300",
      "hideDuration": "1000",
      "timeOut": 0,
      "extendedTimeOut": 0,
      "showEasing": "swing",
      "hideEasing": "linear",
      "showMethod": "fadeIn",
      "hideMethod": "fadeOut",
      "tapToDismiss": false
    }
  } else {
    toastr.options = {
      "closeButton": false,
      "debug": false,
      "newestOnTop": false,
      "progressBar": false,
      "positionClass": "toast-bottom-full-width",
      "preventDuplicates": false,
      "onclick": null,
      "showDuration": "300",
      "hideDuration": "1000",
      "timeOut": "10000",
      "extendedTimeOut": "1000",
      "showEasing": "swing",
      "hideEasing": "linear",
      "showMethod": "fadeIn",
      "hideMethod": "fadeOut"
    }
  }
  toastr["info"](msg)
}

function parseForm(category, mote_id){
  result = new Array();
  $("#m-" + category + "-" + mote_id + " form").find('input').each(function(){
    var obj = {};
    obj.key = $(this).attr('id');
    obj.val = $(this).val();
    if(obj.key != undefined && obj.val != undefined){
      obj.key = obj.key.substring('input-'.length + mote_id.length + '-'.length);
      result.push( obj );
    }
  });
  return result;
}

function setProgressVisible(visible, json) {
  if(visible != undefined) {
    if(visible) {
      $(".pbar-container").each(function() {
        $(this).show();
      })
      $(".pbar-content").each(function() {
        $(this).css("width", "0%");
        $(this).removeClass("progress-bar-success");
      });
      $(".pbar-content .progress_label").each(function() {
        $(this).text("");
      });
    } else {
      if(json != undefined) {
        $(".pbar-content").each(function() {
          $(this).addClass("progress-bar-" + json["pbar_class"]);
        });
        $(".pbar-content .progress_label").each(function() {
          $(this).text(json["pbar_msg"]);
        });
        setControlsStatus(true);
        setTimeout(function() {
          toastr.clear();
          $(".pbar-container").each(function() {
            $(this).hide();
          });
        }, 10000);
      }
    }
  }
}

function setProgressBarStatus(progress, text) {
  $(".pbar-content").each(function() {
    $(this).css("width", progress + "%");
  });
  $(".pbar-content .progress_label").each(function() {
    $(this).text(text);
  });
}

function setControlsStatus(value) {
  if(value != undefined) {
    if(value) {
      $(".avo-link").disable(false);
      $(".poll-link").each(function() {
        $(this).disable(false);
      });
    } else {
      $(".avo-link").disable(true);
      $(".poll-link").each(function() {
        $(this).disable(true);
      });
    }
  }
}

/* */

function loadDoc(url, dest, method) {
    if (typeof(method)==='undefined') method = "GET";
    $.ajax({
        type: method,
        url: url,
        success: function(msg) {
            $(dest).html(msg);
        },
        error: function(ts) {
            alert("Errore! " + ts.statusText);
        }
    });
}

function ajaxRequest(method, url, data, destdiv, postfunction, pleasewait) {
    if(pleasewait == undefined || pleasewait == true) {
        $(destdiv).html("<div class='text-center'><h1>Please wait...</h1></div>");
    }
    
    $.ajax({
        type: method,
        url: url,
        data: JSON.stringify(data),
        beforeSend: function(xhr, settings) {
            if (method == "POST") {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        },
        success: function(msg) {
            //alert(msg);
            $(destdiv).html(msg);
            if(postfunction != undefined) {
                postfunction();
            }
        },
        error: function(err) {
          //alert(msg);
            $(destdiv).html("Error! " + err.responseText);
           //alert(err);
        }
    });
}

function getCookie(name) {
var cookieValue = null;
if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
}
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
console.log(csrftoken);

//Ajax call
function csrfSafeMethod(method) {
// these HTTP methods do not require CSRF protection
return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function update_motecontent(mote_id) {
//Most Recent Values
  ajaxRequest("GET", "/data/history/" + mote_id + "/1/list", {}, "#mrv-" + mote_id);
  
  //Measures Accordion
  ajaxRequest("GET", "/data/history/" + mote_id + "/10/table", {}, "#accordion-history-" + mote_id + " .panel-body");

  //Statistics Accordion
  ajaxRequest("GET", "/data/stats/" + mote_id, {}, "#accordion-stats-" + mote_id + " .panel-body");

  //Notifications Accordion
  ajaxRequest("GET", "/data/notifications/" + mote_id, {}, "#accordion-notifications-" + mote_id + " .panel-body");

  chart_types = ["base", "acc", "acc_details"]
  for (i = 0; i < chart_types.length; i++) {
    if(document.getElementById("#accordion-" + chart_types[i] + "-" + mote_id)) {
      ajaxRequest("GET", "/data/chart/" + mote_id + "/" + chart_types[i], {}, "#accordion-" + chart_types[i] + "-" + mote_id + " .panel-body");
    }
  }
}

// Topology
function showImageMotes(){
  $('#topology-status').text("Loading RPL Routing...");

  var n_dots = 1;
  setTimeout(function() {
        $(document).ready(function(){
          $.ajax({
            dataType: "json",
            url: "http://" + document.URL.split('/')[2].split(":")[0] + ":8080/routing/dag",
            success: updateForData,
          //  async:true,
         //   global:false,
          });
        });
  }, 2000);
}

function searchNode(nodes, node_id) {
  toRet = null
  nodes.forEach(function(node) { 
    if(node["id"] == node_id) { 
      toRet = node
    }
  });
  return toRet
}

function explore(startNodes, states, edgesOrig) {
  console.log("Nodes: " + startNodes)
  //Foreach node, search edges
  foundEdges = []
  startNodes.forEach(function(node) {
    foundEdges = foundEdges.concat($.grep(edgesOrig, function(e){ return e.v === node.id }));
  });
  newStates = []
  foundEdges.forEach(function(edge) {
    newStates.push(searchNode(states, edge["u"]))
  });
  if(foundEdges.length > 0) {
    allNodes = explore(newStates, states, edgesOrig);
    console.log(allNodes)
    return startNodes.concat(allNodes);
  } else {
    return startNodes;
  }
}

function updateForData(json) {
  //json = {"states": [{"id": "ED31", "value": {"label": "ED31"}}, {"id": "9F1A", "value": {"label": "9F1A"}}, {"id": "ECDC", "value": {"label": "ECDC"}}, {"id": "ED94", "value": {"label": "ED94"}}, {"id": "ED4B", "value": {"label": "ED4B"}}, {"id": "ED84", "value": {"label": "ED84"}}], "edges": [{"u": "ECDC", "v": "ED94"}, {"u": "ED84", "v": "9F1A"}, {"u": "9F1A", "v": "ECDC"}, {"u": "ED31", "v": "9F1A"}, {"u": "ED4B", "v": "9F1A"}]}

  for (var i = 0; i <= 3; i++) {
    var svg = d3.select("svg");
    svg.selectAll("*").remove();

    var states = json.states;
    var edges = json.edges;
    /*
    var states = []
    var edgesOrig = json.edges;

    //Filter graph
    json["states"].forEach(function(node) { 
      if(node["id"] == "ED94") { 
        states.push(node) 
      }
    });

    nodes = explore(states, edgesOrig);

    do {
      foundEdges = [];
      lastNodeFound = states[states.length - 1];
      //Search for edges
      
      
    } while(foundEdges != [])
    */

    // Create the input graph
    var g = new dagreD3.graphlib.Graph().setGraph({});

    states.forEach(function(state) {
      g.setNode(state.id, { style: "fill: #afa" });
    });

    edges.forEach(function(edge) {
      g.setEdge(edge.u, edge.v, {
        lineInterpolate: 'basis' 
      });
    });

    g.nodes().forEach(function(v) {
      var node = g.node(v);
      // Round the corners of the nodes
      node.rx = node.ry = 5;
    });

    // Create the renderer
    var render = new dagreD3.render();

    // Set up an SVG group so that we can translate the final graph.
    var inner = svg.append("g");

    // Run the renderer. This is what draws the final graph.
    render(inner, g);
    var styleTooltip = function(name, description) {
      return "<p class='name'>" + name + "</p><p class='description'>" + description + "</p>";
    };

    inner.selectAll("g.node")
      .attr("title", function(v) { return styleTooltip(v, "") })
      .each(function(v) { $(this).tipsy({ gravity: "w", opacity: 1, html: true }); });

    // Center the graph
    var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
    inner.attr("transform", "translate(" + xCenterOffset + ", 20)");
      d3.select("svg")
          .attr("width", g.graph().width + 40)
          .attr("height", g.graph().height + 40);
  }
  $('#topology-status').text("Current RPL Routing");

  if(($("#topologia").data('bs.modal') || {}).isShown) {
    timeoutId = setTimeout(function() {
        $('#topology-status').text("Loading RPL Routing...");
        $.ajax({
            dataType: "json",
            url: "http://" + document.URL.split('/')[2].split(":")[0] + ":8080/routing/dag",
            success: updateForData,
        });
    }, 5000);
  }
}
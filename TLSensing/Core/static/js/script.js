$(document).ready(function(){

  $.ajax({
    type: "GET",
    url: "/motes",
  }).done(function(data) { //console.log(data);
    $("#motes").html(data);
  }).fail(function(data){
    alert(data.responseText);
  });

  $("#add_mote_form").submit(function(event){
    event.preventDefault();
    $.ajax({
      type: "POST",
      url: "/motes",
      data: $("#add_mote_form").serialize()
    }).done(function(data) {
      $("#motes").html(data);
      //console.log(data);
      $("#close_modal").click();
      $.notify("Mote added", {
        style: 'alert',
        className: 'alert_info'
      });

      $("#maxt").html('-');   //added to write '-' on table
      $("#mint").html('-');
      $("#averaget").html('-');

      $("#maxh").html('-');   //added to write '-' on table
      $("#minh").html('-');
      $("#averageh").html('-');

      $("#maxl").html('-');   //added to write '-' on table
      $("#minl").html('-');
      $("#averagel").html('-');

      $("#maxax").html('-');   //added to write '-' on table
      $("#minax").html('-');
      $("#averageax").html('-');

      $("#maxay").html('-');   //added to write '-' on table
      $("#minay").html('-');
      $("#averageay").html('-');

      $("#maxaz").html('-');   //added to write '-' on table
      $("#minaz").html('-');
      $("#averageaz").html('-');

    }).fail(function(data){
      $.notify(data.responseText, {
        style: 'alert',
        className: 'alert_error'
      });
    });
  });
});

$.notify.addStyle('alert', {
  html: "<div data-notify-text></div>",
  classes: {
    base: {
      "padding": "8px 35px 8px 14px",
      "margin-bottom": "18px",
      "color": "#c09853",
      "text-shadow": "0 1px 0 rgba(255, 255, 255, 0.5)",
      "background-color": "#fcf8e3",
      "border": "1px solid #fbeed5",
      "-webkit-border-radius": "4px",
      "-moz-border-radius": "4px",
      "border-radius": "4px",
      "font-weight" : "900",
    },
    alert_error: {
      "color": "#b94a48",
      "background-color": "#f2dede",
      "border-color": "#eed3d7",
      "margin-top": "60px",
    },
    alert_info: {
      "color": "#32CD32",
      "background-color": "#dafdda",
      "border-color": "#3cb371",
      "margin-top": "60px",
    }
  }
});

//////////////////////////////////////////////////////////////////////////////////////////////////////////
//function to authenticate the administrator
function logIn(){
  //1)serve una espressione che debba in qualch modo far riferimento a $("# password field").val(), argomento da inviare con la post
  //2)provare a vedere il metodo richiamato sul click del pulsante Add in fase di registrazione di un mote e capire come poter passare
  //  l'argomento sopra citato all'interno della richiesta e più in generale del metodo (si trova in templates/ajax_admin_motes.html)
  $.ajax({
    type: "POST",
    url: "/admn/log",
  }).done(function(data) { //console.log(data);
    //$("#motes").html(data);
    alert("Successful!");
  }).fail(function(data){
    //alert(data.responseText);
    alert("Error!");
  });
};

//////////////////////////////////////////////////////////////////////////////////////////////////////////
//function to process the data from msg
function receiveMessage(msg) {
  if(msg.length > 0)
  {
    json = $.parseJSON(msg);

    json.motes.forEach(function(mote){
      //last received value
      if (mote.measures.length > 0){
  	    var last_element = mote.measures[mote.measures.length - 1];
      	//var dateString = moment(last_element.date.$date - 7200).format('DD MMM, H:m'); //old versione =>ERROR
        var date_now = new Date(last_element.date.$date -7200000);                                              //new version of date format
        var dateString0 = ((date_now.toLocaleDateString()).concat(', ')).concat(date_now.toLocaleTimeString()); //new version of date format
      	if(dateString0.substring(1,2) == '/') {
          var zero = '0';
          var dateString1 = zero.concat(dateString0);
        }
        else {
          var dateString1 = dateString0;
        }
        if(dateString1.substring(5,6) != '/') {                                                                 //new version of date format
          var dateString = ((dateString1.substring(0,3)).concat(0)).concat(dateString1.substring(3));           //new version of date format
        }
        else{
          var dateString =  dateString1;                                                                        //new version of date format
        }
        $("#last_measure_date-"+mote._id.$oid).html(dateString);
      	$("#last_measure_temp-"+mote._id.$oid).html(last_element.temperature);
      	$("#last_measure_humi-"+mote._id.$oid).html(last_element.humidity);
      	$("#last_measure_light-"+mote._id.$oid).html(last_element.light);
        //notifiche
        if (mote.notifications != null) {
          $("#notifications_body-"+mote._id.$oid).html("");
          mote.notifications.forEach(function(notification){
            $("#notifications_body-"+mote._id.$oid).append('<tr><td>'+notification.type + " </td><td> " + notification.message+'</td></tr>');
          });
        }

        //definition
        //hystoric values
        $("#history_body-"+mote._id.$oid).html("");
        mote.measures.forEach(function(measure){
          //var date = moment(measure.date.$date).format("DD MMM, H:m");  //last version
          var d_now = new Date(measure.date.$date - 7200000); //new version of date format
          var dString0 = ((d_now.toLocaleDateString()).concat(', ')).concat(d_now.toLocaleTimeString()); //new version of date format
          if(dString0.substring(1,2) == '/') {
            var zero = '0';
            var dString1 = zero.concat(dString0);
          }
          else {
            var dString1 = dString0;
          }
          if(dString1.substring(5,6) != '/') { //new version of date format
            var date = ((dString1.substring(0,3)).concat(0)).concat(dString1.substring(3)); //new version of date format
          }
          else{
            var date =  dString1;  //new version of date format
          }
          $("#history_body-"+mote._id.$oid).append("<tr>")
          $("#history_body-"+mote._id.$oid).append("<td>"+date+"</td><td>"+measure.temperature+"</td><td>"+measure.humidity+"</td><td>"+measure.light+"</td>");
          if (mote.mote_type == "OpenMote"){
    	      $("#history_body-"+mote._id.$oid).append ("<td>"+measure.accel_x+"</td><td>"+measure.accel_y+"</td><td>"+measure.accel_z+"</td>");
          }
          $("#history_body-"+mote._id.$oid).append("</tr>");
        });

        $("#base_chart-"+mote._id.$oid).html('<embed style="width: 100%"  src="/chart/'+mote._id.$oid+'/base" />');
        if(mote.mote_type == "OpenMote"){
    	    $("#last_measure_acc_x-"+mote._id.$oid).html(last_element.accel_x);
        	$("#last_measure_acc_y-"+mote._id.$oid).html(last_element.accel_y);
        	$("#last_measure_acc_z-"+mote._id.$oid).html(last_element.accel_z);
          $("#acc_chart-"+mote._id.$oid).html('<embed style="width: 100%"  src="/chart/'+mote._id.$oid+'/acc" />');
          $("#acc_details_chart-"+mote._id.$oid).html('<embed style="width: 100%"  src="/chart/'+mote._id.$oid+'/acc_details" />');
      	}
      }

      /*if (mote.meta_model != null){
        //values
        $("#meta_model_max_temp-"+mote._id.$oid).html(mote.meta_model.max_temp);
        $("#meta_model_min_temp-"+mote._id.$oid).html(mote.meta_model.min_temp);
        $("#meta_model_avg_temp-"+mote._id.$oid).html(mote.meta_model.avg_temp);

        $("#meta_model_max_humi-"+mote._id.$oid).html(mote.meta_model.max_humi);
        $("#meta_model_min_humi-"+mote._id.$oid).html(mote.meta_model.min_humi);
        $("#meta_model_avg_humi-"+mote._id.$oid).html(mote.meta_model.avg_humi);

        $("#meta_model_max_light-"+mote._id.$oid).html(mote.meta_model.max_light);
        $("#meta_model_min_light-"+mote._id.$oid).html(mote.meta_model.min_light);
        $("#meta_model_avg_light-"+mote._id.$oid).html(mote.meta_model.avg_light);
        $("#base_chart-"+mote._id.$oid).html('<embed style="width: 100%"  src="/chart/'+mote._id.$oid+'/base" />')

        if(mote.mote_type == "OpenMote"){
          $("#meta_model_max_acc_x-"+mote._id.$oid).html(mote.meta_model.max_acc_x);
          $("#meta_model_min_acc_x-"+mote._id.$oid).html(mote.meta_model.min_acc_y);
          $("#meta_model_avg_acc_x-"+mote._id.$oid).html(mote.meta_model.avg_acc_z);

          $("#meta_model_max_acc_y-"+mote._id.$oid).html(mote.meta_model.max_acc_y);
          $("#meta_model_min_acc_y-"+mote._id.$oid).html(mote.meta_model.min_acc_y);
          $("#meta_model_avg_acc_y-"+mote._id.$oid).html(mote.meta_model.avg_acc_y);

          $("#meta_model_max_acc_z-"+mote._id.$oid).html(mote.meta_model.max_acc_z);
          $("#meta_model_min_acc_z-"+mote._id.$oid).html(mote.meta_model.min_acc_z);
          $("#meta_model_avg_acc_z-"+mote._id.$oid).html(mote.meta_model.avg_acc_z);
        }
      }*/
    });

    //calling function for calculate values for top table
    setTimeout(function(){Motes_date(json);},2000);
    console.log(json);

    $.notify('Values updated', {
      style: 'alert',
      className: 'alert_info',
    });
  }
}

/////////////////////////////////////////////////////////////////////////////////////////////////
//function to print temperature information in top-table
function Motes_date(obj)
{
  var MotesNow = new Array();

  //console.log(idDeiMotes);
  if(idDeiMotes.length >= 1)
  {
    //creating array with all motes in application
    obj.motes.forEach(function(mote) {
      idDeiMotes.forEach(function(idMote) {
        if(mote._id.$oid == idMote)
        {
          MotesNow.push(mote);
          //console.log(MotesNow);
        }
      });
    });

    //calling functions to print values on top table
    temperature_data(MotesNow);
    humidity_data(MotesNow);
    light_data(MotesNow);
    accx_data(MotesNow);
    accy_data(MotesNow);
    accz_data(MotesNow);
  }
}


//////////////////////////////////////////////////////////////////////////////////////////////////////
function temperature_data(vettMotes){
  //processing of temperatures values
  var alias_temperature = new Array();

  var date_max_temperature = new Array();
  var date_min_temperature = new Array();

  var max_temperatures = new Array();
  var min_temperatures = new Array();
  var avg_temperatures = new Array();

  vettMotes.forEach(function(mote) {
    alias_temperature.push(mote.alias_name);
    if(mote.measures.length > 0)
    {
      var measures_temperature = new Array();
      mote.measures.forEach(function(meas) {
        measures_temperature.push(meas.temperature);
      });

      //calculation of max values of eatch mote
      var maxT=Math.max(...measures_temperature);
      var minT=Math.min(...measures_temperature);
      var avgT=average(measures_temperature);

      //printing values on stat box of each mote
      $("#meta_model_max_temp-"+mote._id.$oid).html(maxT);
      $("#meta_model_min_temp-"+mote._id.$oid).html(minT);
      $("#meta_model_avg_temp-"+mote._id.$oid).html(avgT);

      var max_mote_temp;
      var max_date_mote_temp;
      var min_mote_temp;
      var min_date_mote_temp;

      mote.measures.forEach(function(meas) {
        if(meas.temperature == maxT)
        {
          max_mote_temp = (meas.temperature);
          var date_max_temperature0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
          var date_max_temperature1 = ((date_max_temperature0.toLocaleDateString()).concat(', ')).concat(date_max_temperature0.toLocaleTimeString()); //new version of date format
          if(date_max_temperature1.substring(1,2) == '/') {
            var zero = '0';
            var date_max_temperature2 = zero.concat(date_max_temperature1);
          }
          else {
            var date_max_temperature2 = date_max_temperature1;
          }
          if(date_max_temperature2.substring(5,6) != '/') {                                                                 //new version of date format
            max_date_mote_temp = ( ((date_max_temperature2.substring(0,3)).concat(0)).concat(date_max_temperature2.substring(3)) );           //new version of date format
          }
          else
          {
            max_date_mote_temp = (date_max_temperature2);                                                                        //new version of date format
          }
        }

        if(meas.temperature == minT)
        {
          min_mote_temp = (meas.temperature);
          var date_min_temperature0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
          var date_min_temperature1 = ((date_min_temperature0.toLocaleDateString()).concat(', ')).concat(date_min_temperature0.toLocaleTimeString()); //new version of date format
          if(date_min_temperature1.substring(1,2) == '/') {
            var zero = '0';
            var date_min_temperature2 = zero.concat(date_min_temperature1);
          }
          else {
            var date_min_temperature2 = date_min_temperature1;
          }
          if(date_min_temperature2.substring(5,6) != '/') {                                                                 //new version of date format
            min_date_mote_temp = ( ((date_min_temperature2.substring(0,3)).concat(0)).concat(date_min_temperature2.substring(3)) );           //new version of date format
          }
          else{
            min_date_mote_temp = (date_min_temperature2);                                                                        //new version of date format
          }
        }

        //array containing all measures
        avg_temperatures.push(average(measures_temperature));
      });

      max_temperatures.push(max_mote_temp);
      min_temperatures.push(min_mote_temp);
      date_max_temperature.push(max_date_mote_temp);
      date_min_temperature.push(min_date_mote_temp);
    }
  });

  console.log(max_temperatures);
  console.log(min_temperatures);

  //processing of new max data
  var max_index_temperature;
  var maxTemperature = Math.max(...max_temperatures);
  if(maxTemperature == -Infinity)
  {
    $("#maxt").html('-');
  }
  else
  {
    max_index_temperature = max_temperatures.indexOf(Math.max(...max_temperatures));
    $("#maxt").html(maxTemperature + " (" + alias_temperature[max_index_temperature] + " - " + date_max_temperature[max_index_temperature] + ")");
  }

  //processing of new min data
  var min_index_temperature;
  var minTemperature = Math.min(...min_temperatures);
  if(minTemperature == Infinity)
  {
    $("#mint").html('-');
  }
  else
  {
    min_index_temperature = min_temperatures.indexOf(Math.min(...min_temperatures));
    $("#mint").html(minTemperature + " (" + alias_temperature[min_index_temperature] + " - " + date_min_temperature[min_index_temperature] + ")");
  }

  //processing of new avg data
  if(avg_temperatures.length > 1)
  {
    $("#averaget").html(average(avg_temperatures));
  }
  else
  {
    $("#averaget").html('-');
  }
}

function humidity_data(vettMotes){
  //processing of temperatures values
  var alias_humidity = new Array();

  var date_max_humidity = new Array();
  var date_min_humidity = new Array();

  var max_humidities = new Array();
  var min_humidities = new Array();
  var avg_humidities = new Array();

  vettMotes.forEach(function(mote) {
    alias_humidity.push(mote.alias_name);
    if(mote.measures.length > 0)
    {
      var measures_humidity = new Array();
      mote.measures.forEach(function(meas) {
        measures_humidity.push(meas.humidity);
      });

      //calculation of max values of eatch mote
      var maxH=Math.max(...measures_humidity);
      var minH=Math.min(...measures_humidity);
      var avgH=average(measures_humidity);

      //printing values on stat box of each mote
      $("#meta_model_max_humi-"+mote._id.$oid).html(maxH);
      $("#meta_model_min_humi-"+mote._id.$oid).html(minH);
      $("#meta_model_avg_humi-"+mote._id.$oid).html(avgH);

      var max_mote_humi;
      var max_date_mote_humi;
      var min_mote_humi;
      var min_date_mote_humi;

      mote.measures.forEach(function(meas) {
        if(meas.humidity == maxH)
        {
          max_mote_humi = (meas.humidity);
          var date_max_humidity0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
          var date_max_humidity1 = ((date_max_humidity0.toLocaleDateString()).concat(', ')).concat(date_max_humidity0.toLocaleTimeString()); //new version of date format
          if(date_max_humidity1.substring(1,2) == '/') {
            var zero = '0';
            var date_max_humidity2 = zero.concat(date_max_humidity1);
          }
          else {
            var date_max_humidity2 = date_max_humidity1;
          }
          if(date_max_humidity2.substring(5,6) != '/') {                                                                 //new version of date format
            max_date_mote_humi = ( ((date_max_humidity2.substring(0,3)).concat(0)).concat(date_max_humidity2.substring(3)) );           //new version of date format
          }
          else{
            max_date_mote_humi = (date_max_humidity2);                                                                        //new version of date format
          }
        }

        if(meas.humidity == minH)
        {
          min_mote_humi = (meas.humidity);
          var date_min_humidity0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
          var date_min_humidity1 = ((date_min_humidity0.toLocaleDateString()).concat(', ')).concat(date_min_humidity0.toLocaleTimeString()); //new version of date format
          if(date_min_humidity1.substring(1,2) == '/') {
            var zero = '0';
            var date_min_humidity2 = zero.concat(date_min_humidity1);
          }
          else {
            var date_min_humidity2 = date_min_humidity1;
          }
          if(date_min_humidity2.substring(5,6) != '/') {                                                                 //new version of date format
            min_date_mote_humi = ( ((date_min_humidity2.substring(0,3)).concat(0)).concat(date_min_humidity2.substring(3)) );           //new version of date format
          }
          else{
            min_date_mote_humi = (date_min_humidity2);                                                                        //new version of date format
          }
        }

        //array containing all measures
        avg_humidities.push(meas.humidity);
      });

      max_humidities.push(max_mote_humi);
      min_humidities.push(min_mote_humi);
      date_max_humidity.push(max_date_mote_humi);
      date_min_humidity.push(min_date_mote_humi);
    }
  });

  console.log(max_humidities);
  console.log(min_humidities);

  //processing of new max data
  var max_index_humidity;
  var maxHumidity = Math.max(...max_humidities);
  if(maxHumidity == -Infinity)
  {
    $("#maxh").html('-');
  }
  else
  {
    max_index_humidity= max_humidities.indexOf(Math.max(...max_humidities));
    $("#maxh").html(maxHumidity + " (" + alias_humidity[max_index_humidity] + " - " + date_max_humidity[max_index_humidity] + ")");
  }

  //processing of new min data
  var min_index_humidity;
  var minHumidity = Math.min(...min_humidities);
  if(minHumidity == Infinity)
  {
    $("#minh").html('-');
  }
  else
  {
    min_index_humidity = min_humidities.indexOf(Math.min(...min_humidities));
    $("#minh").html(minHumidity + " (" + alias_humidity[min_index_humidity] + " - " + date_min_humidity[min_index_humidity] + ")");
  }

  //processing of new avg data
  if(avg_humidities.length > 1)
  {
    $("#averageh").html(average(avg_humidities));
  }
  else
  {
    $("#averageh").html('-');
  }
}


function light_data(vettMotes){
  //processing of temperatures values
  var alias_light = new Array();

  var date_max_light = new Array();
  var date_min_light = new Array();

  var max_lights = new Array();
  var min_lights = new Array();
  var avg_lights = new Array();

  vettMotes.forEach(function(mote) {
    alias_light.push(mote.alias_name);
    if(mote.measures.length > 0)
    {
      var measures_light = new Array();
      mote.measures.forEach(function(meas) {
        measures_light.push(meas.light);
      });

      //calculation of max values of eatch mote
      var maxL=Math.max(...measures_light);
      var minL=Math.min(...measures_light);
      var avgL=average(measures_light);

      //printing values on stat box of each mote
      $("#meta_model_max_light-"+mote._id.$oid).html(maxL);
      $("#meta_model_min_light-"+mote._id.$oid).html(minL);
      $("#meta_model_avg_light-"+mote._id.$oid).html(avgL);

      var max_mote_light;
      var max_date_mote_light;
      var min_mote_light;
      var min_date_mote_light;

      mote.measures.forEach(function(meas) {
        if(meas.light == maxL)
        {
          max_mote_light = (meas.light);
          var date_max_light0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
          var date_max_light1 = ((date_max_light0.toLocaleDateString()).concat(', ')).concat(date_max_light0.toLocaleTimeString()); //new version of date format
          if(date_max_light1.substring(1,2) == '/') {
            var zero = '0';
            var date_max_light2 = zero.concat(date_max_light1);
          }
          else {
            var date_max_light2 = date_max_light1;
          }
          if(date_max_light2.substring(5,6) != '/') {                                                                 //new version of date format
            max_date_mote_light = ( ((date_max_light2.substring(0,3)).concat(0)).concat(date_max_light2.substring(3)) );           //new version of date format
          }
          else{
            max_date_mote_light = (date_max_light2);                                                                        //new version of date format
          }
        }

        if(meas.light == minL)
        {
          min_mote_light = (meas.light);
          var date_min_light0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
          var date_min_light1 = ((date_min_light0.toLocaleDateString()).concat(', ')).concat(date_min_light0.toLocaleTimeString()); //new version of date format
          if(date_min_light1.substring(1,2) == '/') {
            var zero = '0';
            var date_min_light2 = zero.concat(date_min_light1);
          }
          else {
            var date_min_light2 = date_min_light1;
          }
          if(date_min_light2.substring(5,6) != '/') {                                                                 //new version of date format
            min_date_mote_light = ( ((date_min_light2.substring(0,3)).concat(0)).concat(date_min_light2.substring(3)) );           //new version of date format
          }
          else{
            min_date_mote_light = (date_min_light2);                                                                        //new version of date format
          }
        }

        //array containing all measures
        avg_lights.push(meas.light);
      });

      max_lights.push(max_mote_light);
      min_lights.push(min_mote_light);
      date_max_light.push(max_date_mote_light);
      date_min_light.push(min_date_mote_light);
    }
  });

  console.log(max_lights);
  console.log(min_lights);

  //processing of new max data
  var max_index_light;
  var maxLight = Math.max(...max_lights);
  if(maxLight == -Infinity)
  {
    $("#maxl").html('-');
  }
  else
  {
    max_index_light= max_lights.indexOf(Math.max(...max_lights));
    $("#maxl").html(maxLight + " (" + alias_light[max_index_light] + " - " + date_max_light[max_index_light] + ")");
  }

  //processing of new min data
  var min_index_light;
  var minLight = Math.min(...min_lights);
  if(minLight == Infinity)
  {
    $("#minl").html('-');
  }
  else
  {
    min_index_light = min_lights.indexOf(Math.min(...min_lights));
    $("#minl").html(minLight + " (" + alias_light[min_index_light] + " - " + date_min_light[min_index_light] + ")");
  }

  //processing of new avg data
  //processing of new avg data
  if(avg_lights.length > 1)
  {
    $("#averagel").html(average(avg_lights));
  }
  else
  {
    $("#averagel").html('-');
  }
}


function accx_data(vettMotes){
  //processing of temperatures values
  var alias_accx = new Array();

  var date_max_accx = new Array();
  var date_min_accx = new Array();

  var max_accsx = new Array();
  var min_accsx = new Array();
  var avg_accsx = new Array();

  vettMotes.forEach(function(mote) {
    if(mote.mote_type == "OpenMote")
    {
      alias_accx.push(mote.alias_name);
      if(mote.measures.length > 0)
      {
        var measures_accx = new Array();
        mote.measures.forEach(function(meas) {
          measures_accx.push(meas.accel_x);
        });

        //calculation of max values of eatch mote
        var maxAx=Math.max(...measures_accx);
        var minAx=Math.min(...measures_accx);
        var avgAx=average(measures_accx);

        //printing values on stat box of each mote
        $("#meta_model_max_acc_x-"+mote._id.$oid).html(maxAx);
        $("#meta_model_min_acc_x-"+mote._id.$oid).html(minAx);
        $("#meta_model_avg_acc_x-"+mote._id.$oid).html(avgAx);

        var max_mote_accx;
        var max_date_mote_accx;
        var min_mote_accx;
        var min_date_mote_accx;

        mote.measures.forEach(function(meas) {
          if(meas.accel_x == maxAx)
          {
            max_mote_accx = (meas.accel_x);
            var date_max_accx0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
            var date_max_accx1 = ((date_max_accx0.toLocaleDateString()).concat(', ')).concat(date_max_accx0.toLocaleTimeString()); //new version of date format
            if(date_max_accx1.substring(1,2) == '/') {
              var zero = '0';
              var date_max_accx2 = zero.concat(date_max_accx1);
            }
            else {
              var date_max_accx2 = date_max_accx1;
            }
            if(date_max_accx2.substring(5,6) != '/') {                                                                 //new version of date format
              max_date_mote_accx = ( ((date_max_accx2.substring(0,3)).concat(0)).concat(date_max_accx2.substring(3)) );           //new version of date format
            }
            else{
              max_date_mote_accx = (date_max_accx2);                                                                        //new version of date format
            }
          }

          if(meas.accel_x == minAx)
          {
            min_mote_accx = (meas.accel_x);
            var date_min_accx0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
            var date_min_accx1 = ((date_min_accx0.toLocaleDateString()).concat(', ')).concat(date_min_accx0.toLocaleTimeString()); //new version of date format
            if(date_min_accx1.substring(1,2) == '/') {
              var zero = '0';
              var date_min_accx2 = zero.concat(date_min_accx1);
            }
            else {
              var date_min_accx2 = date_min_accx1;
            }
            if(date_min_accx2.substring(5,6) != '/') {                                                                 //new version of date format
              min_date_mote_accx = ( ((date_min_accx2.substring(0,3)).concat(0)).concat(date_min_accx2.substring(3)) );           //new version of date format
            }
            else{
              min_date_mote_accx = (date_min_accx2);                                                                        //new version of date format
            }
          }

          //array containing all measures
          avg_accsx.push(meas.accel_x);
        });
      }

      max_accsx.push(max_mote_accx);
      min_accsx.push(min_mote_accx);
      date_max_accx.push(max_date_mote_accx);
      date_min_accx.push(min_date_mote_accx);
    }
  });

  console.log(max_accsx);
  console.log(min_accsx);

  //processing of new max data
  var max_index_accx;
  var maxaccX = Math.max(...max_accsx);
  if(maxaccX == -Infinity)
  {
    $("#maxax").html('-');
  }
  else
  {
    max_index_accx= max_accsx.indexOf(Math.max(...max_accsx));
    $("#maxax").html(maxaccX + " (" + alias_accx[max_index_accx] + " - " + date_max_accx[max_index_accx] + ")");
  }

  //processing of new min data
  var min_index_accx;
  var minaccX = Math.min(...min_accsx);
  if(minaccX == Infinity)
  {
    $("#minax").html('-');
  }
  else
  {
    min_index_accx = min_accsx.indexOf(Math.min(...min_accsx));
    $("#minax").html(minaccX + " (" + alias_accx[min_index_accx] + " - " + date_min_accx[min_index_accx] + ")");
  }

  //processing of new avg data
  if(avg_accsx.length > 1)
  {
    $("#averageax").html(average(avg_accsx));
  }
  else
  {
    $("#averageax").html('-');
  }
}


function accy_data(vettMotes){
  //processing of temperatures values
  var alias_accy = new Array();

  var date_max_accy = new Array();
  var date_min_accy = new Array();

  var max_accsy = new Array();
  var min_accsy = new Array();
  var avg_accsy = new Array();

  vettMotes.forEach(function(mote) {
    if(mote.mote_type == "OpenMote")
    {
      alias_accy.push(mote.alias_name);
      if(mote.measures.length > 0)
      {
        var measures_accy = new Array();
        mote.measures.forEach(function(meas) {
          measures_accy.push(meas.accel_y);
        });

        //calculation of max values of eatch mote
        var maxAy=Math.max(...measures_accy);
        var minAy=Math.min(...measures_accy);
        var avgAy=average(measures_accy);

        //printing values on stat box of each mote
        $("#meta_model_max_acc_y-"+mote._id.$oid).html(maxAy);
        $("#meta_model_min_acc_y-"+mote._id.$oid).html(minAy);
        $("#meta_model_avg_acc_y-"+mote._id.$oid).html(avgAy);

        var max_mote_accy;
        var max_date_mote_accy;
        var min_mote_accy;
        var min_date_mote_accy;

        mote.measures.forEach(function(meas) {
          if(meas.accel_y == maxAy)
          {
            max_mote_accy = (meas.accel_y);
            var date_max_accy0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
            var date_max_accy1 = ((date_max_accy0.toLocaleDateString()).concat(', ')).concat(date_max_accy0.toLocaleTimeString()); //new version of date format
            if(date_max_accy1.substring(1,2) == '/') {
              var zero = '0';
              var date_max_accy2 = zero.concat(date_max_accy1);
            }
            else {
              var date_max_accy2 = date_max_accy1;
            }
            if(date_max_accy2.substring(5,6) != '/') {                                                                 //new version of date format
              max_date_mote_accy = ( ((date_max_accy2.substring(0,3)).concat(0)).concat(date_max_accy2.substring(3)) );           //new version of date format
            }
            else{
              max_date_mote_accy = (date_max_accy2);                                                                        //new version of date format
            }
          }

          if(meas.accel_y == minAy)
          {
            min_mote_accy = (meas.accel_y);
            var date_min_accy0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
            var date_min_accy1 = ((date_min_accy0.toLocaleDateString()).concat(', ')).concat(date_min_accy0.toLocaleTimeString()); //new version of date format
            if(date_min_accy1.substring(1,2) == '/') {
              var zero = '0';
              var date_min_accy2 = zero.concat(date_min_accy1);
            }
            else {
              var date_min_accy2 = date_min_accy1;
            }
            if(date_min_accy2.substring(5,6) != '/') {                                                                 //new version of date format
              min_date_mote_accy = ( ((date_min_accy2.substring(0,3)).concat(0)).concat(date_min_accy2.substring(3)) );           //new version of date format
            }
            else{
              min_date_mote_accy = (date_min_accy2);                                                                        //new version of date format
            }
          }

          //array containing all measures
          avg_accsy.push(meas.accel_y);
        });
      }

      max_accsy.push(max_mote_accy);
      min_accsy.push(min_mote_accy);
      date_max_accy.push(max_date_mote_accy);
      date_min_accy.push(min_date_mote_accy);
    }
  });

  console.log(max_accsy);
  console.log(min_accsy);

  //processing of new max data
  var max_index_accy;
  var maxaccY = Math.max(...max_accsy);
  if(maxaccY == -Infinity)
  {
    $("#maxay").html('-');
  }
  else
  {
    max_index_accy= max_accsy.indexOf(Math.max(...max_accsy));
    $("#maxay").html(maxaccY + " (" + alias_accy[max_index_accy] + " - " + date_max_accy[max_index_accy] + ")");
  }

  //processing of new min data
  var min_index_accy;
  var minaccY = Math.min(...min_accsy);
  if(minaccY == Infinity)
  {
    $("#minay").html('-');
  }
  else
  {
    min_index_accy = min_accsy.indexOf(Math.min(...min_accsy));
    $("#minay").html(minaccY + " (" + alias_accy[min_index_accy] + " - " + date_min_accy[min_index_accy] + ")");
  }

  //processing of new avg data
  if(avg_accsy.length > 1)
  {
    $("#averageay").html(average(avg_accsy));
  }
  else
  {
    $("#averageay").html('-');
  }
}


function accz_data(vettMotes){
  //processing of temperatures values
  var alias_accz = new Array();

  var date_max_accz = new Array();
  var date_min_accz = new Array();

  var max_accsz = new Array();
  var min_accsz = new Array();
  var avg_accsz = new Array();

  vettMotes.forEach(function(mote) {
    if(mote.mote_type == "OpenMote")
    {
      alias_accz.push(mote.alias_name);
      if(mote.measures.length > 0)
      {
        var measures_accz = new Array();
        mote.measures.forEach(function(meas) {
          measures_accz.push(meas.accel_z);
        });

        //calculation of max values of eatch mote
        var maxAz=Math.max(...measures_accz);
        var minAz=Math.min(...measures_accz);
        var avgAz=average(measures_accz);

        //printing values on stat box of each mote
        $("#meta_model_max_acc_z-"+mote._id.$oid).html(maxAz);
        $("#meta_model_min_acc_z-"+mote._id.$oid).html(minAz);
        $("#meta_model_avg_acc_z-"+mote._id.$oid).html(avgAz);

        var max_mote_accz;
        var max_date_mote_accz;
        var min_mote_accz;
        var min_date_mote_accz;

        mote.measures.forEach(function(meas) {
          if(meas.accel_z == maxAz)
          {
            max_mote_accz = (meas.accel_z);
            var date_max_accz0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
            var date_max_accz1 = ((date_max_accz0.toLocaleDateString()).concat(', ')).concat(date_max_accz0.toLocaleTimeString()); //new version of date format
            if(date_max_accz1.substring(1,2) == '/') {
              var zero = '0';
              var date_max_accz2 = zero.concat(date_max_accz1);
            }
            else {
              var date_max_accz2 = date_max_accz1;
            }
            if(date_max_accz2.substring(5,6) != '/') {                                                                 //new version of date format
              max_date_mote_accz = ( ((date_max_accz2.substring(0,3)).concat(0)).concat(date_max_accz2.substring(3)) );           //new version of date format
            }
            else{
              max_date_mote_accz = (date_max_accz2);                                                                        //new version of date format
            }
          }

          if(meas.accel_z == minAz)
          {
            min_mote_accz = (meas.accel_z);
            var date_min_accz0 = new Date(meas.date.$date -7200000);                                                  //new version of date format
            var date_min_accz1 = ((date_min_accz0.toLocaleDateString()).concat(', ')).concat(date_min_accz0.toLocaleTimeString()); //new version of date format
            if(date_min_accz1.substring(1,2) == '/') {
              var zero = '0';
              var date_min_accz2 = zero.concat(date_min_accz1);
            }
            else {
              var date_min_accz2 = date_min_accz1;
            }
            if(date_min_accz2.substring(5,6) != '/') {                                                                 //new version of date format
              min_date_mote_accz = ( ((date_min_accz2.substring(0,3)).concat(0)).concat(date_min_accz2.substring(3)) );           //new version of date format
            }
            else{
              min_date_mote_accz = (date_min_accz2);                                                                        //new version of date format
            }
          }

          //array containing all measures
          avg_accsz.push(meas.accel_z);
        });
      }

      max_accsz.push(max_mote_accz);
      min_accsz.push(min_mote_accz);
      date_max_accz.push(max_date_mote_accz);
      date_min_accz.push(min_date_mote_accz);
    }
  });

  console.log(max_accsz);
  console.log(min_accsz);

  //processing of new max data
  var max_index_accz;
  var maxaccZ = Math.max(...max_accsz);
  if(maxaccZ == -Infinity)
  {
    $("#maxaz").html('-');
  }
  else
  {
    max_index_accz= max_accsz.indexOf(Math.max(...max_accsz));
    $("#maxaz").html(maxaccZ + " (" + alias_accz[max_index_accz] + " - " + date_max_accz[max_index_accz] + ")");
  }

  //processing of new min data
  var min_index_accz;
  var minaccZ = Math.min(...min_accsz);
  if(minaccZ == Infinity)
  {
    $("#minaz").html('-');
  }
  else
  {
    min_index_accz = min_accsz.indexOf(Math.min(...min_accsz));
    $("#minaz").html(minaccZ + " (" + alias_accz[min_index_accz] + " - " + date_min_accz[min_index_accz] + ")");
  }

  //processing of new avg data
  if(avg_accsz.length > 1)
  {
    $("#averageaz").html(average(avg_accsz));
  }
  else
  {
    $("#averageaz").html('-');
  }
}
/////////////////////////////////////////////////////////////////////////////////////////////////////////
//functions to add motes bar
function mostraMotes(id)
{
  if($("#"+id).is(":visible") )
  {
    $('html, body').animate({
      scrollTop: $("#"+id).offset().top
    }, 1000);
  }
}

function createBottomBar()
{
   aliasDeiMotes.forEach(function(i){
        $("#Bar").append(
          "<button class='btn btn-primary btn-motes' onclick='mostraMotes(\""+i+"\")'>" + i + "</button>"
          );
   });
}

/////////////////////////////////////////////////////////////////////////////////////////////////
//functions to show number of motes
function contamotes() {
  if(aliasDeiMotes.length > 0)
    document.getElementById("n_motes").innerHTML = aliasDeiMotes.length;
}

function contaOM() {
 var i, contOM=0;

  if(aliasDeiMotes.length > 0)
  {
    for(i=0; i<aliasDeiMotes.length; i++){
       if(tipologia_motes[i] == "OpenMote")
        {
          contOM++;
        }
      }
    document.getElementById("OM").innerHTML = contOM;
  }
}

function contaTB() {
 var i, contTB=0;

  if(aliasDeiMotes.length > 0)
  {
   for(i=0; i<aliasDeiMotes.length; i++){
       if(tipologia_motes[i] != "OpenMote")
        {
          contTB++;
        }
      }
   document.getElementById("TB").innerHTML = contTB;
  }
}


/////////////////////////////////////////////////////////////////////////////////////////
// functions to generate topology image
function updateForData(json) {
	var n_dots = 1;

    // Updates DAG
    console.log('DAG data received');
    var hasJson = true
    if (json.result && json.result == "none") {
        console.log('no data in result');
        hasJson = false;
    } else if (!json.states || !json.edges) {
        console.log('state/edges not found in result');
        hasJson = false;
    }

    if (hasJson) {
        if(json.states.length > 0 && json.edges.length > 0) {
            $("#routing_status").text("");
            var states = json.states;
            var edges  = json.edges;
            var g = new dagreD3.Digraph();
            var renderer = new dagreD3.Renderer();
            var layout = dagreD3.layout().rankDir("BT");
            var rrun = renderer.layout(layout).run(dagreD3.json.decode(states, edges), d3.select("svg g"));
            d3.select("svg")
                .attr("width", rrun.graph().width + 40)
                .attr("height", rrun.graph().height + 40);
        }
        else
        {
            var dots = Array(n_dots + 1).join(".");
            n_dots++;
            if (n_dots > 3)
                n_dots = 1;
            $("#routing_status").text("Waiting routing information " + dots);
        }
    }

    timeoutId = setTimeout(function() {
        $.ajax({
            dataType: "json",
            url: "http://193.204.50.185:8080/routing/dag",
            success: updateForData,
        });
    }, 5000);
}

function errorOnAjax(jqxhr, status, errorstr) {
  var errText = (errorstr == null)
          ? '' : ', error: ' + errorstr;
  console.log('Ajax error: ' + status + errText);
}


function showImageMotes(){
  $('#im_top').toggle('slow',function() {
  //Animation complete.
  });

  var n_dots = 1;
  $(document).ready(function(){
    $.ajax({
      dataType: "json",
      url: "http://193.204.50.185:8080/routing/dag",
      success: updateForData,
    //  async:true,
   //   global:false,
    });
  });
}


//////////////////////////////////////////////////////////////////////////////////////////////////
//function to scroll to upper table
function Up_table()
{
  $('html, body').animate({
    scrollTop: $("#top").offset().top
  }, 1000);

}

///////////////////////////////////////////////////////////////////////////////////////////////////
//function average/max/min of the vector
function average(vector)
{
  var sum=0;
  vector.forEach(function(i){
    sum+=i;
  });
  return (Math.round((sum/vector.length)*100)/100);
}

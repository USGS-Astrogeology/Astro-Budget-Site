function save_row_preference(table) {
  let table_row_size = table.page.len();
  console.log("New table row preference is " + table_row_size + " rows");

  $.get("/row_setting/ajax/save/" + table_row_size)
    .always(function(data)
    {
      displayAlert(data);
    });

}

function check_row_preference(table) {
  var user_preference = null;
  $.get("/row_setting/ajax/get")
   .always(function(data) {
     if (data != "None") {
       user_preference = parseInt(data);
     }

     if (user_preference != null) {
       table.page.len(user_preference).draw();
     }

   });
}

function loadTable(ajax, reload, table) {
    if (reload) {
      if (ajax === '') {                            
        $(table).DataTable().ajax.reload()          // if ajax argument empty, reload from instantiation path
      } else {
        $(table).DataTable().ajax.url(ajax).load(); // otherwise, load from the ajax argument
      }
    } else {
      // creates the table if it doesn't already exist
      $(table).DataTable( {
          'processing': true,
          'serverSide': false,
          'autoWidth': false,
          'ajax': ajax,
          'lengthMenu': [[5, 10, 20, -1], [5, 10, 20, 'All']]
        });
    }

    check_row_preference($(table).DataTable());
}

function editDialog(ajax, proposalid, table) {
  var save_ajax = ajax.replace('edit', 'save');

  $('<div></div>').load(ajax, function(data) {
    $(this).dialog({
      width: 'auto',
      modal: true,
      draggable: false,
      title: $(data).find('#title').val(),
      close: function() { $(this).dialog("destroy") },
      buttons: {
        "Save": function () {
          dialog = $(this);
          callSave(save_ajax, table, dialog) },
        Cancel: function () { $(this).dialog("destroy"); }
      }
    });
  });
}


function deleteDialog(ajax, proposalid, table, description) {
  let div = $('<div><h2>Are you sure you want to delete ' + description + '?</h2></body></html></div>');

  $(div).dialog({
    width: 'auto',
    modal: true,
    draggable: false,
    close: function() { $(this).dialog("destroy") },
    buttons: {
      "Delete": function () {
        dialog = $(this);
        callDelete(ajax, proposalid, table, dialog) },
      Cancel: function () { $(this).dialog("destroy") }
    }
  });
  //console.log(ajax);
}

function displayAlert(data) {
  let content = `${ data['status']}: ${data['description']} 
                 ${(data['status'] === 'Error') ? 'not' : ''} 
                 ${ data['action']}`;
  $('.alert').last().html(content).slideDown('fast', function() {
    alert = $(this);
    setTimeout(function() {
      $(alert).slideUp('fast');
    }, 3000);
  });
}

function callSave(ajax, table, dialog) {
  $.post(ajax, $('form').serialize())
    .always(function(response){

      if (response['status'] === 'Success') {
        dialog.dialog('destroy');
        loadTable(response['reload_path'], true, table);
      }    

      displayAlert(response);
  });
}

function callDelete(ajax, proposalid, table, dialog) {
  $.get(ajax + '&' + proposalid)
    .always (function(response) {
      //dialog.dialog("close");
      //$("#warningDiv").html("<p>Successfully Deleted</p>");
      //$("#warningDiv").html(data);
      //$("#warningDiv").show();
      //console.log(ajax);
      displayAlert(response);

      //var load_ajax = ajax.replace('delete', 'list');

      var elements = load_ajax.split('/');
      var elements_size = elements.length;
      //console.log(elements);
      if (elements[1] === "conferenceattendees")
      {
        //console.log(true);
        var new_ajax = load_ajax.replace(elements[elements_size - 1],
          ("byproposal/" + proposalid));
        //console.log(new_ajax);
      }
      else
      {
        var new_ajax = load_ajax.replace(elements[elements_size - 1], proposalid);
      }

      //console.log(table);

      dialog.dialog('destroy');
      loadTable(new_ajax, true, table);
    });
}

function updateDropdown (id) {
  var newDate = $("#" + id).datepicker("getDate");

  //console.log ("datepicker returned " + newDate);
  if (newDate == null) {
    //console.log ("newDate is NULL!!!!!");
    newDate = new Date();
    $("#" + id).val((newDate.getMonth() + 1) + '/' + newDate.getDate() + '/' +  newDate.getFullYear());
  }

  var month = newDate.getMonth() + 1;
  var year  = newDate.getFullYear();

  var fyYear = year - 2000;
  if (month >= 10) {
    fyYear += 1;
  }

  var FYDate = '10/01/20' + (fyYear - 1);
  var hid = '#' + id + 'dd';

  $(hid).val(FYDate);
}

function updateCalendar (id) {
  var hid = '#' + id;
  var idname = hid + 'dd';
  var newDate = $(idname).val();

  $(hid).val (newDate);
}

function figureCosts(proposalid) {
  $('#budgetDashboard').html('');
  deleteProjectBudgetDashboard('#budgetDashboard');
  $.getJSON( "index.php?view=proposal-cost-titles-json&proposalid=" + proposalid, function( data ) {
    var items = [];
    $.each( data.data[0], function( key, val ) {
      $.each( val, function( title, mesg ) {
        $(title).html(mesg);
      });
    });
  });
  $('#fbmsTitle').html('FBMS Accounts');

  // Dashboard
  $.getJSON( "index.php?view=proposal-costs-json&proposalid=" + proposalid, function( data ) {
    projectBudgetDashboard('#budgetDashboard',data.data[0].budget);
    projectBudgetTable('#budgetTable', data.data[0].budget);
  });
}

function projectBudgetTable (id, data) {
  var newTable = "<table class='display' width='100%'>";
  newTable += "<tr><th>Year</th>";
  $.each(data, function(i, item) {
    newTable += "<td>" + item.fy + "</td>";
  });

  newTable += "</tr>\n<tr><th>Costs</th>";
  $.each(data, function(i, item) {
    newTable += "<td>$";
    var costs = (item.costs.expenses + item.costs.staffing + item.costs.travel + item.costs.equipment + item.costs.overhead);
    newTable += costs.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    newTable += "</td>";
  });

  newTable += "</tr>\n<tr><th>Funding</th>";
  $.each(data, function(i, item) {
    newTable += "<td>$" + item.funding.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + "</td>";
  });

  newTable += "</tr>\n<tr><th>Total</th>";
  $.each(data, function(i, item) {
    totals = item.funding - (item.costs.expenses + item.costs.staffing + item.costs.travel + item.costs.equipment +
      item.costs.overhead);
    if (totals < 0) { newTable += "<td><font color='firebrick'>$"; }
    else { newTable += "<td><font color='darkolivegreen'>$"; }
    newTable += totals.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    newTable += "</td>";
  });

  newTable += "</tr><tr></table>\n";

  $(id).html(newTable);
}

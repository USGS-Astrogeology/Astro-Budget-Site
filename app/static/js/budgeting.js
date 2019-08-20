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
        $(table).DataTable().ajax.reload()
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

function editDialog(ajax, table) {
  let save_ajax = ajax.replace('edit', 'save').replace('new', 'save');
  let div = $(`<div></div>`);

  console.log(ajax);

  $(div).load(ajax, function(data) {
    $(this).dialog({
      width: 'auto',
      modal: true,
      draggable: false,
      title: $(data).find('#title').val(),
      close: function() { $(this).dialog("destroy") },
      buttons: {
        "Save":   function () { submitAction(save_ajax, table, $(this)) },
        "Cancel": function () { $(this).dialog("destroy"); }
      }
    });
  });
}


function deleteDialog(ajax, table, description) {
  let div = $('<div><h2>Are you sure you want to delete ' + description + '?</h2></body></html></div>');

  $(div).dialog({
    width: 'auto',
    modal: true,
    draggable: false,
    close: function() { $(this).dialog("destroy") },
    buttons: {
      "Delete": function () { submitAction(ajax, table, $(this)) },
      "Cancel": function () { $(this).dialog("destroy") }
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

function submitAction(ajax, table, dialog) {
  $.post(ajax, $('form').serialize())
    .always(function(response){

      if (response['status'] === 'Success') {
        dialog.dialog('destroy');
        loadTable(ajax, true, table);
      }

      displayAlert(response);
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

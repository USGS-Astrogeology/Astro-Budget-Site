// this will work even if the value chosen is not on the dropdown menu
// if this is null, the code will choose the first available option for size on the dropdown menu
var user_preference = 10;

function save_row_preference(table) {
  // look up the data tables thing from wherever and figure out how to get the size from it
  // will be called by an onClick function from the button
  // will save this somewhere
  var table_row_size = table.page.len();
  console.log("New table row preference is " + table_row_size + " rows");
}

function check_row_preference(table) {
  if (user_preference != null) {
    console.log(table.page.len());
    table.page.len(user_preference).draw();
    console.log(table.page.len());
  }
}

function loadTable(ajax, reload, table) {

    if (reload) {
      $(table).DataTable().ajax.reload();
    } else {
      // creates the table if it doesn't already exist
      $(table).dataTable( {
          'processing': true,
          'serverSide': false,
          'autoWidth': false,
          'ajax': ajax,
          'lengthMenu': [[5, 10, 20, -1], [5,10, 20, 'All']]
        });
    }

    check_row_preference($(table).DataTable());
    /*
    if (!reload) {
        check_row_preference($(div).DataTable());
    }
    */
}

function editDialog(ajax, proposalid, table) {
  var save_ajax = ajax.replace('edit', 'save');

  $('<div></div>').load(ajax, function(data) {
    $(this).dialog({
      width: 'auto',
      modal: true,
      title: $(data).find('#title').val(),
      close: function() { $(this).dialog("destroy") },
      buttons: {
        "Save": function () {
          dialog = $(this);
          callSave(save_ajax, proposalid, table, dialog) },
        Cancel: function () { $(this).dialog("destroy"); }
      }
    });
  });

  //console.log(save_ajax);
  //console.log(table);
}


function deleteDialog(ajax, proposalid, table, description) {
  let div = $('<div><h2>Are you sure you want to delete ' + description + '?</h2></body></html></div>');

  $(div).dialog({
    width: 'auto',
    modal: true,
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
  $('.alert').last().html(data).slideDown('fast', function() {
    alert = $(this);
    setTimeout(function() {
      $(alert).slideUp('fast');
    }, 3000);
  });
}


// TODO: generalize a save call
function callSave(ajax, proposalid, table, dialog) {

  $.post(ajax, $('form').serialize())
    .always(function(data){
      displayAlert(data);

      //console.log(ajax);
      var load_ajax = ajax.replace('save', 'list');

      var elements = load_ajax.split('/');
      var elements_size = elements.length;
      //console.log(elements);
      if (elements[1] === "conferenceattendees") {
        //console.log(true);
        var new_ajax = load_ajax.replace(elements[elements_size - 1],
          ("byproposal/" + proposalid));
        //console.log(new_ajax);
      } else {
        var new_ajax = load_ajax.replace(elements[elements_size - 1], proposalid);
      }

      dialog.dialog('destroy');
      //console.log("ajax: " + new_ajax);
      //console.log("table " + table);
      loadTable(new_ajax, true, table);

  });
}


function callDelete(ajax, proposalid, table, dialog) {
  $.get(ajax + '&' + proposalid)
    .always (function(data) {
      //dialog.dialog("close");
      //$("#warningDiv").html("<p>Successfully Deleted</p>");
      $("#warningDiv").html(data);
      $("#warningDiv").show();

      //console.log(ajax);

      var load_ajax = ajax.replace('delete', 'list');

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


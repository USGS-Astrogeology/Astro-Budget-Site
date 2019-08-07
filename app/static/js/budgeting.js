// TODO: update references throughout application (outside of proposal-edit.html)
function loadTable(ajax, reload, table) {
    //let html =$(table).html();

    if (reload) {
        //$(table).dataTable().fnDestroy();
        //$(table).html(html);
        $(table).DataTable().ajax.reload();
    }
    else
    {
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


// TODO: update references throughout application
function editDialog(ajax, proposalid, table, form) {
  var save_ajax = ajax.replace('edit', 'save');

  $('#editDialog').load(ajax, function() {
    $(this).dialog({
      width: 'auto',
      modal: true,
      buttons: {
        "Save": function () { callSave(save_ajax, proposalid, table, form); },
        Cancel: function () { $(this).dialog("close"); }
      }
    });
  });
}


function deleteDialog(ajax, proposalid, table, description) {
  //$.getJSON(ajax, function(data) {
    $("#editDialog").html("<html><head><title>Confirm Deletion</title></head>" +
                        "<body><h2>Are you sure you want to delete " + description + "?</h2></body></html>");
  //});

  $("#editDialog").dialog({
    width: 'auto',
    modal: true,
    buttons: {
      "Delete": function () { callDelete(ajax, proposalid, table); },
      Cancel: function () { $(this).dialog("close"); }
    }
  });

  console.log(ajax);

}



// TODO: generalize a save call
function callSave(ajax, proposalid, table, form) {
  $.post(ajax, $('form').serialize())
    .always(function(data){

    //dialog.dialog("close");
    //$("#warningDiv").html("<p>Save Successful</p>");
    $("#warningDiv").html(data);
    $("#warningDiv").show();

    console.log(ajax);
    var load_ajax = ajax.replace('save', 'list');

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

    loadTable(new_ajax, true, table);
  });
}


function callDelete(ajax, proposalid, table) {
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

      loadTable(new_ajax, true, table);
    });
}

function updateDropdown (id) {
  var newDate = $("#" + id).datepicker("getDate");

  console.log ("datepicker returned " + newDate);
  if (newDate == null) {
    console.log ("newDate is NULL!!!!!");
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

  console.log ("Setting " + hid + " to " + FYDate);
  $(hid).val(FYDate);
}

function updateCalendar (id) {
  var hid = '#' + id;
  var idname = hid + 'dd';
  var newDate = $(idname).val();

  $(hid).val (newDate);
}

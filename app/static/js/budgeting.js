// TODO: update references throughout application (outside of proposal-edit.html)
function loadTable(reload, ajax, div) {
    let html =$(div).html();

    if (reload) {
        $(div).dataTable().fnDestroy();
        $(div).html(html);
    }

    $(div).dataTable( {
        'processing': true,
        'serverSide': false,
        'autoWidth': false,
        'ajax': ajax,
        'lengthMenu': [[5, 10, 20, -1], [5,10, 20, 'All']]
    });

    check_row_preference($(div).DataTable());
    /*
    if (!reload) {
        check_row_preference($(div).DataTable());
    }
    */
}

// TODO: generalize dialog for edit
// TODO: update references throughout application
function editDialog(ajax, proposalid, height, width, table) {
    $('#editDialog').load(ajax);

    dialog = $('#editDialog').dialog({
      autoOpen: false,
      height: height,
      width: width,
      modal: true,
      buttons: {
        "Save": function () { callSave(proposalid, ajax, table); }, // TODO, determine simplest way to call this with minimum parameters
        Cancel: function () {
          dialog.dialog("close");
        }
      }
    });

    dialog.dialog("open");
}

// TODO: generalize dialog for delete
function deleteDialog(ajax, proposalid, height, width, table)
{
  $.getJSON( ajax ) {
    $("#editDialog").html("<html><head><title>Confirm Deletion</title></head>" +
                        "<body><h2>Are you sure you want to delete?</h2></body></html>");
  });

  dialog = $("#editDialog").dialog({
    autoOpen: false,
    height: height,
    width: width,
    modal: true,
    buttons: {
      "Delete": function () { callDelete(proposalid, ajax, table); },
      Cancel: function () {
        dialog.dialog("close");
      }
    }
}

// TODO: generalize a save call
function callSave(proposalid, ajax, table) {
  //$.post("index.php", $("#fbmsForm").serialize())
    .always(function(){

    dialog.dialog("close");
    $("#warningDiv").html("<p>Save Successful</p>");
    $("#warningDiv").show();

    var load_ajax = ajax.replace('edit', 'list');

    // see if proposalid is provided in the ajax call already
    loadTable(true, load_ajax + proposalid, ('#' + table));
  });
}

// TODO: generalize a delete call
function callDelete(proposalid, ajax, table)
{
  var load_ajax = ajax.replace('edit', 'list');

  $.get(ajax)
    .always (function() {
      dialog.dialog("close");
      $("#warningDiv").html("<p>Succesfully Deleted</p>");
      $("#warningDiv").show();

      // see if proposalid is provided in the ajax call already
      loadTable(true, load_ajax + proposalid, ('#' + table));
    });
}

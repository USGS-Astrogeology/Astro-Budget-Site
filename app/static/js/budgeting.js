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

    if (!reload) {
        check_row_preference($(div).DataTable());
    }
}

// TODO: generalize dialog for edit
// TODO: update references throughout application
function editDialog(ajax, proposalid, height, width) {
    $('#editDialog').load(ajax);

    dialog = $('#editDialog').dialog({
      autoOpen: false,
      height: height,
      width: width,
      modal: true,
      buttons: {
        "Save": function () { callSave(proposalid); }, // TODO, determine simplest way to call this with minimum parameters
        Cancel: function () {
          dialog.dialog("close");
        }
      }
    });
  
    dialog.dialog("open");
}

// TODO: generalize dialog for delete
function deleteDialog(ajax, proposalid) {

}

// TODO: generalize a save call
function callSave(proposalid) {

}

// TODO: generalize a delete call
function callDelete() {

}


function loadTasksTable (reload, proposalid) {
  if (reload) {
    $('#tasksTableDiv').jsGrid("destroy");
  }

  var CopyField = function(config) {
      jsGrid.Field.call(this, config);
  };

  CopyField.prototype = new jsGrid.Field({

      css: "copy-field",           // redefine general property 'css'
      align: "center",              // redefine general property 'align'

  });

  $task_res = $.ajax('/tasks/ajax/list/' + proposalid, {dataType: "json", async: false});
  $task_json = $task_res.responseJSON['data'];
  $people_res = $.ajax('/people/ajax/dropdown', {dataType: "json", async: false});
  $task_dd_res = $.ajax('/tasks/ajax/dropdown?proposalid=' + proposalid, {dataType: "json", async: false});
  $filtered_task_list = new Set($task_dd_res.responseJSON['data']);
  $task_dd_list = [];
  $filtered_task_list.forEach(function(task){
    $task_dd_list.push({name: task});
  });

  $fields = [];
  $new_array = [];

  // Iterates through the JSON data
  $task_json.forEach(function(element) {
    $new_array = $new_array.concat(Object.keys(element));
  });

  $new_fields = Array.from(new Set($new_array)).sort();

  if ($new_fields.length == 0) {
    let date = new Date();
    $new_fields.push("FY" + date.getFullYear().toString().substr(2,));
  }

  let css_classes = "sorting ui-state-default DataTables_sort_wrapper";

  // Pushes static values for Task, Staffing, and Cost
  $fields.push({
    name: "Task",
    type: "select",
    width: 100,

    items: $task_dd_list,
    valueField: "name",
    textField: "name",
    headercss: css_classes
  });
  $fields.push({
    name: "Staffing",
    type: "select",
    width: 150,
    valueType: "number",

    items: $people_res.responseJSON['data'],
    valueField: "peopleid",
    textField: "name",

    selectedIndex: 0,
    headercss: css_classes
  });
  $fields.push({
    name: "Cost",
    type: "text",
    width: 100,

    editing: false,
    inserting: false,
    headercss: css_classes
  });
  // Iterates through parsed JSON data and inserts them into the fields array
  $new_fields.forEach(function(element){
    if (element.includes("FY") && !element.includes("id")) {
      $fields.push({
        name: element,
        type: "number",
        width: 75,

        headercss: css_classes
      });
    };
  });
  // jsGrid static value pushed on the fields array last
  $fields.push({
    type: "control",
    width: 100,

    headercss: css_classes,
    itemTemplate: function(value, item) {
      $result = jsGrid.fields.control.prototype.itemTemplate.apply(this, arguments);
      $customButton = $("<button id=\"dupeButton\" class=\"jsgrid-button\" title=\"Duplicate\">" + "</button>").click(function(e) {
        var copy = $.extend({}, item, {Task: item.Task});
        $("#tasksTableDiv").jsGrid("insertItem", copy);
        e.stopPropagation();
      });
      return $result.add($customButton);
    }
  });

  // Initializes the grid using the fields array and JSON data
  $("#tasksTableDiv").jsGrid({
    width: "100%",
    height: "400px",
    inserting: true,
    editing: true,
    sorting: true,
    paging: true,

    data: $task_json,
    fields: $fields,

    onItemInserted: function(args) {
      $entry = args.item;
      $keys = Object.keys($entry);

      $task_res = $.ajax({
        type:'post',
        url: 'index.php?',
        data: {
          view: 'task-save',
          taskid: 'new',
          proposalid: proposalid,
          peopleid: $entry['Staffing'],
          taskname: $entry['Task']
        },
        async: false,
        cache: false
      });

      $keys.forEach( function(key) {
        if (key.includes("FY") && !key.includes("id")) {
          fiscalyear = "10/01/20" + (parseInt(key.substring(2, )) - 1);

          $.ajax({
            type:'post',
            url: 'index.php?',
            success: function() {
              loadTasksTable(true, proposalid);
            },
            data: {
              view: 'staffing-save',
              taskid: $task_res.responseText,
              staffingid: 'new',
              staffingpeopleid: $entry['Staffing'],
              fiscalyear: fiscalyear,
              flexhours: $entry[key]
            },
            async: true,
            cache: false
          });
        }
      });
      figureCosts(proposalid);
    },
    onItemUpdated: function(args) {
      $entry = args.item;
      $keys = Object.keys($entry);

      $.ajax({
        type:'post',
        url: 'index.php?',
        success: function() {
          loadTasksTable(true, proposalid);
        },
        data: {
          view: 'task-save',
          taskid: $entry['taskid'],
          proposalid: proposalid,
          peopleid: $entry['Staffing'],
          taskname: $entry['Task']
        },
        async: true,
        cache: false
      });

      $keys.forEach( function(key) {
        if (key.includes("FY") && !key.includes("id")) {
          fiscalyear = "10/01/20" + (parseInt(key.substring(2, )) - 1);

          if ($entry[key + 'staffingid']) {
            staffingid = $entry[key + 'staffingid'];
          }
          else {
            staffingid = 'new';
          }

          if ($entry[key] === 0) {
            $data = {
              view: 'staffing-delete',
              staffingid: staffingid,
              proposalid: proposalid
            }
          }
          else {
            $data = {
              view: 'staffing-save',
              taskid: $entry['taskid'],
              staffingid: staffingid,
              staffingpeopleid: $entry['Staffing'],
              fiscalyear: fiscalyear,
              flexhours: $entry[key]
            }
          }

          $.ajax({
            type:'post',
            url: 'index.php?',
            success: function() {
              loadTasksTable(true, proposalid);
            },
            data: $data,
            async: true,
            cache: false
          });
        }
      });
      figureCosts(proposalid);
    },
    onItemDeleted: function(args) {
      $entry = args.item;
      $keys = Object.keys($entry);

      $.ajax({
        type:'post',
        url: 'index.php?',
        success: function() {
          loadTasksTable(true, proposalid);
        },
        data: {
          view: 'task-delete',
          taskid: $entry['taskid'],
          proposalid: proposalid
        },
        async: true,
        cache: false
      });
      figureCosts(proposalid);
    }
  });
}

// Custom method for adding columns to jsGrid
function addColumn(proposalid) {
  $task_json = $("#tasksTableDiv").jsGrid("option", "data");
  $fields = $("#tasksTableDiv").jsGrid("option", "fields");

  let field_names = [];
  $fields.forEach(function(field) {
    field_names.push(field['name']);
  });

  let name = $('#validfiscalyearsdd :selected').text();

  if (field_names.includes(name)) {
    return;
  }

  let css_classes = "sorting ui-state-default DataTables_sort_wrapper";
  let temp = $fields.pop();

  // Pushes user defined column
  $fields.push({
    name: name,
    type: "number",
    width: 75,

    headercss: css_classes
  });

  // Pushes static jsGrid value back onto the array
  $fields.push(temp);

  // Retintializes the grid to allow for row and column editing
  $("#tasksTableDiv").jsGrid({
    width: "100%",
    height: "400px",
    inserting: false,
    editing: true,
    sorting: true,
    paging: true,

    data: $task_json,
    fields: $fields,
  });
}

function addTask() {
  $task_items = $("#tasksTableDiv").jsGrid("fieldOption", "Task", "items");

  $tasks = [];
  $task_items.forEach(function(task) {
    $tasks.push(task['name']);
  });

  let new_task = $("#taskField").val();
  $("#taskField").val('');

  if ($tasks.includes(new_task)) {
    return;
  }

  $task_items.push({"name": new_task});

  $("#tasksTableDiv").jsGrid("fieldOption", "Task", "items", $task_items);
}

/*
function editTaskDialog (taskid, proposalid) {
  if (taskid == 'new') {
    $.post("index.php", $("#newTaskForm").serialize())
      .always( function(data) {
      console.log("Inside post: " + data);
      return (editTaskDialog(data, proposalid));
    });
  }

  $("#editDialog").load("/tasks/ajax/edit?proposalid=" + proposalid + "&taskid=" + taskid);

  dialog = $("#editDialog").dialog({
    autoOpen: false,
    height: 600,
    width: 1000,
    modal: true,
    buttons: {
      "Save Task": function () { saveTask(proposalid); },
      Cancel: function () {
        dialog.dialog("close");
      }
    }
  });

  dialog.dialog("open");
}*/

function saveTask (proposalid) {
  //$.post("index.php", $("#taskForm").serialize())
  $.post(("/tasks/ajax/save/" + $("#taskid").val()), $("taskForm").serialize())
    .always (function() {

      loadTasksTable(true, proposalid);

      dialog.dialog("close");
      $("#warningDiv").html("<p>Updated " + $("#taskname").val() + "</p>");
      $("#warningDiv").show();

      figureCosts(proposalid);
   });
}

function deleteTaskDialog(taskid, proposalid) {
  var task;

  $.getJSON( "index.php?view=tasks-list-json&proposalid=" + proposalid + "&taskid=" + taskid, function( data ) {
    var pattern = />(.+)<\/a>/i;
    task = pattern.exec(data.data[0][0])[1];
    $("#editDialog").html("<html><head><title>Confirm Deletion</title></head>" +
                        "<body><h2>Are you sure you want to delete task " + task +
                        " and any staffing assigned to it?</h2></body></html>");
  });

  dialog = $("#editDialog").dialog({
    autoOpen: false,
    height: 250,
    width: 400,
    modal: true,
    buttons: {
      "Delete Task": function () { deleteTask(taskid, proposalid); },
      Cancel: function () {
        dialog.dialog("close");
      }
    }
  });

  dialog.dialog("open");
}

function deleteTask(taskid, proposalid) {
  $.get("index.php?view=task-delete&taskid=" + taskid + "&proposalid=" + proposalid)
    .always (function() {
      dialog.dialog("close");
      $("#warningDiv").html("<p>Deleted [" + taskid + "]</p>");
      $("#warningDiv").show();

      loadTasksTable(true, proposalid);
      figureCosts(proposalid);
    });
}

function saveAttendee(proposalid) {
  $.post("index.php", $("#conferenceAttendeeForm").serialize())
    .always (function() {

      dialog.dialog("close");
      $("#warningDiv").html("<p>Updated [" + $("#expenseid").val() + "] (" + $("#description").val() + ")</p>");
      $("#warningDiv").show();

      figureCosts(proposalid);

      loadTable('/conferenceattendees/ajax/list/byproposal/' + proposalid, true, $('#conferenceattendeesTable'));
    });
}

function deleteAttendee(travelid, proposalid) {
  $.get("index.php?view=conference-attendee-delete&travelid=" + travelid + "&proposalid=" + proposalid)
    .always (function() {
      dialog.dialog("close");
      $("#warningDiv").html("<p>Deleted [" + travelid + "]</p>");
      $("#warningDiv").show();

      loadTable('/conferenceattendees/ajax/list/byproposal/' + proposalid, true, $('#conferenceattendeesTable'));
      figureCosts(proposalid);
    });
}

function loadConferenceRate() {
  $("#meeting").val($("#conferenceiddropdown option:selected").text());
  //$.getJSON("index.php?view=conference-rate-list-json&conferenceid=" + $("#conferenceiddropdown").val() +
      //"&effectivedate=" + $("#tripstartdate").val(), function( data ) {
    //$.getJSON("/conferencerates/ajax/list/" + $(#conferenceiddropdown), function(data){
    //$.getJSON("/conferencerates/ajax/list" + $(#conferenceiddropdown).val(), function(data)){
  $.get("/conferencerates/ajax/get/" + $("#conferenceiddropdown").val())
    .always(function(data)
    {
      console.log(data);

      elements = data.replace('[', '');
      elements = elements.replace(']', '');
      elements_array = elements.split(',');
      console.log(elements_array);

      console.log(elements_array[0]);
      //console.log(data.city);

      $("#perdiem").val(elements_array[0]);
      $("#lodging").val(elements_array[1]);
      $("#registration").val(elements_array[2]);
      $("#groundtransport").val(elements_array[3]);
      $("#airfare").val(elements_array[4]);
      $("#city").val(elements_array[5].replace(/'/g, ""));
      $("#state").val(elements_array[6].replace(/'/g, ""));
      $("#country").val(elements_array[7].replace(/'/g, ""));

      /*
      $("#perdiem").val(data.data[0][1]);
      $("#lodging").val(data.data[0][2]);
      $("#registration").val(data.data[0][3]);
      $("#groundtransport").val(data.data[0][4]);
      $("#airfare").val(data.data[0][5]);
      $("#city").val(data.data[0][6]);
      $("#state").val(data.data[0][7]);
      $("#country").val(data.data[0][8]);
      */
    });
    //console.log(data);
  //});
  console.log($("#conferenceiddropdown").val())
}

function saveExpense(proposalid) {
  $.post("index.php", $("#expenseForm").serialize())
    .always (function () {

      dialog.dialog("close");
      $("#warningDiv").html("<p>Updated [" + $("#expenseid").val() + "] (" + $("#description").val() + ")</p>");
      $("#warningDiv").show();

      figureCosts(proposalid);

      loadTable('/expenses/ajax/list/' + proposalid, true, $('#expensesTable'));
  });
}

function deleteExpense(expenseid, proposalid) {
  $.get("index.php?view=expense-delete&expenseid=" + expenseid + "&proposalid=" + proposalid)
    .always (function() {
      dialog.dialog("close");
      $("#warningDiv").html("<p>Deleted [" + expenseid + "]</p>");
      $("#warningDiv").show();

      loadTable('/expenses/ajax/list/' + proposalid, true, $('#expensesTable'));
      figureCosts(proposalid);
    });
}

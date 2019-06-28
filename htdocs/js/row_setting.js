// this will work even if the value chosen is not on the dropdown menu
// if this is null, the code will choose the first available option for size on the dropdown menu
var user_preference = 10;


function save_row_preference(table)
{
  // look up the data tables thing from wherever and figure out how to get the size from it
  // will be called by an onClick function from the button
  // will save this somewhere
  var table_row_size = table.page.len();
  console.log("New table row preference is " + table_row_size + " rows");


}


function check_row_preference(table)
{

  if (user_preference != null)
  {
    console.log(table.page.len());

   table.page.len(user_preference).draw();

    console.log(table.page.len());
  }


}

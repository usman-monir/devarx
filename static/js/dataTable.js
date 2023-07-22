const btn = document.createElement('button')
btn.setAttribute('id', "showUsers")
btn.classList.add("btn")
btn.classList.add("btn-primary")
btn.innerText = "Show Users"
document.body.append(btn)

function showTable(e) {
    $.ajax({
        type:"GET",
        url:'/usersTable',
        success: function(res){
            const table = document.createElement('table')
            table.setAttribute('id', "show")
            table.setAttribute('border', "2")
            document.body.append(table)
            $("#show").dataTable({
              data:res,
              columns:[{data: "id"},{data:"username"}, {data:"email"}],
              destroy:true,
            })
        }
    })
  }
$(document.body).on("click", "#showUsers", showTable);

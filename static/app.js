function getStatus(d) {
    console.print(d);
    objdata = d;
}

order = []
$('#orderButton').on('click', function () {
    $.ajax({
        url: '/result',
        data: $("input,select").serialize(),
        method: 'POST'
    })
        .done(function (res) {
            console.log(res);
            order = res;
            getStatus(res[0]);
            $('#formDiv').hide();
            $('#respName').append(res[1].name);
            $('#respDye').prepend(
                function () {
                    if (res[1].dye == "true") {
                        return "with"
                    }
                    return "without"
                });

            $('#respLid').prepend(
                function () {
                    if (res[1].lid == "true") {
                        return "with"
                    }
                    return "without"
                });
            $('#respTable').prepend(
                function () {
                    switch (res[1].table) {
                        case '1':
                            return "at Table 1";
                            break;
                        case `2`:
                            return "at Table 2";
                            break;
                        case `3`:
                            return "at Table 3";
                            break;
                        case `4`:
                            return "at mobile pickup";
                            break;
                        default:
                            return "by asking a staff member"
                    }
                });
            $('#orderConfirm').show()
            $('#statustable').show();

        });
});
$('#orderConfirm').hide()
$('#statustable').hide()


function getStatus(taskID) {
    $.ajax({
        url: `/tasks/${taskID}`,
        method: 'GET'
    })
        .done((res) => {
            console.log(res);

            const html = `
      <tr>
        <td>${res.data.task_id}</td>
        <td>${res.data.task_status}</td>
        <td>${res.data.task_result}</td>
      </tr>`
            $('#tasks').html(html);
            const taskStatus = res.data.task_status;
            if (taskStatus === 'Success' || taskStatus === 'failed') return false;
            setTimeout(function () {
                getStatus(res.data.task_id);
            }, 2000);
        })
        .fail((err) => {
            console.log(err)
        });
}
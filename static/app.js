
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
                    if (res[1].dye === "true") {
                        return "with"
                    }
                    return "without"
                });

            $('#respLid').prepend(
                function () {
                    if (res[1].lid === "true") {
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
            $('#orderID').text(res[0])
            $('#smallOrderID').show();
        });
});
$('#orderConfirm').hide()
$('#statustable').hide()
$('#smallOrderID').hide();

function getStatus(taskID) {
    $.ajax({
        url: `/tasks/${taskID}`,
        method: 'GET'
    })
        .done((res) => {
            console.log(res);
            console.log(res.data.task_percent)
            $("#orderProgressBar").width(res.data.task_percent + "%").attr("aria-valuenow", res.data.task_percent);
            if(0 <= res.data.task_percent < 100){
                $("#OrderProgressBar").addClass("bg-info").removeClass("bg-success").removeClass("progress-bar-striped");
            }
            if (res.data.task_percent === 100) {
                $("#orderProgressBar").addClass("bg-success").removeClass("progress-bar-striped");
            }
            if(res.data.task_status === "Error"){
                $("#orderProgressBar").addClass("bg-danger").removeClass("bg-success").removeClass("bg-info").removeClass("progress-bar-striped");
                $("#orderProgressBar").width(100 + "%").attr("aria-valuenow", 100);

            }

            $('.orderStatus').text(res.data.task_status);
            const taskStatus = res.data.task_status;
            if (taskStatus === 'Success' || taskStatus === 'failed' || taskStatus === "Error") return false;
            setTimeout(function () {
                getStatus(res.data.task_id);
            }, 750);
        })
        .fail((err) => {
            console.log(err)
        });
}
$("#line45").hide();

   $('#table').on('change',function(){
        if( $(this).val()==="4"){
        $("#line45").show()
        }
        else{
        $("#line45").hide()
        }
    });
jobIDList = []
function getStatus(taskID) {
    $.ajax({
        url: `/tasks/${taskID}`,
        method: 'GET'
    })
        .done((res) => {
            console.log(res)
           return res;

        })
        };


function evalID(jobID) {
    stat=getStatus(jobID);
    console.log(stat);

}
window.setInterval(function(){ // Run this code every 5 seconds
  /// call your function here
    $.ajax({
        url: `/updatescreen`,
        method: 'GET'
    })
        .done((res) => {

            jobIDList = $.merge(jobIDList, res.data.q);
            jobIDList = $.uniqueSort(jobIDList);
            jobIDList.forEach(evalID);
/*            $("#orderProgressBar").width(res.data.task_percent + "%").attr("aria-valuenow", res.data.task_percent);
            if (res.data.task_percent == 100) {
                $("#orderProgressBar").addClass("bg-success").removeClass("progress-bar-striped");
            }
            $('.orderStatus').text(res.data.task_status);
            const taskStatus = res.data.task_status;
            if (taskStatus === 'Success' || taskStatus === 'failed') return false;
            setTimeout(function () {
                getStatus(res.data.task_id);
            }, 2000);*/
        })
        .fail((err) => {
            console.log(err)
        });
}, 2500);
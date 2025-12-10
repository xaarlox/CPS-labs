jQuery(function($){

    $(".ipze-poll-vote").on("click", function(){

        let box = $(this).closest(".ipze-poll-box");
        let poll_id = box.data("poll-id");

        $.post(ipze_poll_ajax.url, {
            action: "ipze_poll_vote",
            poll: poll_id
        }, function(response){
            if(response.success){
                box.find(".ipze-poll-result").text(response.data.message);
            }
        });

    });

});


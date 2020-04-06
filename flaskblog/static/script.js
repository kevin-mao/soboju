$(document).ready(() => {
    jQuery.each( [ "put", "delete" ], function( i, method ) {
        jQuery[ method ] = function( url, data, callback, type ) {
          if ( jQuery.isFunction( data ) ) {
            type = type || callback;
            callback = data;
            data = undefined;
          }
      
          return jQuery.ajax({
            url: url,
            type: method,
            dataType: type,
            data: data,
            success: callback
          });
        };
      });

   
});

function addPage(){
    title = $(`#page`).val();
    $.post('/page', {title}, (response) => {
        console.log(response);
        response = JSON.parse(response);
        page_id = response.page_id;
    });
}

function addEntry(page_id){
    text = $(`#${page_id}-entry`).val();
    console.log(text);
    $.post('/entry', {page_id, text}, (response) => {
        console.log(response);
        response = JSON.parse(response);
        entry_id = response.entry_id;
    });
}

function editEntry(entry_id, entry_text) {
    console.log(entry_id)
     $(`#${entry_id}-entry-btn`).click(function(){
        console.log('yes')
        // {{entry.id}}-entry-row
        $(`#${entry_id}-entry-row`).empty()

        var input_box = $('<input type="text" id="input_entry">')
        $(`#${entry_id}-entry-row`).html(input_box)
        $("#input_entry").val(entry_text)

    })

}

function addGoal(page_id){
    text = $(`#${page_id}-goal`).val();
    console.log(text);
    $.post('/goal', {page_id, text}, (response) => {
        console.log(response);
        response = JSON.parse(response);
        goal_id = repsonse.goal_id;
    });
}

function addFriend(user_id){
    $.post('/friend', {user_id});
}

function addComment(text, user_id, entry_id, goal_id){
    if (entry_id) {
        $.post('/comment', {text, user_id, entry_id}, (response) => {
            console.log(response);
            response = JSON.parse(response);
            comment_id = repsonse.comment_id;
        });
    } else if (goal_id) {
        $.post('/comment', {text, user_id, goal_id}, (response) => {
            console.log(response);
            response = JSON.parse(response);
            comment_id = repsonse.comment_id;
        });
    }
}

function updatePage(page_id, title){
    $.put('/page', {page_id, title});
}

function updateEntry(entry_id, text){
    $.put('/page', {entry_id, text});
}

function updateGoal(goal_id, text){
    $.put('/page', {goal_id, text});
}

function updateComment(comment_id, user_id, text){
    $.put('/page', {comment_id, user_id, text});
}

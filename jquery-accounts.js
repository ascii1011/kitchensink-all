var fnNoteAdd;
$(document).ready(function(){
    fnNoteEdit = function( url, isEdit){
        $("#noteform").bind("keypress", function(e){
            if (e.keyCode==13) {
                $.ajax({
                    'url': url,
                    type: 'POST',
                    dataType: 'json',
                    headers: {'X-CSRFToken': getCookie('csrftoken')},
                    data: $("#noteform").ajaxForm().formSerialize(),
                    success: function(dat){
                        if (dat.message=='OK'){
                            $("#dialogbox").dialog('close');
                        } else {
                            $("#dialogbox").html(dat.html);
                        }
                    },
                    error: function(xhr,status,error){
                        console.log(xhr);
                    }
                });
                
            }
        });
        //console.log(isEdit);

        $("#dialogbox").load(url).dialog({
            'title': (isEdit != undefined )?'Edit Note':'Add Note' , 
            'stack': true, 'modal': true, 'draggable': true, 'resizeable': true, 'autoOpen': true, 'width': 500, 
            'height': 'auto', 
            'close': function(){
                $(".ui-dialog-buttonpane :button").removeClass('ui-state-focus');
                $(this).empty();
                $(this).removeClass('ui-state-focus');
            },
            'buttons': {
                'Submit': function(){
                    var $form=$('form', this);
                    //console.log( $('form', this).ajaxForm().formSerialize() );
                    $.ajax({
                        'url': url,
                        type: 'POST',
                        dataType: 'json',
                        headers: {'X-CSRFToken': getCookie('csrftoken')},
                        data: $form.ajaxForm().formSerialize(),
                        success: function(dat){
                            if (dat.message=='OK'){
                                $("#dialogbox").dialog('close');
                            } else {
                                $("#dialogbox").html(dat.html);
                            }
                        },
                        error: function(xhr,status,error){
                            console.log('something went wrong');
                            console.log(xhr);
                        }
                    });
                },
                'Close': function(){
                    $('#dialogbox').dialog('close');
                }
            }

        });
        
        return false;
    };



    $(".tabs").tabs();
    var oid=$("meta[name='oid']").attr("content");
    $(".notelink").click(function(){
        $("#dialogbox").load($(this).attr('href')).dialog({
            'title': 'Note',
            'stack': true,
            'modal': true,
            'draggable': false,
            'resizable': false,
            'autoOpen': true,
            'width': 500,
            'height': "auto",
            'close': function(){
                $(".ui-dialog-buttonpane :button").removeClass('ui-state-focus');
                $(this).empty();
                $(this).removeClass('ui-state-focus');
            }
        });
        return false;
    });

    $("#noteadd").click(function(){
        return fnNoteEdit($(this).attr('href'));
    });
    $(".editaddress").dblclick(function(){
        var tname=$(this).attr('rel');
        $("#addredit").load("/accounts/edit/"+oid+"/address/" + $(this).attr("rel") + "/").dialog({
            'title': $(this).attr("rel") + " address form",
            'stack': true,
            'modal': true,
            'draggable': false,
            'resizable': false,
            'autoOpen': true,
            'width': 500,
            'height': "auto",
            'close': function(){
                $(".ui-dialog-buttonpane :button").removeClass('ui-state-focus');
                $(this).empty();
                $(this).removeClass('ui-state-focus');
            },
            'buttons': {
                'Submit': function(){
                    $("#address_form").ajaxSubmit({
                        dataType: 'json',
                        success: function(data){
                            if (data.message=='OK'){
                                $("td.editaddress[rel='"+tname+"']").html(data['tabledata']);
                                $("#addredit").dialog('close');
                        } else {
                            $("#addredit").html(data['tabledata']);
                        }
                    }
                    });
                },
                'Cancel': function(){
                    $(this).dialog('close');
                }
            }
            
        });
        return false;
    });
});

$(document).ready(function(){

    /**************************************************************************
    *
    *                                      Gesion ADD REMOVE Formset 
    *
    ***************************************************************************/

    index_form = function( fset, index ){

        $(fset).find('input').each(function() {
            //var name = $(this).attr('name').replace( new RegExp('(\_\_prefix\_\_|\\d)') , index );
            var name = $(this).attr('name').replace(/__prefix__/g , index);
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id});
        });

        $(fset).find('label').each(function() {
            //var newFor = $(this).attr('for').replace( new RegExp('(\_\_prefix\_\_|\\d)') , index );
            var newFor = $(this).attr('for').replace(/__prefix__/g , index);
            var id = 'label_' + newFor;
            $(this).attr({'id':id, 'for':newFor});
        });

    }

    reindex_formset = function( formset_zone ){

        var formset = $(formset_zone).find( '.nsorte' );
        //for( var cpt=0;cpt<formset.length;cpt++ ){
             
          for( var cpt=0;cpt<10;cpt++ ){
            index_form( formset[cpt], cpt );
        };

        $("#id_form-TOTAL_FORMS").val( parseInt( cpt, 10));

    };



    /**************************************************************************
    *
    *                               Gesion Des evenements formulaire
    *
    ***************************************************************************/


    set_event = function(){
            //Bind le(s) bt delete sorte
            $(".bt_rm_sorte").on('click',function(){
                $(this).parents(".nsorte").remove();
                reindex_formset( "#formsetZone" );
            });
    };

    $("#bt_add_sorte").on('click',function(){

        //Copy eform
        $( "#eform" ).clone(true).appendTo( $("#formsetZone") );

        reindex_formset( "#formsetZone" );

    });

    set_event();


});

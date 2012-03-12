/*
 * CTEditor 1.0 - Categorized Tags Editor plugin for jQuery
 *
 * Licensed under the GPL license:
 *   http://www.gnu.org/licenses/gpl.html
 *
 */
(function($){
    $.fn.cteditor = function( params ){
        params = $.extend( {
            
        }, params);  
        return this.each(function(i,obj) {
            
            // express a single node as a jQuery object  
            var $t = $(this);
                
            // open modal with editor
            $('#cteditor').modal();
            
            if ( $t.data('cteditor') )
                return
            
            // create inputs for each category
            $('#cteditor select').each(function(){
                
                // create el
                var el = $('<input />').attr({
                    name: $(this).attr('name'),
                    value: '',
                    'class': 'cteditor-input'
                })
                
                // fill input after multiple-select
                $(this).attr('name', '_'+ $(this).attr('name') ).hide().after( el );
                
                // initialize textboxlist
                var t = new $.TextboxList(el, {unique: true, plugins: {autocomplete: {
                    minLength: 1,
                    onlyFromValues: true
                }}});
                
                // retrieve available tags
                var tags = [];
                $(this).children('option').each(function(){
                    tags.push([ $(this).val(), $(this).text() ]);
                    if ( $(this).attr('selected') )
                        t.add( $(this).text(), $(this).val() );
                });
                
                // adds to autocompleter
                t.plugins['autocomplete'].setValues(tags);
                
                $t.data('cteditor', t)
            });
        
        });
    }
})(jQuery);

/*
// retrieve arguments editor
$.get('index.php?page=arguments_editor', function(data) {
    
    $('#argumentEditor').html(data).on('shown', function() {
        $(this).find('.modal-header h3').addClass('textboxlist-loading'); 
    }).modal();
    
    // retrieve arguments
    $.getJSON('index.php?page=arguments&format=json', function(data) {
        
        // for each input initialize Textboxlist with retrieved arguments
        $('#argumentEditor input.arguments').each(function() {
            t = new $.TextboxList('#'+$(this).attr('id'), {unique: true, plugins: {autocomplete: {
                minLength: 1,
                onlyFromValues: true
            }}});
            t.plugins['autocomplete'].setValues(data);
        });
        $('#argumentEditor .modal-header h3').removeClass('textboxlist-loading'); 
    });
});*/
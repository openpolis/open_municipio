/*!
 * jQuery Submit Link plugin
 * Author: @joke2k
 * Licensed under the MIT license
 */

;(function ( $, window, document, undefined ) {

    $.fn.submitLink = function ( options ) {


        options = $.extend( {}, $.fn.submitLink.options, options );

        return this.each(function () {

            // hide forms
            var form = $(this).hide().submit(options.onSubmit);

            // search button to emulate
            var button = form.find(options.submitSelector);

            var link;
            if ( options.link ) {
                link = $(options.link)
            } else {
                // create ajax sender link
                link = $('<a />').prop({
                    'href' : '#'
                })
                // fill link with submit button contents
                if ( button.is('input'))
                {
                    link.html( button.html() )
                } else if( button.is('button') ) {
                    button.contents().each(function(){
                        link.append(this);
                    })
                }
                // inject content and insert before the form
                link.insertBefore(form)
            }

            link.on('click', function() {
                form.submit();
                return false;
            });
/*
            // create ajax sender link
            var link = $('<a />').prop({
                'href' : '#'
            }).on('click', function() {
                form.submit();
                return false;
            });
            button.contents().each(function(){
                link.append(this);
            });
            // inject content and insert before the form
            $(this).before( link );*/
        });
    };

// Globally overriding options

    $.fn.submitLink.options = {

        submitSelector: '*[type="submit"]',
        link: undefined,
        onSubmit: function() { }
    };

})( jQuery, window, document );


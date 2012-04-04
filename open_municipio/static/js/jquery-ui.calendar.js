jQuery(document).ready(function($) {
    /* Italian initialisation for the jQuery UI date picker plugin. */
    /* Written by Antonello Pasella (antonello.pasella@gmail.com). */
    /* http://jquery-ui.googlecode.com/svn/trunk/ui/i18n/jquery.ui.datepicker-it.js */

    $.datepicker.regional['it'] = {
        closeText: 'Chiudi',
        prevText: '&#x3c;Prec',
        nextText: 'Succ&#x3e;',
        currentText: 'Oggi',
        monthNames: ['Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno','Luglio','Agosto','Settembre','Ottobre','Novembre','Dicembre'],
        monthNamesShort: ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'],
        dayNames: ['Domenica','Luned&#236','Marted&#236','Mercoled&#236','Gioved&#236','Venerd&#236','Sabato'],
        dayNamesShort: ['Dom','Lun','Mar','Mer','Gio','Ven','Sab'],
        dayNamesMin: ['Do','Lu','Ma','Me','Gi','Ve','Sa'],
        weekHeader: 'Sm',
        dateFormat: 'mm/dd/yy',
        firstDay: 1,
        isRTL: false,
        showMonthAfterYear: false,
        yearSuffix: ''};

    $.datepicker.setDefaults($.datepicker.regional['it']);

    var scrollTo = function(container, target, duration)
    {
        //console.log('scroll', container, 'to', $(target) );

        var $container = $(container),
            $target = $(target);

        // Prepare the Inline Element of the Container
        var $inline = $('<span/>').css({
            'position': 'absolute',
            'top': '0px',
            'left': '0px'
        });
        var position = $container.css('position');

        // Insert the Inline Element of the Container
        $container.css('position','relative');
        $inline.appendTo($container);

        // Determine the Offsets
        var	startOffset = $inline.offset().top,
            targetOffset = $target.offset().top,
            offsetDifference = targetOffset - startOffset;

        // Reset the Inline Element of the Container
        $inline.remove();
        $container.css('position',position);

        // Perform the Scroll
        $container.animate({
            'scrollTop': offsetDifference+'px'
        }, duration||2000 );

    }


    // extends Datepicker to Calendar
    // http://jsfiddle.net/Zrz9t/2/
    $('.calendar').each(function(){

        var events = [];
        $( $(this).data('events') ).children().each(function() {

            if (!$(this).data('day') )
            {
                if ( $(this).data('month') )
                {
                    $(this).prop('id', $(this).data('month').replace(/\//gi,'') );
                }
                return;
            }
            else
            {
                $(this).prop('id', $(this).data('day').replace(/\//gi,'') );
            }

            var event = {
                Title: $(this).text(),
                Date: new Date($(this).data('day')),
                Id: $(this).prop('id')
            };
            events.push(event);
        });

        // Load Datepicker
        var today = new Date();
        var event_container = $( $(this).data('events') );
        $(this).datepicker({
            inline: true,
            minDate: new Date(today.getFullYear(), today.getMonth()-1, 1),
            beforeShowDay: function(date) {
                var result = [true, '', null];
                var matching = $.grep(events, function(event) {
                    return event.Date.valueOf() === date.valueOf();
                });

                if (matching.length) {
                    result = [true, 'highlight', null];
                }
                return result;
            },
            onChangeMonthYear: function(year, month, inst) {
                var date,
                    i = 0,
                    event = null;

                var monthId = '#'+ ((month < 10) ? ("0" + month) : month) + year;

                if ( $(monthId).length )
                {
                    scrollTo(event_container,monthId);
                    return;
                }

                while (i < events.length && !event) {
                    date = events[i].Date;

                    if ( (month === (date.getMonth()+1)) && (year === (date.getFullYear())) ) {
                        event = events[i];
                    }
                    i++;
                }
                if (event) {
                    scrollTo(event_container,'#'+event.Id);

                    /*$('#'+event.Id).ScrollTo({
                        offset: 50
                    });*/
                }
            },
            onSelect: function(dateText) {
                var date,
                    selectedDate = new Date(dateText),
                    i = 0,
                    event = null;

                while (i < events.length && !event) {
                    date = events[i].Date;

                    if (selectedDate.valueOf() === date.valueOf()) {
                        event = events[i];
                    }
                    i++;
                }

                if (event) {
                    scrollTo(event_container,'#'+event.Id);
                    /*
                    $('#'+event.Id).ScrollTo({
                        offset: 50
                    });*/
                }
            }
        });
    });



});
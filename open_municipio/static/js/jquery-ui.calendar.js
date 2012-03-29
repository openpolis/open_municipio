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

    // extends Datepicker to Calendar
    // http://jsfiddle.net/Zrz9t/2/

    $('.calendar').each(function(){

        var events = [];
        $( $(this).data('events') ).children().each(function() {
            var event = {
                Title: $(this).text(),
                'Date': new Date($(this).data('day'))
            };
            console.log(event);
            events.push(event);
        });
        console.log('events initialized from',$(this).data('events'), events);

        // Load Datepicker
        $(this).datepicker({
            inline: true,
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
                console.log(event);
                if (event) {
                    alert(event.Title);
                }
            }
        });
    });



});
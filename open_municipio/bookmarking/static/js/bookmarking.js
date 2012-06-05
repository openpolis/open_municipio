/**
This script binds a ``onclick`` event to any DOM element with class ``bookmarkable``.

When a such click event is triggered, the handler sends a POST AJAX request to
the URL ``/bookmark/<app_label>/<model_name>/<obj_pk>/toggle/``, that is
supposed to toggle the "bookmarked" flag for the model instance identified by
the 3-tuple of coordinates ``(<app_label>, <model_name>, <obj_pk>)``, where:

* ``<app_label>`` is the "app label" for the model instance -- as intended by Django
* ``<model_name>`` is the (lowercased) name of the model
* ``<obj_pk>`` is the primary key of the model instance

These parameters must be provided to the handler by encoding them within the
``id`` attribute of the DOM element marked with the ``bookmarkable`` class,
using the following format:

    id="<app_label>-<model_name>-<obj_pk>" (e.g. id="acts-act-5")

If the POST request succeeds, the class of the "bookmarkable" element will be
toggled between the values ``icon-star``, ``icon-star-empty``.  These classes,
in turn, may be used to modify the visual appearance of the element, e.g. by
displaying different icon images depending on the element's class.
**/

$(document).ready(function() {
    $('.bookmarkable').click(function () {
      $that = $(this);
      var params = $(this).attr('id').split('-');
      var app_label = params[0];
      var model_name = params [1];
      var obj_pk = params[2];
      $.post('/bookmark/' + app_label + '/' + model_name + '/' + obj_pk + '/toggle/', 
        function(data){
          if (data.success == true) {
              $that.find('i').toggleClass("icon-star icon-star-empty").attr('title', data.message);
          } else {
		      alert('ERROR: ' + data.error_message);
	        }
        }, 'json');
      return false;
    });
});
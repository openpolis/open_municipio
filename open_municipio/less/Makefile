BOOTSTRAP = ../static/css/bootstrap.css
BOOTSTRAP_LESS = ./bootstrap.less
BOOTSTRAP_RESPONSIVE = ../static/css/bootstrap-responsive.css
BOOTSTRAP_RESPONSIVE_LESS = ./responsive.less
LESS_COMPRESSOR ?= `which lessc`
WATCHR ?= `which watchr`


#
# BUILD SIMPLE BOOTSTRAP DIRECTORY
# lessc & uglifyjs are required
#

bootstrap:
	lessc ${BOOTSTRAP_LESS} > ${BOOTSTRAP}
#	${LESSCPATH}lessc --compress ${BOOTSTRAP_LESS} > bootstrap/css/bootstrap.min.css
	lessc ${BOOTSTRAP_RESPONSIVE_LESS} > ${BOOTSTRAP_RESPONSIVE}
#	${LESSCPATH}lessc --compress ${BOOTSTRAP_RESPONSIVE_LESS} > bootstrap/css/bootstrap-responsive.min.css
#	cat js/bootstrap-transition.js js/bootstrap-alert.js js/bootstrap-button.js js/bootstrap-carousel.js js/bootstrap-collapse.js js/bootstrap-dropdown.js js/bootstrap-modal.js js/bootstrap-tooltip.js js/bootstrap-popover.js js/bootstrap-scrollspy.js js/bootstrap-tab.js js/bootstrap-typeahead.js > bootstrap/js/bootstrap.js
#	uglifyjs -nc bootstrap/js/bootstrap.js > bootstrap/js/bootstrap.min.js

#
# WATCH LESS FILES
#

watch:
	echo "Watching less files..."; \
    watchr -e "watch('less/.*\.less') { system 'make' }"


.PHONY: dist docs watch gh-pages

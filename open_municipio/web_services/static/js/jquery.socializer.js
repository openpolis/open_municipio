/*
 jquery.fbjlike.js - http://socialmediaautomat.com/jquery-fbjlike-js.php
 based on: jQuery OneFBLike v1.1 - http://onerutter.com/open-source/jquery-facebook-like-plugin.html
 Copyright (c) 2010 Jake Rutter modified 2011 by Stephan Helbig
 This plugin available for use in all personal or commercial projects under both MIT and GPL licenses.
 */

(function($){

    $.fn.fbjlike = function(options) {

        //Set the default values, use comma to separate the settings
        var defaults = {
            appID: '224229974253687',
            siteTitle: '',
            siteName: '',
            siteImage: '',
            buttonWidth: 450,
            buttonHeight: 60,
            showfaces: true,
            font: 'lucida grande',
            layout: 'normal',
            action: 'like',
            colorscheme: 'light',
            lang: 'en_US',
            hideafterlike:false,
            onlike: function(){return true;},
            onunlike: function(){return true;}
        }

        var options =  $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            var dynUrl = document.location;

            // Add Meta Tags for additional data - options
            if(o.siteTitle!='')$('head').append('<meta property="og:title" content="'+o.siteTitle+'"/>');
            if(o.siteName!='')$('head').append('<meta property="og:site_name" content="'+o.siteName+'"/>');
            if(o.siteImage!='')$('head').append('<meta property="og:image" content="'+o.siteImage+'"/>');

            // Add #fb-root div - mandatory - do not remove
            $('body').append('<div id="fb-root"></div>');
            $('#fb-like iframe').css('height','35px !important');

            (function() {
                var e = document.createElement('script');
                e.async = true;
                e.src = document.location.protocol + '//connect.facebook.net/'+o.lang+'/all.js';
                $('#fb-root').append(e);
            }());

            // setup FB Developers App Link - do not touch
            window.fbAsyncInit = function() {
                FB.init({appId: o.appID, status: true, cookie: true, xfbml: true});
                FB.Event.subscribe('edge.create', function(response) {
                    if(o.hideafterlike)$(obj).hide();
                    o.onlike.call(response);
                });
                FB.Event.subscribe('edge.remove', function(response) {
                    o.onunlike.call(response);
                });
            };

            // Apply the like button to an element on the page and include all available options
            // If no options are passed in from the page, the defaults will be applied
            $(obj).html('<fb:like href="'+dynUrl+'" width="'+o.buttonWidth+'" height="'+o.buttonHeight+'" show_faces="'+o.showfaces+'" font="'+o.font+'" layout="'+o.layout+'" action="'+o.action+'" colorscheme="'+o.colorscheme+'"/>');

        });
    };



/*
 jquery.gplusone.js - http://socialmediaautomat.com/jquery-gplusone-js.php
 Copyright (c) 2011 Stephan Helbig
 This plugin available for use in all personal or commercial projects under both MIT and GPL licenses.
 */

    $.fn.gplusone = function(options) {

        //Set the default values, use comma to separate the settings
        var defaults = {
            mode: 'insert',											//insert|append
            size: 'standard',										//small|medium|standard|tall
            count: true,												//true|false
            href: false,												//false|url
            lang: 'en-US',											//en-US|en-GB|de|es|fr|...
            hideafterlike:false,								//true|false (only possible with mode: 'insert')
            googleanalytics:false,							//true|false
            googleanalytics_obj: 'pageTracker',	//pageTracker|_gaq
            onlike: "return true;",
            onunlike: "return true;"
        }

        var options =  $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            var dynUrl = document.location;
            var dynTitle = document.title.replace("'",'&apos;');

            if(!o.href){
                o.href=dynUrl;
            }
            var strcount='false';
            if(o.count){
                strcount='true';
            }
            (function() {
                var e = document.createElement('script');
                e.async = true;
                e.src = document.location.protocol + '//apis.google.com/js/plusone.js';
                $(e).append("{lang: '"+o.lang+"'}");

                $('head').append(e);
                var e = document.createElement('script');
                var hidefunc = '';
                if(o.hideafterlike){
                    hidefunc = '$(obj).hide();';
                }
                var gfunclike = '';
                var gfuncunlike = '';
                if(o.googleanalytics){
                    if(o.googleanalytics_obj!='_gaq'){
                        gfunclike = o.googleanalytics_obj+"._trackEvent('google', 'plussed', '"+dynTitle+"');";
                        gfuncunlike = o.googleanalytics_obj+"._trackEvent('google', 'unplussed', '"+dynTitle+"');";
                    } else {
                        gfunclike = o.googleanalytics_obj+".push(['_trackEvent','google', 'plussed', '"+dynTitle+"']);";
                        gfuncunlike = o.googleanalytics_obj+".push(['_trackEvent','google', 'unplussed', '"+dynTitle+"']);";
                    }
                }
                $(e).append("function gplus_callback(r){if(r.state=='on'){"+hidefunc+gfunclike+o.onlike+"}else{"+gfuncunlike+o.onunlike+"}}");
                $('head').append(e);
            }());

            var thtml = '<g:plusone size="'+o.size+'" callback="gplus_callback" href="'+o.href+'" count="'+strcount+'"></g:plusone>';
            if(o.mode=='insert')
                $(obj).html(thtml);
            else
                $(obj).append(thtml);
        });
    };



/*
 jquery.twitterbutton.js - http://socialmediaautomat.com/jquery-twitterbutton-js.php
 Copyright (c) 2011 Stephan Helbig
 This plugin available for use in all personal or commercial projects under both MIT and GPL licenses.
 */


    $.fn.twitterbutton = function(options) {

        //Set the default values, use comma to separate the settings
        var defaults = {
            user: false,
            user_description: false,
            url: false,
            count_url: false,
            title: false,
            mode: 'insert',
            layout: 'vertical', //vertical|horizontal|none
            action: 'tweet',		//tweet|follow
            lang: 'en',					//en|de|ja|fr|es
            hideafterlike:false,
            googleanalytics:false,							//true|false
            googleanalytics_obj: 'pageTracker',	//pageTracker|_gaq
            ontweet: function(){return true;},
            onretweet: function(){return true;},
            onfollow: function(){return true;}
        }

        var options =  $.extend(defaults, options);
        var script_loaded = false;
        return this.each(function() {
            var o = options;
            var obj = $(this);
            if(!o.url) var dynUrl = document.location;
            else var dynUrl = o.url;
            if(!o.title)var dynTitle = document.title;
            else var dynTitle = o.title;

            if(!o.count_url)o.count_url=dynUrl;

            if(!script_loaded){
                var e = document.createElement('script'); e.type="text/javascript"; e.async = true;
                e.src = 'http://platform.twitter.com/widgets.js';
                (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(e);

                $(e).load(function() {
                    function clickEvent(intent_event) {
                        if (intent_event) {
                            var label = intent_event.region;
                            if(o.googleanalytics){
                                if(o.googleanalytics_obj!='_gaq'){
                                    _gaq.push(['_trackEvent', 'twitter_web_intents', intent_event.type, label]);
                                } else {
                                    pageTracker._trackEvent('twitter_web_intents', intent_event.type, label);
                                }
                            }
                        };
                    }
                    function tweetIntent(intent_event) {
                        if (intent_event) {
                            var label = intent_event.data.tweet_id;
                            if(o.googleanalytics){
                                if(o.googleanalytics_obj!='_gaq'){
                                    _gaq.push(['_trackEvent', 'twitter_web_intents', intent_event.type, label]);
                                } else {
                                    pageTracker._trackEvent('twitter_web_intents', intent_event.type, label);
                                }
                            }
                            o.ontweet.call(intent_event);
                            if(o.hideafterlike)$(obj).hide();
                        };
                    }
                    function favIntent(intent_event) {
                        tweetIntent(intent_event);
                    }
                    function retweetIntent(intent_event) {
                        if (intent_event) {
                            var label = intent_event.data.source_tweet_id;
                            if(o.googleanalytics){
                                if(o.googleanalytics_obj!='_gaq'){
                                    _gaq.push(['_trackEvent', 'twitter_web_intents', intent_event.type, label]);
                                } else {
                                    pageTracker._trackEvent('twitter_web_intents', intent_event.type, label);
                                }
                            }
                            o.onretweet.call(intent_event);
                            if(o.hideafterlike)$(obj).hide();
                        };
                    }
                    function followIntent(intent_event) {
                        if (intent_event) {
                            var label = intent_event.data.user_id + " (" + intent_event.data.screen_name + ")";
                            if(o.googleanalytics){
                                if(o.googleanalytics_obj!='_gaq'){
                                    _gaq.push(['_trackEvent', 'twitter_web_intents', intent_event.type, label]);
                                } else {
                                    pageTracker._trackEvent('twitter_web_intents', intent_event.type, label);
                                }
                            }
                            o.onfollow.call(intent_event);
                            if(o.hideafterlike)$(obj).hide();
                        };
                    }
                    twttr.events.bind('click',    clickEvent);
                    twttr.events.bind('tweet',    tweetIntent);
                    twttr.events.bind('retweet',  retweetIntent);
                    twttr.events.bind('favorite', favIntent);
                    twttr.events.bind('follow',   followIntent);
                    script_loaded = true;
                });
            }


            if(o.action=='tweet'){
                var via = '';
                var related = '';
                if(o.user!=false){
                    via = 'data-via="'+o.user+'" ';
                    if(o.user_description!=false){
                        related = 'data-related="'+o.user+':'+o.user_description+'" ';
                    }
                }
                var counturl = '';
                if(o.count_url!=dynUrl)counturl = 'data-counturl="'+o.count_url+'" ';
                var thtml = '<div><a href="http://twitter.com/share" class="twitter-share-button" data-url="'+dynUrl+'" '+counturl+''+via+'data-text="'+dynTitle+'" data-lang="'+o.lang+'" '+related+'data-count="'+o.layout+'">Tweet</a></div>';
            } else {
                var thtml = '<div><a href="http://twitter.com/'+o.user+'" class="twitter-follow-button">Follow</a></div>';
            }
            if(o.mode=='append')$(obj).append(thtml);
            else $(obj).html(thtml);

        });
    }
})(jQuery);
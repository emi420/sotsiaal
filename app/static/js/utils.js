        if( !window.XMLHttpRequest ) XMLHttpRequest = function()
        {
            try{ return new ActiveXObject("Msxml2.XMLHTTP.6.0") }catch(e){}
            try{ return new ActiveXObject("Msxml2.XMLHTTP.3.0") }catch(e){}
            try{ return new ActiveXObject("Msxml2.XMLHTTP") }catch(e){}
            try{ return new ActiveXObject("Microsoft.XMLHTTP") }catch(e){}
            throw new Error("Could not find an XMLHttpRequest alternative.")
        };

        // AJAX request
        function AjaxRequest(function_name, opt_argv_names, opt_argv, callback) {
            // Find if the last arg is a callback function; save it
            var async = (callback != null);
  
            // Encode the arguments in to a URI
            var query = '';
            for (var i = 0; i < opt_argv.length; i++) {
                var key = opt_argv_names[i];
                var val = JSON.stringify(opt_argv[i]);
                query += '&' + key + '=' + encodeURIComponent(val);
            }
            query += '&time=' + new Date().getTime(); // IE cache workaround

            // Create an XMLHttpRequest 'GET' request w/ an optional callback handler 
            var req = new XMLHttpRequest();
            req.open('GET', '/ajax/' + function_name + '/?' + query, async);
         
            if (async) {
                req.onreadystatechange = function() {
                    if(req.readyState == 4 && req.status == 200) {
                        var response = null;
                        try {
                            response = JSON.parse(req.responseText);
                        } catch (e) {
                            response = req.responseText;
                        }
                        callback(response);
                    }
                }
            }
         
            // Make the actual request
            req.send(null);
        }

		// Name: createXMLDocument
		// Input: String
		// Output: XML Document
		jQuery.createXMLDocument = function(string) {
			var browserName = navigator.appName;
			var doc;
			if (browserName == 'Microsoft Internet Explorer')
			{
				doc = new ActiveXObject('Microsoft.XMLDOM');
				doc.async = 'false'
				doc.loadXML(string);
			} else {
				doc = (new DOMParser()).parseFromString(string, 'text/xml');
			}
			return doc;
		}


        // Handy "macro"
        function ebid(id){
            return document.getElementById(id);
        }

        // Funciones que llaman al RPC
        function doAddMessage() {
        	if ( visualFX.currentAction == 'pub-image' || visualFX.currentAction == 'pub-doc') {
	        	alert('ok ajax');
	            //AjaxRequest('add_friend', ['friendkey', 'userkey'], [friendkey, userkey], onAddSuccess);
	        } else {
	        	ebid('sndfrm').submit();
	        }
        }

        function doAddFriend(friendkey, userkey) {
            ebid('link-follow').innerHTML = 'Cargando..' ;
            AjaxRequest('add_friend', ['friendkey', 'userkey'], [friendkey, userkey], onAddSuccess);
        }

        function doRemoveFriend(friendkey, userkey) {
            ebid('link-follow').innerHTML = 'Cargando..' ;
            AjaxRequest('remove_friend', ['friendkey', 'userkey'], [friendkey, userkey], onRemoveSuccess);
        }

        function getStoryWall(storykey) {
            ebid('story-menu-item1').className = 'selected' ;
            ebid('story-menu-item2').className = 'style1' ;
            ebid('story-menu-item3').className = 'style2' ;
            // ebid('story-menu-item3').className = 'style2' ;
            ebid('story-wall').style.display = 'block' ;
            ebid('story-wall-2').style.display = 'none' ;
        }

        function activateCommentControls() {
            visualFX.loadTabsX('tx_control') ;
            var eMap = document.getElementById('t_map') ;
           /* $( eMap ).removeClass('hidden');
            $().ready( function(){ load(); } );
            $( eMap ).addClass('hidden');*/
			$('#lnk-map').click(function() {
			 loadGMapsAPI();
			});

			/*var oHead = document.getElementsByTagName('HEAD').item(0);

			var oScript= document.createElement("script");
			oScript.type = "text/javascript";
			oScript.src="http://maps.google.com/maps?file=api&amp;v=3&amp;key={{ gmaps_api_key }}";

			var oScript2= document.createElement("script");
			oScript2.type = "text/javascript";
			oScript2.src="/static/js/gmaps.js";

			var oScript3= document.createElement("script");
			oScript3.type = "text/javascript";
			oScript3.src="http://gmaps-utility-library.googlecode.com/svn/trunk/markermanager/release/src/markermanager.js";

			oHead.appendChild( oScript);
			oHead.appendChild( oScript2);
			oHead.appendChild( oScript3);*/
        }

        function getStoryFollowers(storykey) {
            ebid('story-menu-item1').className = 'style0' ;
            ebid('story-menu-item2').className = 'selected' ;
            ebid('story-menu-item3').className = 'style2' ;
            // ebid('story-menu-item3').className = 'style2' ;
            ebid('story-wall').style.display = 'none' ;
            ebid('story-wall-2').style.display = 'block' ;
            ebid('story-wall-2').innerHTML = '<p class="loading-msg"><span>Cargando...</span></p>' ;
            AjaxRequest('story_followers', ['storykey'], [storykey], onGetStoryFollowersSuccess);
        }

        function getStoryPrintOptions(storykey) {
            ebid('story-menu-item1').className = 'style0' ;
            ebid('story-menu-item2').className = 'style1' ;
            ebid('story-menu-item3').className = 'selected' ;
            // ebid('story-menu-item3').className = 'style2' ;
            ebid('story-wall').innerHTML = '<p class="loading-msg"><span>Cargando...</span></p>' ;
            AjaxRequest('story_print_options', ['storykey'], [storykey], onGetStoryPrintOptionsSuccess);
        }

        function getMoreMessages(storykey, page) {
            ebid('more-messages').innerHTML = '<p class="loading-msg"><span>Cargando...</span></p>' ;
            AjaxRequest('more_story_messages', ['storykey', 'page'], [storykey, page], onGetMoreMessagesSuccess);
        }

        function doDeleteCurrentAvatar(userkey) {
            ebid('delete-current-avatar').getElementsByTagName('a')[0].innerHTML = 'Borrando..' ;
            AjaxRequest('delete_avatar', ['userkey'], [userkey], onDeleteCurrentAvatarSuccess);
        }

        function doDeleteCurrentBg(userkey) {
            ebid('delete-current-bg').getElementsByTagName('a')[0].innerHTML = 'Borrando..' ;
            AjaxRequest('delete_bg', ['userkey'], [userkey], onDeleteCurrentBgSuccess);
        }

        function doDeleteCurrentBanner(userkey) {
            ebid('delete-current-banner').getElementsByTagName('a')[0].innerHTML = 'Borrando..' ;
            AjaxRequest('delete_banner', ['userkey'], [userkey], onDeleteCurrentBannerSuccess);
        }

        function doDeleteMsg(msgkey) {
            ebid('deletemsg-' + msgkey).innerHTML = 'Borrando..' ;
            AjaxRequest('delete_message', ['msgkey'], [msgkey], onDeleteMsgSuccess);
        }

        function doDeleteReply(replykey) {
            ebid('deletereply-' + replykey).innerHTML = 'Borrando..' ;
            AjaxRequest('delete_reply', ['replykey'], [replykey], onDeleteReplySuccess);
        }

        function doVoteMsg(msgkey, votetype) {
            ebid('pts-msg-' + msgkey).innerHTML = '...' ;
            AjaxRequest('vote_msg', ['msgkey', 'votetype'], [msgkey, votetype], onVoteMsgSuccess);
        }

        function doVoteReply(replykey, votetype) {
            ebid('pts-reply-' + replykey).innerHTML = '...' ;
            AjaxRequest('vote_reply', ['replykey', 'votetype'], [replykey, votetype], onVoteReplySuccess);
        }

        function doVoteStory(storykey, votetype) {
            $('#pts-story-' + storykey).fadeOut('slow') ;
            AjaxRequest('vote_story', ['storykey', 'votetype'], [storykey, votetype], onVoteStorySuccess);
        }

        function GetNewStoryImgSrc(url) {
            AjaxRequest('local_proxy', ['url'], [url], onGetNewStoryImgSrcSuccess);
        }

        function GetStoriesFromFeed(feed) {
            AjaxRequest('get_stories_from_feed', ['feed'], [feed], onGetStoriesFromFeedSuccess);
        }
		
        // Callbacks
		
        function onGetStoriesFromFeedSuccess(response) {
			var ul = ebid('feed-story-list') ;
			var xml = $.createXMLDocument(response);
			var titles = xml.getElementsByTagName('title')
			var descriptions = xml.getElementsByTagName('description')
			var links = xml.getElementsByTagName('link')

			for( var i = 0 ; i < titles.length ; i++ ) {
				var li = document.createElement('li') ;
				li.innerHTML = '<h2>' + titles[i].textContent + '</h2>';
				li.innerHTML += '<label>T&iacute;tulo</label><input class="text-input" id="title_' + i + '" name="title_' + i + '" type="text" value="' + titles[i].textContent + '"/><div class="clear"></div>'  ;
				li.innerHTML += '<label>Descripci&oacute;n</label><input class="text-input" id="description_' + i + '" name="description_' + i + '" type="text" value="' + descriptions[i].textContent.substring(0, 255).replace('<','').replace('>','').replace('"','') + '..."/><div class="clear"></div>'  ;
				li.innerHTML += '<label>Enlace</label><input class="text-input" id="link_' + i + '" name="link_' + i + '" type="text" value="' + links[i].textContent + '"/><div class="clear"></div>'  ;
				li.innerHTML += '<label>Categor&iacute;a</label><select class="select" name="category_' + i + '" id="category_' + i + '"><option selected="selected" value="mas">M&aacute;s</option><option value="gobierno">Gobierno</option><option value="justicia">Justicia</option><option value="medioambiente">Medio ambiente</option><option value="transporte">Transporte</option><option value="productos">Productos</option><option value="servicios">Servicios</option></select><div class="clear"></div>' ;
				ul.appendChild(li) ;				 
			 } //
             var li = document.createElement('li') ;
             li.innerHTML += '<input name="items-count" id="items-count" value="' + i + '" type="hidden" />' ;
             ul.appendChild(li) ;				 

			 ebid('feed_stories_count').innerHTML = titles.length ;
        }		

        function onGetNewStoryImgSrcSuccess(response) {
			img = ebid('url_img') ;
			img.src = response ;
			ebid('url_img_value').value = response ;
			document.getElementById('img').style.display='none';
			document.getElementById('img_t').style.display='none';
			document.getElementById('imgfile').style.display='none';
			document.getElementById('delete-current-img').style.display='block';
			document.getElementById('url_img').style.display='block';
        }

        function onAddSuccess(response) {
            if ( response == 1 ) {
                ebid('link-follow').onclick = 'void()' ;
            }
            ebid('link-follow').innerHTML = 'Listo!' ;
        }

        function onRemoveSuccess(response) {
            if ( response == 1 ) {
                ebid('link-follow').onclick = 'void()' ;
            }
            ebid('link-follow').innerHTML = 'Listo!' ;
        }

        function onGetStoryFollowersSuccess(response) {
           ebid('story-wall-2').innerHTML = response ;
        }

        function onGetStoryPrintOptionsSuccess(response) {
            ebid('story-wall').innerHTML = response ;
        }

        function onGetMoreMessagesSuccess(response) {
            ebid('story-messages').removeChild(ebid('more-messages'));
            ebid('story-messages').innerHTML += response;
        }

       function onDeleteCurrentAvatarSuccess(response) {
            ebid('delete-current-avatar').style.display = 'none' ;
            ebid('img-current-avatar').src = '/static/img/det/avatar.png' ;
        }

        function onDeleteCurrentBgSuccess(response) {
            ebid('delete-current-bg').style.display = 'none' ;
            ebid('img-current-bg').src = '/static/img/bg-body.png' ;
        }

        function onDeleteCurrentBannerSuccess(response) {
            ebid('delete-current-banner').style.display = 'none' ;
            ebid('img-current-banner').src = '/static/img/det/avatar.png' ;
        }

        function onDeleteMsgSuccess(response) {
            ebid('deletemsg-' + response).innerHTML = 'listo!' ;
            ebid('comment-' + response).setAttribute('class','comment-hidden deleted') ;
            ebid('title-' + response).innerHTML = '<p>Comentario borrado</p>' ;
            ebid('title-' + response).style = 'display: block !important' ;
        }

        function onDeleteReplySuccess(response) {
            ebid('deletereply-' + response).innerHTML = 'listo!' ;
            ebid('reply-' + response).setAttribute('class','reply-hidden deleted') ;
            ebid('reply-inside-' + response).innerHTML = '<p>Comentario borrado</p>' ;
            ebid('teply-inside-' + response).style = 'display: block !important' ;
        }

        function onVoteMsgSuccess(response) {
            ebid('pts-msg-' + response.split(" ")[0]).innerHTML = response.split(" ")[1] ;
        }

        function onVoteReplySuccess(response) {
            ebid('pts-reply-' + response.split(" ")[0]).innerHTML = response.split(" ")[1] ;
        }

        function onVoteStorySuccess(response) {
            ebid('pts-story-' + response.split(" ")[0]).innerHTML = response.split(" ")[1] ;
            $('#pts-story-' + response.split(" ")[0]).fadeIn('fast') ;
			if(response.split(" ")[2] == 'remove') {
				ebid('box-welcome').setAttribute('class','box welcome buried')
				$('#pts-story-' + response.split(" ")[0]).fadeIn('fast') ;
				$('#link-bury').fadeOut('fast') ;
				ebid('vote-button-li').innerHTML = 'Enterrado' ;
			} else {			
				ebid('vote-button-li').innerHTML = 'Votado' ;
			}
       }
       
       

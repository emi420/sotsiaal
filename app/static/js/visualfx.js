/*
 * Proyecto 83 - http://proyecto83.com - "Simplify, simplify, simplify"
 * Copyright (C) 2008 Emilio Mariscal
 * 
 * == BEGIN LICENSE ==
 * 
 * Licensed under the terms of any of the following licenses at your
 * choice:
 * 
 *  - GNU General Public License Version 2 or later (the "GPL")
 *    http://www.gnu.org/licenses/gpl.html
 * 
 *  - GNU Lesser General Public License Version 2.1 or later (the "LGPL")
 *    http://www.gnu.org/licenses/lgpl.html
 * 
 * == END LICENSE ==
 * 
 *  File Name  :
 *
 *  visualfx.js
 *
 * File Authors :
 *      Emilio Mariscal ( emi420@gmail.com )
 */
 
 
var visualFX = {

    /*** DropDown menu ***/
    
    cDDMenu: 0,         // Control DropDown menu
    aDDMenu: null,      // Array DropDown menu
    eMenu : null,       // Elemento menu
    aMenuList : null,   // Array menu (listado)
    cMenu : 0,          // Control menu 

    currentAction: '',
    
    loadDDMenu: function( eId ) {
    
        visualFX.aDDMenu = new Array() ;
        var eMenu = document.getElementById(eId) ;      
        var eMenuContent = document.getElementById( eMenu.id + '_c' ) ;
        var leftPos = visualFX.getLeftPos(eMenu) - 195 ;

        eMenuContent.style.left = leftPos + 'px';
        
        eMenu.onclick = function () { 

            eMenuContent = document.getElementById( this.id + '_c' ) ;
            eMenu = document.getElementById( this.id ) ;
            visualFX.aDDMenu[visualFX.aDDMenu.length] = eMenuContent ;
            visualFX.hideDDMenus() ;
            
            visualFX.cDDMenu = 1 ;
            
            if(eMenuContent.style.display == 'none') {
                eMenuContent.style.display = 'block' ;
            } else {
                eMenuContent.style.display = 'none' ;
            }
        } ;
        
        var aMenuElements = eMenuContent.getElementsByTagName('li') ;
        
        for(i = 0 ; i < aMenuElements.length ; i++ ) {
            aMenuElements[i].onmouseout = function() {
                visualFX.cDDMenu = 0 ;
                setTimeout( "if(visualFX.cDDMenu==0) visualFX.hideDDMenus() ;" , visualFX.ConfigMenuTimeOut ); 
            } ;
        }
        
        for(i = 0 ; i < aMenuElements.length ; i++ ) {
            aMenuElements[i].onmouseover = function() {
                visualFX.cDDMenu = 1 ;
            } ;
        }
        
    },
    
    hideDDMenus: function() {
        for(i = 0; i < visualFX.aDDMenu.length; i++ )
            visualFX.aDDMenu[i].style.display = 'none' ;
    },
    
    getTopPos: function ( inputObj ) {
    
      var returnValue = inputObj.offsetTop;
      while((inputObj = inputObj.offsetParent) != null){
        if(inputObj.tagName!='HTML')returnValue += inputObj.offsetTop;
      }
      return returnValue;
    },

    getLeftPos: function ( inputObj ) {
    
      var returnValue = inputObj.offsetLeft;
      while((inputObj = inputObj.offsetParent) != null){
        if(inputObj.tagName!='HTML')returnValue += inputObj.offsetLeft;
      }
      return returnValue;
    },
    
    /*** Tooltips ***/
    
    tooltipObj : new Array,
    tooltipIndex : 0,
    
    loadTooltip: function( eId ) {
        
        eTooltip = document.getElementById(eId) ;

        eTooltip.onmouseover = function () { 
            msg = '<p>' + document.getElementById(this.id + '_t').innerHTML + '</p>' ;
            visualFX.tooltip( msg, this.id ) ;  
        } ;
        
        eTooltip.onmouseout = function() { visualFX.hideAllTooltips() } ;
        
    },  

    tooltip: function( msg, objId ) {

        inputObj = document.getElementById(objId) ;
        
        tooltipIndex = visualFX.tooltipIndex ;
        tooltipObj = visualFX.tooltipObj ;
            
        if(!tooltipObj[tooltipIndex])   
        {
            tooltipObj[tooltipIndex] = document.createElement('DIV');
            tooltipObj[tooltipIndex].style.position = 'absolute';
            tooltipObj[tooltipIndex].id = 'tooltipObj';     
            document.body.appendChild(tooltipObj[tooltipIndex]);
        
            var contentDiv = document.createElement('DIV'); 
            contentDiv.className = 'tooltip_content';
            tooltipObj[tooltipIndex].appendChild(contentDiv);
            contentDiv.id = 'tooltip_content_' + tooltipIndex;

            contentDiv.innerHTML = msg ;
            
        }
            
        tooltipObj[tooltipIndex].onclick = function() { visualFX.hideAllTooltips() } ;
        
        tooltipObj[tooltipIndex].style.display='block';
        visualFX.posTooltip(inputObj, tooltipIndex);
        visualFX.tooltipIndex++ ;
    },
    
    hideAllTooltips: function() {
    
    for( i = 0 ; i < visualFX.tooltipIndex ; i++ )
                tooltipObj[i].style.display='none';
    
    },

    posTooltip: function posTooltip( inputObj, tooltipIndex ) {
        
        var leftPos = (visualFX.getLeftPos(inputObj) + inputObj.offsetWidth) + 1 ;
        var topPos = visualFX.getTopPos(inputObj) + (inputObj.offsetHeight/6) ;
        var tooltipWidth = document.getElementById('tooltip_content_' + tooltipIndex).offsetWidth ; 

        if( leftPos > 1200 ) {
            leftPos = leftPos - 354 - inputObj.offsetWidth  ;
            tooltipObj[tooltipIndex].className = 'derecha' ;
        }
                    
        tooltipObj[tooltipIndex].style.left = leftPos + 'px';
        tooltipObj[tooltipIndex].style.top = topPos + 'px'; 
    },
    
    // Validar formularios

    validateForm: function validateForm( frmFields ) {
        aFrmFields = frmFields.split(',') ;
        control = 1 ;
        for ( i = 0 ; i < aFrmFields.length ; i++ ) {
            field = document.getElementById(aFrmFields[i]) ;
            validateMsg = document.getElementById(field.id + '_frmv') ;
            field.onfocus = function() {
                validateMsg = document.getElementById(this.id + '_frmv') ;
                validateMsg.style.display = 'none' ;                
            }
            validateMsg.onmouseover = function() {
                this.style.display = 'none' ;
            }
            if ( field.value == '' ) {
                validateMsg.style.display = 'block' ;
                validateMsg.setAttribute('class',validateMsg.className.replace('validatemsg hidden','validatemsg')) ;           
                control = 0 ;
            } else {
                validateMsg.setAttribute('class',validateMsg.className.replace('validatemsg','validatemsg hidden')) ;           
            }
        }
        if ( control )
            return true ;
        else
            return false ;
    },
    
    // General  
        
    eShow: function( eId ) {
        document.getElementById( eId ).style.display = 'block' ;
    },
    
    eHide: function( eId ) {
        document.getElementById( eId ).style.display = 'none' ;
    },

    loadTabsX: function( eId ) {
        var e = document.getElementById(eId) ;
        var aTabs = e.getElementsByTagName('a') ;
        visualFX.currentAction = e.className.replace('pub-actions','') ;
        for( var i = 0 ; i < aTabs.length ; i++ ) {
            aTabs[i].onclick = function() {
                visualFX.hideAllTabsX( aTabs ) ;
                $(this).parent().addClass('selected') ;
                var form = document.getElementById( this.className.replace('lnk-','t_') ) ;
                $( form ).removeClass('hidden') ;
                $(this).parent().parent().removeClass( visualFX.currentAction ) ;
                $(this).parent().parent().addClass( this.className.replace('lnk-','pub-' ) ) ;
                visualFX.currentAction = this.className.replace('lnk-','pub-' ) ;
                document.getElementById('msg_type').value = this.className.replace('lnk-', '') ;
            }
        }
    },
    
    hideAllTabsX: function ( aTabs ) {
        for( var i = 0 ; i < aTabs.length ; i++ ) {
            var form = document.getElementById( aTabs[i].className.replace('lnk-','t_') ) ;
            $( aTabs[i] ).parent().removeClass('selected') ;
            $( form ).addClass('hidden') ;
        }
    }

}
    
/*** Lightbox ***/

function htmlLightbox(url){
    MOOdalBox.open(url, "", "540 340");
    document.getElementById("mb_contents").style.removeAttribute("filter");
}
    

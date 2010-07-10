# -*- coding: utf-8 -*-

# Widget para mostrar una columna estándar en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 25, 2010

import gtk
import logging

from turpial.ui import util as util
from turpial.ui.gtk.errorbox import ErrorBox
from turpial.ui.gtk.statuslist import StatusList
from turpial.ui.gtk.waiting import CairoWaiting

log = logging.getLogger('Gtk:Column')

class GenericColumn(gtk.VBox):
    def __init__(self, mainwin, label='', menu='normal', marknew=False):
        gtk.VBox.__init__(self, False)
        
        self.last = None    # Last tweets updated
        self.mainwin = mainwin
        
        self.tweetlist = StatusList(mainwin, menu, marknew)
        
        self.waiting = CairoWaiting(mainwin)
        self.walign = gtk.Alignment(xalign=1, yalign=0.5)
        self.walign.add(self.waiting)
        
        self.errorbox = ErrorBox()
        
        self.label = gtk.Label(label)
        self.caption = label
        
        self.connect('expose-event', self.error_show)
        
    def error_show(self, widget, event):
        self.errorbox.show()
        
    def update_tweets(self, response):
        count = 0
        if response.type == 'error':
            self.stop_update(True, response.errmsg)
        else:
            arr_tweets = response.items
            if len(arr_tweets) == 0:
                self.tweetlist.clear()
                self.stop_update(True, _('No tweets available'))
            else:
                count = util.count_new_tweets(arr_tweets, self.last)
                self.stop_update()
                
                if self.tweetlist.autoscroll:
                    self.tweetlist.clear()
                    for tweet in arr_tweets:
                        self.tweetlist.add_tweet(tweet, False)
                else:
                    for tweet in arr_tweets:
                        if self.last is None:
                            self.tweetlist.add_tweet(tweet, False)
                        elif not util.has_tweet(self.last, tweet):
                            self.tweetlist.add_tweet(tweet)
                            self.tweetlist.del_last()
                
                self.last = arr_tweets
            
        self.on_update()
        return count
            
    def update_user_pic(self, user, pic):
        self.tweetlist.update_user_pic(user, pic)
        
    def update_wrap(self, width):
        self.tweetlist.update_wrap(width)
    
    def start_update(self):
        self.waiting.start()
        self.errorbox.hide()
        
    def stop_update(self, error=False, msg=''):
        self.waiting.stop(error)
        self.errorbox.show_error(msg, error)
    
    def clear(self):
        self.tweetlist.clear()
    
    def on_update(self, data=None):
        pass
        
class StandardColumn(GenericColumn):
    def __init__(self, mainwin, label='', menu='normal', id=None, marknew=False):
        GenericColumn.__init__(self, mainwin, label, menu, marknew)
        
        self.id = id
        self.listcombo = gtk.combo_box_new_text()
        self.listcombo.append_text('Lista de prueba 1')
        self.listcombo.append_text('Lista de prueba 2')
        
        self.refresh = gtk.Button()
        self.refresh.set_image(self.mainwin.load_image('refresh.png'))
        self.refresh.set_tooltip_text(_('Manual Update'))
        #self.refresh.set_relief(gtk.RELIEF_NONE)
        
        self.autoscroll = gtk.ToggleButton()
        self.autoscroll.set_image(self.mainwin.load_image('autoscroll.png'))
        self.autoscroll.set_tooltip_text(_('Automatic Scroll'))
        self.autoscroll.set_active(True)
        self.tweetlist.set_autoscroll(True)
        
        listsbox = gtk.HBox(False)
        listsbox.pack_start(self.autoscroll, False, False)
        listsbox.pack_start(self.listcombo, True, True)
        listsbox.pack_start(self.refresh, False, False)
        listsbox.pack_start(self.walign, False, False, 2)
        
        self.pack_start(listsbox, False, False)
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.tweetlist, True, True)
        
        self.refresh.connect('clicked', self.__manual_update)
        self.autoscroll.connect('toggled', self.__toggle_autoscroll)
        
    def __manual_update(self, widget):
        self.mainwin.manual_update(self.id)
        
    def __toggle_autoscroll(self, widget):
        value = self.autoscroll.get_active()
        self.tweetlist.set_autoscroll(value)
        
    def start_update(self):
        self.waiting.start()
        self.errorbox.hide()
        self.refresh.set_sensitive(False)
        self.listcombo.set_sensitive(False)
        
    def stop_update(self, error=False, msg=''):
        self.waiting.stop(error)
        self.errorbox.show_error(msg, error)
        self.refresh.set_sensitive(True)
        self.listcombo.set_sensitive(True)
        
    def clear_bg_color(self):
        self.tweetlist.unset_bg_color()
        
class SingleColumn(GenericColumn):
    def __init__(self, mainwin, label='', menu='normal'):
        GenericColumn.__init__(self, mainwin, label, menu)
        
        #self.errorbox = gtk.HBox(False)
        #self.errorbox.pack_start(self.lblerror, False, False, 2)
        #self.errorbox.pack_start(self.walign, False, False, 2)
        
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.tweetlist, True, True)
        
class SearchColumn(GenericColumn):
    def __init__(self, mainwin, label=''):
        GenericColumn.__init__(self, mainwin, label)
        
        self.input_topics = gtk.Entry()
        self.clearbtn = gtk.Button()
        self.clearbtn.set_image(self.mainwin.load_image('clear.png'))
        self.clearbtn.set_tooltip_text(_('Clear results'))
        #self.clearbtn.set_relief(gtk.RELIEF_NONE)
        try:
            #self.input_topics.set_property("primary-icon-stock", 
            #                               gtk.STOCK_FIND)
            self.input_topics.set_property("secondary-icon-stock",
                                           gtk.STOCK_FIND)
            self.input_topics.connect("icon-press", self.__on_icon_press)
        except: 
            pass
        
        inputbox = gtk.HBox(False)
        inputbox.pack_start(self.input_topics, True, True)
        inputbox.pack_start(self.clearbtn, False, False)
        inputbox.pack_start(self.walign, False, False, 2)
        
        self.pack_start(inputbox, False, False)
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.tweetlist, True, True)
        
        self.clearbtn.connect('clicked', self.__clear)
        self.input_topics.connect('activate', self.__search_topic)
        self.input_topics.grab_focus()
        
    def __on_icon_press(self, widget, pos, e):
        #if pos == 0: 
        #    self.__search_topic(widget)
        if pos == 1:
            #widget.set_text('')
            self.__search_topic(widget)
            
    def __clear(self, widget):
        self.tweetlist.clear()
        self.input_topics.grab_focus()
        
    def __search_topic(self, widget):
        topic = widget.get_text()
        if topic != '':
            self.lock()
            self.mainwin.request_search(topic)
            widget.set_text('')
        else:
            widget.set_text(_('You must write something to search'))
            widget.grab_focus()
        
    def on_update(self, data=None):
        self.unlock()
        
    def lock(self):
        self.input_topics.set_sensitive(False)
        self.clearbtn.set_sensitive(False)
        
    def unlock(self):
        self.input_topics.set_sensitive(True)
        self.clearbtn.set_sensitive(True)


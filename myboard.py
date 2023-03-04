#ref: https://github.com/byunei/system_hotkey/blob/master/system_hotkey/system_hotkey.py
#$ sudo apt install python3-xlib
#python-xlib is already the newest version (0.23-2).
#$ sudo apt install gir1.2-webkit2-4.0
#gir1.2-webkit2-4.0 is already the newest version (2.28.3-2).
#$ sudo pip install pywebview typelib python3-gi python3-gi-cairo
#after upgrade python3.11:
#$ sudo pip install --upgrade bottle   #or else report error: "ImportError: cannot import name 'getargspec' from 'inspect'"
#$ sudo pip install pygobject   #replace python3-gi
#Requirement already satisfied: pywebview in /usr/local/lib/python2.7/dist-packages (3.2)
#python3 myboard.py

from Xlib.display import Display
from Xlib import X, XK
from Xlib.protocol.event import KeyPress, KeyRelease, ButtonPress, ButtonRelease, ClientMessage
from Xlib.ext.xtest import fake_input
import time
import os
import socket
from collections import namedtuple
import json
import webview
import threading
#import thread      #python2

#from gi.repository import GdkX11
#from pprint import pprint

disp=Display()
screen=disp.screen()
root=screen.root
MOUSE_STEP=round(screen.width_in_pixels/20)
MOUSE_STEP_SLOW=round(screen.width_in_pixels/100)
is_on=0
is_ready_switchall=0
key_delay_shift=''
_NET_WM_STATE_REMOVE=0
_NET_WM_STATE_ADD=1
_NET_WM_STATE_TOGGLE=2

#X.Mod1Mask alt  X.ShiftMask   X.AnyModifier X.ControlMask
#q, F1, Left
keys=[{'key':'Control_L', 'mod':X.ControlMask},
      {'key':'Control_R', 'mod':X.ControlMask},

      {'key':'l', 'mod':X.NONE},
      {'key':'j', 'mod':X.NONE},
      {'key':'i', 'mod':X.NONE},
      {'key':'k', 'mod':X.NONE},
      {'key':'l', 'mod':X.ShiftMask},
      {'key':'j', 'mod':X.ShiftMask},
      {'key':'i', 'mod':X.ShiftMask},
      {'key':'k', 'mod':X.ShiftMask},
      {'key':'l', 'mod':X.ControlMask},
      {'key':'j', 'mod':X.ControlMask},
      {'key':'i', 'mod':X.ControlMask},
      {'key':'k', 'mod':X.ControlMask},

      {'key':'s', 'mod':X.NONE},
      {'key':'d', 'mod':X.NONE},
      {'key':'f', 'mod':X.NONE},
      {'key':'e', 'mod':X.NONE},

      {'key':' ', 'mod':X.NONE},
      {'key':'`', 'mod':X.NONE},
      {'key':',', 'mod':X.NONE},
      {'key':'r', 'mod':X.NONE},
      {'key':'u', 'mod':X.NONE},
      {'key':'b', 'mod':X.NONE},
      {'key':'n', 'mod':X.NONE},
      {'key':'t', 'mod':X.NONE},
      {'key':'y', 'mod':X.NONE},

      {'key':'p', 'mod':X.NONE},
      {'key':'q', 'mod':X.NONE},
      {'key':'z', 'mod':X.NONE},
      {'key':'a', 'mod':X.NONE},
      {'key':';', 'mod':X.NONE},
      {'key':'g', 'mod':X.NONE},
      {'key':'h', 'mod':X.NONE},
      {'key':'x', 'mod':X.NONE},
      {'key':'c', 'mod':X.NONE},
      {'key':'v', 'mod':X.NONE},
      {'key':'o', 'mod':X.NONE},
      {'key':'m', 'mod':X.NONE},
      {'key':'w', 'mod':X.NONE},
      {'key':'/', 'mod':X.NONE},
      {'key':'.', 'mod':X.NONE},
      {'key':'g', 'mod':X.ControlMask},
      {'key':'g', 'mod':X.ShiftMask},
      {'key':'h', 'mod':X.ControlMask},
      {'key':'h', 'mod':X.ShiftMask}
     ]
keys_mapped=[{'key':'SwitchAll', 'mod':X.NONE, 'act':0},
             {'key':'SwitchAll', 'mod':X.NONE, 'act':0},

             {'key':'MoveRight', 'mod':X.NONE, 'act':MOUSE_STEP},
             {'key':'MoveLeft', 'mod':X.NONE, 'act':MOUSE_STEP},
             {'key':'MoveUp', 'mod':X.NONE, 'act':MOUSE_STEP},
             {'key':'MoveDown', 'mod':X.NONE, 'act':MOUSE_STEP},
             {'key':'MoveRight', 'mod':X.NONE, 'act':1},
             {'key':'MoveLeft', 'mod':X.NONE, 'act':1},
             {'key':'MoveUp', 'mod':X.NONE, 'act':1},
             {'key':'MoveDown', 'mod':X.NONE, 'act':1},
             {'key':'MoveRight', 'mod':X.NONE, 'act':MOUSE_STEP_SLOW},
             {'key':'MoveLeft', 'mod':X.NONE, 'act':MOUSE_STEP_SLOW},
             {'key':'MoveUp', 'mod':X.NONE, 'act':MOUSE_STEP_SLOW},
             {'key':'MoveDown', 'mod':X.NONE, 'act':MOUSE_STEP_SLOW},

             {'key':'Left', 'mod':X.NONE, 'act':2},
             {'key':'Down', 'mod':X.NONE, 'act':2},
             {'key':'Right', 'mod':X.NONE, 'act':2},
             {'key':'Up', 'mod':X.NONE, 'act':2},

             {'key':X.Button1, 'mod':X.NONE, 'act':2},
             {'key':X.Button2, 'mod':X.NONE, 'act':2},
             {'key':X.Button3, 'mod':X.NONE, 'act':2},
             {'key':X.Button1, 'mod':X.NONE, 'act':0},
             {'key':X.Button1, 'mod':X.NONE, 'act':1},
             {'key':X.Button3, 'mod':X.NONE, 'act':0},
             {'key':X.Button3, 'mod':X.NONE, 'act':1},
             {'key':X.Button4, 'mod':X.NONE, 'act':1},
             {'key':X.Button5, 'mod':X.NONE, 'act':1},

             {'key':'Return', 'mod':X.NONE, 'act':2},
             {'key':'Escape', 'mod':X.NONE, 'act':2},
             {'key':'Delete', 'mod':X.ShiftMask, 'act':2},
             {'key':'Delete', 'mod':X.NONE, 'act':2},
             {'key':'BackSpace', 'mod':X.NONE, 'act':2},
             {'key':'Home', 'mod':X.NONE, 'act':2},
             {'key':'End', 'mod':X.NONE, 'act':2},
             {'key':'x', 'mod':X.ControlMask, 'act':2},
             {'key':'c', 'mod':X.ControlMask, 'act':2},
             {'key':'v', 'mod':X.ControlMask, 'act':2},
             {'key':'n', 'mod':X.ControlMask, 'act':2},
             {'key':'d', 'mod':X.ControlMask|X.Mod1Mask, 'act':2},
             {'key':'F4', 'mod':X.Mod1Mask, 'act':2},
             {'key':'z', 'mod':X.ControlMask, 'act':2},
             {'key':'a', 'mod':X.ControlMask, 'act':2},
             {'key':'Home', 'mod':X.ControlMask, 'act':2},
             {'key':'Home', 'mod':X.ShiftMask, 'act':2},
             {'key':'End', 'mod':X.ControlMask, 'act':2},
             {'key':'End', 'mod':X.ShiftMask, 'act':2}
            ]
pinyin_keys=[#1-9,0
             {'key':'1', 'mod':X.NONE},
             {'key':'2', 'mod':X.NONE},
             {'key':'3', 'mod':X.NONE},
             {'key':'4', 'mod':X.NONE},
             {'key':'5', 'mod':X.NONE},
             {'key':'6', 'mod':X.NONE},
             {'key':'7', 'mod':X.NONE},
             {'key':'8', 'mod':X.NONE},
             {'key':'9', 'mod':X.NONE},
             {'key':'0', 'mod':X.NONE},
             #a..z
             {'key':'a', 'mod':X.NONE},
             {'key':'b', 'mod':X.NONE},
             {'key':'c', 'mod':X.NONE},
             {'key':'d', 'mod':X.NONE},
             {'key':'e', 'mod':X.NONE},
             {'key':'f', 'mod':X.NONE},
             {'key':'g', 'mod':X.NONE},
             {'key':'h', 'mod':X.NONE},
             {'key':'i', 'mod':X.NONE},
             {'key':'j', 'mod':X.NONE},
             {'key':'k', 'mod':X.NONE},
             {'key':'l', 'mod':X.NONE},
             {'key':'m', 'mod':X.NONE},
             {'key':'n', 'mod':X.NONE},
             {'key':'o', 'mod':X.NONE},
             {'key':'p', 'mod':X.NONE},
             {'key':'q', 'mod':X.NONE},
             {'key':'r', 'mod':X.NONE},
             {'key':'s', 'mod':X.NONE},
             {'key':'t', 'mod':X.NONE},
             {'key':'u', 'mod':X.NONE},
             {'key':'v', 'mod':X.NONE},
             {'key':'w', 'mod':X.NONE},
             {'key':'x', 'mod':X.NONE},
             {'key':'y', 'mod':X.NONE},
             {'key':'z', 'mod':X.NONE},
             #Backspace
             {'key':'\b', 'mod':X.NONE},
             #!,@,#,$,%,^,&,*,(,), and 11 double-sign keys:=-[]\/,.;'`
             {'key':'1', 'mod':X.ShiftMask},
             {'key':'2', 'mod':X.ShiftMask},
             {'key':'3', 'mod':X.ShiftMask},
             {'key':'4', 'mod':X.ShiftMask},
             {'key':'5', 'mod':X.ShiftMask},
             {'key':'6', 'mod':X.ShiftMask},
             {'key':'7', 'mod':X.ShiftMask},
             {'key':'8', 'mod':X.ShiftMask},
             {'key':'9', 'mod':X.ShiftMask},
             {'key':'0', 'mod':X.ShiftMask},
             {'key':'=', 'mod':X.NONE},
             {'key':'-', 'mod':X.NONE},
             {'key':'[', 'mod':X.NONE},
             {'key':']', 'mod':X.NONE},
             {'key':'\\', 'mod':X.NONE},
             {'key':'/', 'mod':X.NONE},
             {'key':',', 'mod':X.NONE},
             {'key':'.', 'mod':X.NONE},
             {'key':';', 'mod':X.NONE},
             {'key':'\'', 'mod':X.NONE},
             {'key':'`', 'mod':X.NONE},
             {'key':'=', 'mod':X.ShiftMask},
             {'key':'-', 'mod':X.ShiftMask},
             {'key':'[', 'mod':X.ShiftMask},
             {'key':']', 'mod':X.ShiftMask},
             {'key':'\\', 'mod':X.ShiftMask},
             {'key':'/', 'mod':X.ShiftMask},
             {'key':',', 'mod':X.ShiftMask},
             {'key':'.', 'mod':X.ShiftMask},
             {'key':';', 'mod':X.ShiftMask},
             {'key':'\'', 'mod':X.ShiftMask},
             {'key':'`', 'mod':X.ShiftMask},
             #SPACE,TAB,RETURN,ESCAPE,APPS,END,HOME,UP,DOWN,LEFT,RIGHT,LWIN,RWIN,DELETE,MOD_ALT, MOD_CONTROL
             {'key':' ', 'mod':X.NONE},
             {'key':'\t', 'mod':X.NONE},
             {'key':'\n', 'mod':X.NONE},
             {'key':'\e', 'mod':X.NONE},
             {'key':'Menu', 'mod':X.NONE},
             {'key':'End', 'mod':X.NONE},
             {'key':'Home', 'mod':X.NONE},
             {'key':'Up', 'mod':X.NONE},
             {'key':'Down', 'mod':X.NONE},
             {'key':'Left', 'mod':X.NONE},
             {'key':'Right', 'mod':X.NONE},
             {'key':'Super_L', 'mod':X.NONE},
             {'key':'Super_R', 'mod':X.NONE},
             {'key':'Delete', 'mod':X.NONE}
            ]

def string_to_keycode(key):
    #'\r':'Return' for Shift+Return will trigger "\r" and enter string_to_keycode() refer: https://github.com/SavinaRoja/PyKeyboard/blob/master/pykeyboard/x11.py
    keys_special={' ':'space','\t':'Tab','\r':'Return','\n':'Return','\b':'BackSpace','\e':'Escape',
                  '!':'exclam','#':'numbersign','%':'percent','$':'dollar','&':'ampersand','"':'quotedbl',
                  '\'':'apostrophe','(':'parenleft',')':'parenright','*':'asterisk','=':'equal','+':'plus',
                  ',':'comma','-':'minus','.':'period','/':'slash',':':'colon',';':'semicolon','<':'less',
                  '>':'greater','?':'question','@':'at','[':'bracketleft',']':'bracketright','\\':'backslash',
                  '^':'asciicircum','_':'underscore','`':'grave','{':'braceleft','|':'bar','}':'braceright',
                  '~':'asciitilde'
                 }
    key_sym=XK.string_to_keysym(key)
    if key_sym==0:
       key_sym=XK.string_to_keysym(keys_special[key])
    return disp.keysym_to_keycode(key_sym)

def keycode_to_string(key_code):
    syms_mod=[65505,65506,65513,65514,65507,65508,
              65361,65362,65363,65364,65360,65367,65365,65366,
              65379,65535,65491,
              65470,65471,65472,65473,65474,65475,65476,65477,65478,65479,65480,65481
             ]
    names_mod=['Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Control_L', 'Control_R',
               'Left', 'Up', 'Right', 'Down', 'Home', 'End', 'Page_Up', 'Page_Down',
               'Insert', 'Delete', 'Print',
               'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'
               '\r'
              ]
    #2nd: 0 is unshifted, 1 is shifted, 2 is alt grid, and 3 is shiftalt grid
    key_sym=disp.keycode_to_keysym(key_code, 0)
    if key_sym in syms_mod:
       return names_mod[syms_mod.index(key_sym)]
    return XK.keysym_to_string(key_sym)

def send_event(key, mod, act):
    print('send key,mod,act:'+str(key)+','+str(mod)+','+str(act))
    if key in ['MoveLeft', 'MoveRight', 'MoveUp', 'MoveDown']:
       if key=='MoveLeft':
          disp.warp_pointer(-act, 0)
       if key=='MoveRight':
          disp.warp_pointer(act, 0)
       if key=='MoveUp':
          disp.warp_pointer(0, -act)
       if key=='MoveDown':
          disp.warp_pointer(0, act)
       return

    if key in [X.Button1,X.Button2,X.Button3,X.Button4,X.Button5]:
       wind=root
       window=root.query_pointer().child
       #wind=root.query_pointer().child
       #window=root.query_pointer().child.query_pointer().child #in some linux, it is root.query_pointer().child
       key_action=[X.ButtonPress,X.ButtonRelease][act]
       if act:
          KeyAction=ButtonRelease
       else:
            KeyAction=ButtonPress
            #try:
            #    window.configure(stack_mode=X.Above)  #set foreground window
            #except:
            #       window=wind
            #       window.configure(stack_mode=X.Above)
            #window.set_input_focus(X.RevertToParent, X.CurrentTime)
            #disp.sync()
    else:
         wind=disp.get_input_focus().focus
         windows=wind.query_pointer().child
         key=string_to_keycode(key)
         key_action=[X.KeyPress,X.KeyRelease][act]
         if act:
            KeyAction=KeyRelease
         else:
              KeyAction=KeyPress
    try:
        window.query_pointer()
    except:
           window=wind
    x=window.query_pointer().win_x
    y=window.query_pointer().win_y
    evt_key=KeyAction(detail=key, state=mod,
                      root=root, window=window, child=X.NONE,
                      root_x=0, root_y=0, event_x=x, event_y=y,
                      same_screen=1, time=X.CurrentTime
                     )
    if key_action in [X.ButtonPress, X.ButtonRelease]:
        fake_input(disp, key_action, key) #only use fake_input in mouse button, for it won't send modifiers
    else:
         #disp.send_event(X.PointerWindow, evt_key)   #if keyboard event, to use X.InputFocus
         window.send_event(evt_key)
    #if key in [X.Button1] and wind!=window:
    #    wind.send_event(evt_key)

def grab_key(key, mod):
    key_code=string_to_keycode(key)
    #3rd: bool owner_events, 4th: pointer_mode, 5th: keyboard_mode, X.GrabModeSync, X.GrabModeAsync
    root.grab_key(key_code, mod, 0, X.GrabModeAsync, X.GrabModeAsync)
    root.grab_key(key_code, mod|X.LockMask, 0, X.GrabModeAsync, X.GrabModeAsync) #caps lock
    root.grab_key(key_code, mod|X.Mod2Mask, 0, X.GrabModeAsync, X.GrabModeAsync) #num lock
    root.grab_key(key_code, mod|X.LockMask|X.Mod2Mask, 0, X.GrabModeAsync, X.GrabModeAsync)

def ungrab_key(key, mod):
    key_code=string_to_keycode(key)
    root.ungrab_key(key_code, mod)
    root.ungrab_key(key_code, mod|X.LockMask)
    root.ungrab_key(key_code, mod|X.Mod2Mask)
    root.ungrab_key(key_code, mod|X.LockMask|X.Mod2Mask)

def handle_event(evt):
    global is_ready_switchall,key_delay_shift,is_on
    key_name=keycode_to_string(evt.detail)
    mod=evt.state & ~(X.LockMask | X.Mod2Mask | 256 | 1024 | 2048) #strip caps lock and num lock, and left mouse pressed
    print('receive keycode,keyname,type,state:'+str(evt.detail)+','+key_name+','+str(evt.type)+','+str(mod)+','+('is_on' if is_on else'is_off'))
    key={'key':key_name, 'mod':mod}
    if (is_on and key in keys) or ((key_name=='Control_L' or key_name=='Control_R') and mod==4):
        key_mapped=keys_mapped[keys.index(key)]
    else:
       print('==================key_name:'+key_name+','+str(mod))
       if evt.type==X.KeyRelease: #only can send key after previous key released
          is_ready_switchall=0
          key_delay_shift=key_name  #because Control_* key still pressed
       key_mapped=key

    if evt.type==X.KeyPress:
       if key_mapped['key']=='SwitchAll':
          is_ready_switchall=1
       else:
          is_ready_switchall=0
          if is_on:
             if key_mapped['key'] in ['MoveLeft', 'MoveRight', 'MoveUp', 'MoveDown']:
                send_event(key_mapped['key'], key_mapped['mod'], key_mapped['act'])
             if key_mapped['key'] in [X.Button1,X.Button2,X.Button3,X.Button4,X.Button5]:
                if key_mapped['act']==2:
                   send_event(key_mapped['key'], key_mapped['mod'], 0)
                   send_event(key_mapped['key'], key_mapped['mod'], 1)
                else:
                    send_event(key_mapped['key'], key_mapped['mod'], key_mapped['act'])
    elif evt.type==X.KeyRelease:
         if key_mapped['key']=='SwitchAll':
            if is_ready_switchall==1:
               switch_all()
            elif key_delay_shift:
                 send_event(key_delay_shift, X.ShiftMask, 0)
                 send_event(key_delay_shift, X.ShiftMask, 1)
                 key_delay_shift=''
            return

         if not key_mapped['key'] in ['MoveLeft', 'MoveRight', 'MoveUp', 'MoveDown',
                                      X.Button1,X.Button2,X.Button3,X.Button4,X.Button5
                                     ]:
            send_event(key_mapped['key'], key_mapped['mod'], 0)
            send_event(key_mapped['key'], key_mapped['mod'], 1)

def switch_all():
    global is_on,is_ready_switchall
    for key in keys:
        #print 'key:'+key['key']
        if key['key']!='Control_L' and key['key']!='Control_R':
           if not is_on:
              grab_key(key['key'], key['mod'])
           else:
                ungrab_key(key['key'], key['mod'])
    if is_on:
       is_on=0
       window.load_html('<body style="background-color:white; margin:0px;">off</body>')
    else:
         os.system('xset r rate 200 30')
         is_on=1
         window.load_html('<body style="background-color:green; margin:0px;">on</body>')
    is_ready_switchall=0

from Xlib.ext import record
from Xlib.protocol import rq
def process_replay(replay):
    data=replay.data
    while len(data):
          try:
              evt, data=rq.EventField(None).parse_binary_value(data, disp.display, None, None)
              key_name=keycode_to_string(evt.detail)
          except:
                 continue
          if evt.type==X.KeyPress:# and (key_name=='Shift_L' or key_name=='Shift_R'):
             print('replay:',evt.detail,evt.state)
             #switch_all()

def listen_shift():
    ctx=disp.record_create_context(0,
                                   [record.AllClients],
                                   [{'core_requests': (0, 0),'core_replies': (0, 0),
                                     'ext_requests': (0, 0, 0, 0),'ext_replies': (0, 0, 0, 0),
                                     'delivered_events': (0,0),'device_events': (X.KeyPress,X.ButtonPress),
                                     'errors': (0,0),'client_started': False,'client_died': False
                                   }]
                                  )
    disp.record_enable_context(ctx, process_replay)
    disp.record_free_context(ctx)

def get_window(title=str):
    window_ids=root.get_full_property(disp.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType).value
    for window_id in window_ids:
        wind=disp.create_resource_object('window', window_id)
        #pid=wind.get_full_property(disp.intern_atom('_NET_WM_PID'), X.AnyPropertyType)
        #print wind.get_wm_name()
        if wind.get_wm_name()==title:
            return wind

def dockize(wind):
    #disable minimize:
    #got the data format from 'xtrace xprop -id 0x02e00007 -f _NET_WM_WINDOW_TYPE 32a -set _NET_WM_WINDOW_TYPE _NET_WM_WINDOW_TYPE_DOCK'
    #set window type _NET_WM_WINDOW_TYPE_DOCK first, then change _NET_WM_STRUT
    wind.change_property(disp.intern_atom('_NET_WM_WINDOW_TYPE'),
                         disp.intern_atom('ATOM'),
                         32,
                         [disp.intern_atom('_NET_WM_WINDOW_TYPE_DOCK')]
                        )

    #occupy screen space:
    wind.change_property(disp.intern_atom('_NET_WM_STRUT'),
                         disp.intern_atom('CARDINAL'),
                         32,
                         [440, 0, 0, 50]
                        )
    wind.change_property(disp.intern_atom('_NET_WM_STRUT_PARTIAL'),
                         disp.intern_atom('CARDINAL'),
                         32,
                         [440, 0, 0, 50,  0,1080,  0,1080,  0,1920,  0,1920]
                        )

    #set position(now be replaced with webview.create_window() parameter x,y):
    #wind.configure(x=0, y=1012)
    '''root.send_event(event=ClientMessage(window=wind,
                                  client_type=disp.intern_atom('_NET_MOVERESIZE_WINDOW'),
                                  data=(32, ([1<<8|1<<9, 0, screen.height_in_pixels-48, 0, 0]))
                                 ),
                    event_mask=X.SubstructureRedirectMask
                   )
    '''

    #make xfce4-panel above myboard:
    #got the data format from 'xtrace wmctrl -r "jack" -b add,above,skip_taskbar'
    panel_wind=get_window('xfce4-panel')
    root.send_event(event=ClientMessage(window=panel_wind,
                                  client_type=disp.intern_atom('_NET_WM_STATE'),
                                  data=(32, ([_NET_WM_STATE_ADD, disp.intern_atom('_NET_WM_STATE_ABOVE'), disp.intern_atom('_NET_WM_STATE_SKIP_TASKBAR'), 0, 0]))
                                 ),
                    event_mask=(X.SubstructureRedirectMask)
                   )
    #all_states=wind.get_full_property(disp.intern_atom('_NET_WM_STATE'), X.AnyPropertyType)
    #pprint(all_states)

    #remove title bar(now be replaced with webview.create_window() parameter frameless=True):
    #maybe conflict and show: [xcb] Most likely this is a multi-threaded client and XInitThreads has not been called
    #GdkX11.X11Window.foreign_new_for_display(GdkX11.X11Display.get_default(), wind.id).set_decorations(0)

    disp.sync()
    disp.flush()

def sub():
    global is_on

    #listen_shift()
    #print 'hello'+str(string_to_keycode('Shift_L'))
    grab_key('Control_L', X.ControlMask)
    grab_key('Control_R', X.ControlMask)
    send_event(X.Button1, X.NONE, 1)
    send_event(X.Button2, X.NONE, 1)
    send_event(X.Button3, X.NONE, 1) #maybe you pressed right mouse button, but myboard.py killed, then mouse and keyboard blocked
    send_event(X.Button4, X.NONE, 1)
    send_event(X.Button5, X.NONE, 1)

    time.sleep(1)

    wind=get_window('myboard_jack')
    dockize(wind)
    window.load_html('<body style="background-color:white;margin:0px;">off</body>')

    sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 21405))
    sock.settimeout(0.001);
    while 1:
          if root.display.pending_events()>0:
              evt=root.display.next_event()
              if evt.type in [X.KeyPress, X.KeyRelease]: #ignore X.MappingNotify(=34)
                 handle_event(evt)
              #else handle_event_pinyin(evt)

          data=''
          try:
              data, address=sock.recvfrom(4096)
              if data!='':
                  print('receive udp:',data)
                  #{"detail":"j", "state":0, "type":2}
                  #{"detail":"j", "state":0, "type":3}
                  evt_key=json.loads(data);
                  if is_on:
                      if evt_key['detail']=='f':
                          evt_key['detail']='s'
                      elif evt_key['detail']=='s':
                          evt_key['detail']='f'
                  evt_key={'detail':string_to_keycode(evt_key['detail']), 'state':evt_key['state'], 'type':evt_key['type']}
                  if evt_key['type']==5:
                      fake_input(disp, 2, evt_key['detail'])
                      fake_input(disp, 3, evt_key['detail'])
                  else:
                      fake_input(disp, evt_key['type'], evt_key['detail'])
                  #handle_event(namedtuple('Struct', evt_key.keys())(*evt_key.values()))
          except socket.error:
              continue

if __name__ == '__main__':
    #thread.start_new_thread(sub, ())     #python2
    threading.Thread(target=sub).start()

    #def create_window(title, url=None, html=None, js_api=None, width=800, height=600, x=None, y=None, resizable=True, fullscreen=False, min_size=(200, 100), hidden=False, frameless=False, minimized=False):
    #default min_size is (200,100) but minimal min_size is (60, 46), the system task bar is 32
    window=webview.create_window('myboard_jack', None, '<html><body><h1>pywebview wow!</h1><body></html>', None, screen.width_in_pixels-20, 49, 10, screen.height_in_pixels, False, False, (50, 10), False, True, False)
    webview.start()

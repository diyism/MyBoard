from Xlib.display import Display
from Xlib import X, XK
from Xlib.protocol.event import KeyPress, KeyRelease, ButtonPress, ButtonRelease
from Xlib.ext.xtest import fake_input
import time

disp=Display()
screen=disp.screen()
root=screen.root
MOUSE_STEP=screen.width_in_pixels/20
MOUSE_STEP_SLOW=screen.width_in_pixels/100
is_on=0
is_ready_switchall=0
key_delay_shift=''

#X.Mod1Mask alt  X.ShiftMask   X.AnyModifier X.ControlMask
#q, F1, Left
keys=[{'key':'Shift_L', 'mod':X.ShiftMask},
      {'key':'Shift_R', 'mod':X.ShiftMask},
      {'key':'Shift_L', 'mod':X.NONE},
      {'key':'Shift_R', 'mod':X.NONE},

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
             {'key':'SwitchAll', 'mod':X.NONE, 'act':0},
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
             {'key':'F4', 'mod':X.Mod1Mask, 'act':2},
             {'key':'z', 'mod':X.ControlMask, 'act':2},
             {'key':'a', 'mod':X.ControlMask, 'act':2},
             {'key':'Home', 'mod':X.ControlMask, 'act':2},
             {'key':'Home', 'mod':X.ShiftMask, 'act':2},
             {'key':'End', 'mod':X.ControlMask, 'act':2},
             {'key':'End', 'mod':X.ShiftMask, 'act':2}
            ]

def string_to_keycode(key):
    codes_mod=[50,62,64,108,37,105]
    names_mod=['Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Control_L', 'Control_R']
    if key in names_mod:
       return codes_mod[names_mod.index(key)]
    keys_special={' ':'space','\t':'Tab','\n':'Return','\r':'BackSpace','\e':'Escape',
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
    codes_mod=[50,62,64,108,37,105,113,111,114,116,110,115,112,117,118,119,107,
               67,68,69,70,71,72,73,74,75,76,95,96
              ]
    names_mod=['Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Control_L', 'Control_R',
               'Left', 'Up', 'Right', 'Down', 'Home', 'End', 'Page_Up', 'Page_Down',
               'Insert', 'Delete', 'Print',
               'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'
              ]
    if key_code in codes_mod:
       return names_mod[codes_mod.index(key_code)]
    #2nd: 0 is unshifted, 1 is shifted, 2 is alt grid, and 3 is shiftalt grid
    return XK.keysym_to_string(disp.keycode_to_keysym(key_code, 0))

def send_event(key, mod, act):
    print 'send key,mod,act:'+str(key)+','+str(mod)+','+str(act)
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
       wind=root.query_pointer().child
       window=root.query_pointer().child.query_pointer().child #in some linux, it is root.query_pointer().child
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
    global is_ready_switchall,key_delay_shift
    key_name=keycode_to_string(evt.detail)
    mod=evt.state & ~(X.LockMask | X.Mod2Mask | 256 | 1024 | 2048) #strip caps lock and num lock, and left mouse pressed
    print 'receive keycode,keyname,type,state:'+str(evt.detail)+','+key_name+','+str(evt.type)+','+str(mod)
    key={'key':key_name, 'mod':mod}
    if not key in keys:
       if evt.type==X.KeyRelease: #only can send key after previous key released
          is_ready_switchall=0
          key_delay_shift=key_name  #because shift key still pressed
       return
    key_mapped=keys_mapped[keys.index(key)]

    global is_on
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
         if not is_on:#shift is pressed, grabbed something, but off status should grab nothing
            key_delay_shift=key_name #because shift key still pressed
            return
         if not key_mapped['key'] in ['MoveLeft', 'MoveRight', 'MoveUp', 'MoveDown',
                                      X.Button1,X.Button2,X.Button3,X.Button4,X.Button5
                                     ]:
            send_event(key_mapped['key'], key_mapped['mod'], 0)
            send_event(key_mapped['key'], key_mapped['mod'], 1)

def switch_all():
    global is_on
    for key in keys:
        if key['key']!='Shift_L' and key['key']!='Shift_R':
           if not is_on:
              grab_key(key['key'], key['mod'])
           else:
                ungrab_key(key['key'], key['mod'])
    if is_on:
       is_on=0
    else:
         is_on=1
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
             print evt.detail,evt.state
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

def main():
    #listen_shift()
    #print string_to_keycode('F1')
    grab_key('Shift_L', X.NONE)
    grab_key('Shift_R', X.NONE)
    send_event(X.Button1, X.NONE, 1)
    send_event(X.Button2, X.NONE, 1)
    send_event(X.Button3, X.NONE, 1) #maybe you pressed right mouse button, but myboard.py killed, then mouse and keyboard blocked
    send_event(X.Button4, X.NONE, 1)
    send_event(X.Button5, X.NONE, 1)
    while 1:
          evt=root.display.next_event()
          if evt.type in [X.KeyPress, X.KeyRelease]: #ignore X.MappingNotify(=34)
             handle_event(evt)

if __name__ == '__main__':
   main()

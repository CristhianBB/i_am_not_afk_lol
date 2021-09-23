import pygetwindow as gw
import pyautogui
import os
import os.path
import re
import json

from .const import *
from .util import file_is_being_used, pretty_log

class LeagueClient(object):
    def __init__(self):
        self.reset()
        self.update()

    def reset(self):
        self.hwnd = None
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

        self.player_cell_id=None
        self.phase = None
        self.previous_phase=None

        self.logname = None

        # log attrs
        self._last_size = 0
        self._last_str = ''
        self._file_index = 0
        self.initialized = False
    
    def exists(self):
        return self.hwnd != None
    
    def focus(self):
        if self.hwnd == None:
            return False
        
        try:
            if not self.hwnd.isMinimized:
                self.hwnd.minimize()

            self.hwnd.restore()
            self.hwnd.activate()
        except:
            pass
        
        return self._is_focused()

    def _is_focused(self):
        try:
            return (gw.getActiveWindow() == self.hwnd)
        except:
            pass
            
        return False

    def _get_window(self):
        try:
            windows = gw.getWindowsWithTitle(LEAGUE_WINDOW_TITLE)

            if len(windows) < 1:
                self.hwnd = None
            else:
                self.hwnd = windows[0]
        except:
            self.hwnd = None

    def _get_window_info(self):
        if self.hwnd == None:
            return
        
        self.x = self.hwnd.left
        self.y = self.hwnd.top
        self.w = self.hwnd.width
        self.h = self.hwnd.height
    def _get_logname(self):
        log = None
        for root, dirs, files in os.walk(LOG_DIR):
            for file in files:
                if file.endswith('LeagueClient.log'):
                    fpath = LOG_DIR + file
                    if file_is_being_used(fpath):
                        log = fpath
                        break

        self.logname = log

    def _update_log(self):
        if self.hwnd == None:
            return False

        with open(self.logname) as f:
            f.seek(self._file_index)
            self._last_str = f.read(self._last_size - self._file_index)
            self._file_index = self._last_size
        
        return True

    def _log_has_changed(self):
        if self.logname == None:
            return False

        fsize = os.stat(self.logname).st_size
        if fsize != self._last_size:
            self._last_size = fsize
            self._update_log()
            return True

        return False

    def _parse_log(self):
        lines = self._last_str.splitlines()

        for lineNumber in reversed(range(len(lines))):
            line = lines[lineNumber]
            phase = re.search(r'Matchmaking: entering state \'(\w+)\'', line)
            
            if phase != None:
                phase = phase.group(1)
                if (self.phase != phase) and phase in LEAGUE_PHASE.values():
                    self.phase = phase
                    break
            elif 'READY_CHECK_USER_ACCEPTED' in line:
                self.phase = LEAGUE_PHASE.MATCHACCEPTED
                break
            elif '/lol-champ-select/v1/session: ' in line:
                if self._parse_json(line):
                    break
    
    def _parse_json(self, line):
        ts = '/lol-champ-select/v1/session: '
        data = line[line.find(ts) + len(ts):]
        data = json.loads(data)

        self.player_cell_id = data['localPlayerCellId']

        for actions in data['actions']:
            for action in actions:
                if action['isInProgress'] and not action['completed'] and action['actorCellId'] == self.player_cell_id:
                    if action['type'] == 'ban':
                        self.phase = LEAGUE_PHASE.BAN_TURN
                        return True
                    elif action['type'] == 'pick':
                        self.phase = LEAGUE_PHASE.PICK_TURN
                        return True

        return False

    def _accept_match(self):
        try:
            button_x = self.x + (self.w * 0.511)
            button_y = self.y + (self.h * 0.765)

            pyautogui.click(x=button_x, y=button_y) 
            return True
        except:
            return False

    def try_accept_match(self):
        if(self.focus()):
            self._accept_match()

    def log(self, p_phase):
        if p_phase != self.phase:
            if self.in_phase(LEAGUE_PHASE.LOBBY):
                pretty_log('[Client] Lobby')
            elif self.in_phase(LEAGUE_PHASE.QUEUE):
                pretty_log('[Client] Queue')
            elif self.in_phase(LEAGUE_PHASE.MATCHFOUND):
                pretty_log('[Client] Match Found')
            elif self.in_phase(LEAGUE_PHASE.MATCHACCEPTED):
                pretty_log('[Client] Match Accepted')
            elif self.in_phase(LEAGUE_PHASE.PICKSANDBANS):
                pretty_log('[Client] Picks and Bans')
            elif self.in_phase(LEAGUE_PHASE.BAN_TURN):
                pretty_log('[Client] Waiting Your Ban')
            elif self.in_phase(LEAGUE_PHASE.PICK_TURN):
                pretty_log('[Client] Waiting Your Pick')
            elif self.in_phase(LEAGUE_PHASE.RECONNECT):
                pretty_log('[Client] Waiting reconnection...')
            elif self.in_phase(LEAGUE_PHASE.LOBBYOUT) or self.in_phase(LEAGUE_PHASE.NONE):
                pretty_log('[Client] Out of Lobby')
            elif self.in_phase(LEAGUE_PHASE.GAMESTART):
                pretty_log('[Client] Game Starting')
            else:
                pretty_log(self.phase)

    def in_phase(self, phase):
        return self.phase == phase

    def previous_phase_is(self, phase):
        return self.previous_phase == phase

    def previous_phase_isnt(self, phase):
        return self.previous_phase != phase

    def isnt_same_phase(self):
        return self.phase != self.previous_phase
    
    def update(self=None, noLog=False):
        self._get_window()

        if self.initialized:
            if not self.exists():
                pretty_log('[Client] Lost')
                self.reset()
                return
        elif self.exists():
            pretty_log('[Client] Found')
            self.initialized = True
        
        self._get_logname()

        p_phase = self.phase
        self.previous_phase=p_phase
        if self._log_has_changed():
            self._parse_log()
        
        if self.phase == 'ReadyCheck':
            self._get_window()
            self._get_window_info()
        
        if not noLog:
            self.log(p_phase)
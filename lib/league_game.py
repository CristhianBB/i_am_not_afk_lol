import pygetwindow as gw
import os
import os.path
import time
from .util import pretty_log, file_is_being_used

from .const import *

class LeagueGame(object):
    def __init__(self):
        self.reset()
        self.update()

    def reset(self):
        self.logname = None
        self.hwnd = None

        self.phase = None

        # log attrs
        self._last_size = 0
        self._last_str = ''
        self._file_index = 0
        self.initialized = False

    def exists(self):
        return self.hwnd != None

    def update(self):
        self._get_window()
        if self.initialized:
            if not self.exists():
                self.reset()
                return
        elif self.exists():
            self.initialized = True

        self._get_logname()
        p_phase = self.phase
        if self._log_has_changed():
            self._parse_log()
        
        self.log(p_phase)

    def _get_window(self):
        windows = gw.getWindowsWithTitle(LEAGUE_GAME_WINDOW_TITLE)

        if len(windows) < 1:
            self.hwnd = None
        else:
            self.hwnd = windows[0]

    def is_focused(self):
        return (gw.getActiveWindow() == self.hwnd)
    
    def _get_logname(self):
        logdir = None
        for root, dirs, files in os.walk(GAME_LOG_DIR):
            for ldir in dirs:
                fpath = GAME_LOG_DIR + ldir
                if file_is_being_used(fpath):
                    logdir = fpath
                    break

        if logdir == None:
            return
        
        logdir = logdir + '\\'
        log = None
        for root, dirs, files in os.walk(logdir):
            for file in files:
                if file.endswith('r3dlog.txt'):
                    fpath = logdir + file
                    if file_is_being_used(fpath):
                        log = fpath
                        break
        
        self.logname = log

    def _update_log(self):
        try:
            if not self.exists():
                return False

            with open(self.logname) as f:
                f.seek(self._file_index)
                self._last_str = f.read(self._last_size - self._file_index)
                self._file_index = self._last_size
            
            return True
        except:
            return False

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

        for lineNumber in range(0, len(lines)):
            line = lines[lineNumber]

            if 'Waiting for response from game server...' in line:
                self.phase = 'loading'
            elif 'Received Game Start Packet' in line:
                self.phase = 'started'

    def log(self, p_phase):
        if p_phase != self.phase:
            if self.has_started():
                pretty_log('[Game] Started')
            elif self.is_loading():
                pretty_log('[Game] Loading')

    def wait_exists(self):
        while not self.exists():
            self.update()
            time.sleep(1)
    
    def wait_game_start(self):
        while True:
            self.update()

            if self.has_started() or not self.exists():
                break

            time.sleep(1)

    def wait_game_end(self):
        while True:
            self._get_window()

            if not self.exists():
                break

            time.sleep(5)

    def is_loading(self):
        return self.phase == 'loading'

    def has_started(self):
        return self.phase == 'started'
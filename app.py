import time
from pyautogui import keyUp
import pygetwindow
import ctypes  
from lib.discord import DiscordBot

from lib.league_game import LeagueGame
from lib.league_client import LeagueClient
from lib.config import Config
from lib.util import pretty_print, pretty_log
from lib.const import *
from os import system

class App:
    title: str = 'i am not afk!'
    secs_between_updates: int = 1

    config: Config
    discord_bot: DiscordBot
    league_client: LeagueClient
    league_game: LeagueGame

    first_run: bool

    def __init__(self):
        self.config = None
        self.discord_bot = None
        self.league_client = None
        self.league_game = None

        self.setup()

    def setup(self):
        ctypes.windll.kernel32.SetConsoleTitleW(self.title)
        pretty_log("I Am Not Afk!")

        self.first_run = True
        self.config = Config()
        
        config_str = '\n\t'.join(self.config.printable(True).split('\n'))
        config_str = '\t' + config_str
        print(config_str.expandtabs(11))


    
        self.discord_bot = DiscordBot(self.config.get_str_value('DISCORD_WEBHOOK') + self.config.get_str_value('DISCORD_WEBHOOK_PARAMS'))
        
        self.league_client = LeagueClient()
        self.league_game = LeagueGame()

    def focus(self):
        w = pygetwindow.getWindowsWithTitle(self.title)
        if len(w) < 1:
            return
        
        w = w[0]
        if not w.isMinimized:
            w.minimize()

        w.restore()
        w.activate()
    

    def process_league_client(self):

        if self.league_client.in_phase(LEAGUE_PHASE.MATCHFOUND):
            self.league_client.try_accept_match() 

        if self.league_client.isnt_same_phase():
            self.secs_between_updates = 0.5 if self.league_client.in_phase(LEAGUE_PHASE.QUEUE) else 1

            if self.config.get_bool_value('GAME_PHASES_ALERT_DISCORD') and self.discord_bot.ok:
                message = None
                if self.league_client.in_phase(LEAGUE_PHASE.PICKSANDBANS):
                    message = ', estamos na seleção de campeões!'
                elif self.league_client.in_phase(LEAGUE_PHASE.BAN_TURN):
                    message = ', é sua vez de banir um campeão!'
                elif self.league_client.in_phase(LEAGUE_PHASE.PICK_TURN):
                    message = ', selecione seu campeão!'
                
                if message is not None:
                    message = (self.config.get_mention_value('DISCORD_MENTION') or 'Hey') + message
                    self.discord_bot.send_message(
                        message=message
                    )

    def process_league_game(self):
        if not self.league_game.has_started():
            return

        if self.config.get_bool_value('GAME_PHASES_ALERT_DISCORD') and self.discord_bot.ok:
            self.discord_bot.send_message(
                message=(self.config.get_mention_value('DISCORD_MENTION') or 'Hey') + ', a partida iniciou!',
            )
            
        if self.config.get_value('GAME_START_ALERT_BEEP') > 0:
            print('\a' * self.config.get_value('GAME_START_ALERT_BEEP'), end='')
        if self.config.get_value('GAME_START_ALERT_TEXT') == 1:
            if not self.league_game.is_focused():
                self.focus()
            ctypes.windll.user32.MessageBoxW(0, "The game was started!", "I Am Not Afk", 48)
        
        if self.config.get_value('GAME_START_CLOSE') == 1:
            raise KeyboardInterrupt()
        else:
            pretty_log('Waiting game end...')
            self.league_game.wait_game_end()


    def update(self):
        self.league_client.update()
        self.league_game.update()

        if self.league_client.exists():
            self.process_league_client()

        if self.league_game.exists():
            self.process_league_game()

    def run(self):
        try:
            self.update()

            if not (self.league_client.exists() or self.league_game.exists()):
                pretty_log('Start League Client before running the app...')
                raise KeyboardInterrupt()

            while 1:
                self.update()
                time.sleep(self.secs_between_updates)
        except KeyboardInterrupt:
            pass

        pretty_log('Tchau!')

        system("pause")

if __name__ == '__main__':
    App().run()
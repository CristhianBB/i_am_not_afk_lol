class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

RIOT_GAMES='C:\\Riot Games\\'
LOG_DIR = RIOT_GAMES + 'League of Legends\\Logs\\LeagueClient Logs\\'

LEAGUE_WINDOW_TITLE = 'League of Legends'

LEAGUE_PHASE = dotdict({
    'LOBBY': 'Available',
    'QUEUE': 'Searching',
    'MATCHFOUND': 'ReadyCheck',
    'MATCHACCEPTED': 'ReadyCheckAccepted',
    'PICKSANDBANS': 'ChampSelect',
    'BAN_TURN': 'BanTurn',
    'PICK_TURN': 'PickTurn',
    'GAMESTART': 'GameStart',
    'RECONNECT': 'ReconnectAvailable',
    'NONE': 'None',
    'LOBBYOUT':'OutOfLobby',
})

GAME_LOG_DIR = RIOT_GAMES + 'League of Legends\\Logs\\GameLogs\\'
LEAGUE_GAME_WINDOW_TITLE = 'League of Legends (TM) Client'

CONFIG_FILENAME = 'config.ini'
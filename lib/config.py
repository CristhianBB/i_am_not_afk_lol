from .const import *
from .util import pretty_text, pretty_log
import os.path
    
def try_int(strvalue):
    v = None
    try:
        v = int(strvalue)
    except:
        v = strvalue
    
    return isinstance(v, int), v

class Config(object):
    def __init__(self=None):
        self.filename = CONFIG_FILENAME
        self.values = {}

        self.parse_file()
    
    def parse_file(self):
        if not os.path.exists(self.filename):
            return False
        
        with open(self.filename, 'r') as f:
            line_count = 0
            for line in f.readlines():
                line_count += 1

                if line[0] == "#": #comentário
                    continue

                splitted = line.split('=', 1)
                if len(splitted) == 2:
                    key = splitted[0]
                    value = splitted[1].strip()
                    is_int, ivalue = try_int(value)
                    self.values[key] = ivalue
                else:
                    pretty_log("{}: Invalid entry at line {}.".format(self.filename, str(line_count)))
        
        return True

    def save_file(self):
        with open(self.filename, 'w') as f:
            for key in self.values:
                f.write(key)
                f.write('=')
                f.write(self.values[key])
                f.write('\r\n')
        
        return True

    def set_value(self, field, value):
        self.values[field] = value

    def get_mention_value(self, field):
        if field not in self.values:
            return None

        return self.values[field]
                
    def get_value(self, field):
        if field not in self.values:
            return None
        
        return self.values[field]
        
    def get_str_value(self, field):
        if field not in self.values:
            return ''
        
        return str(self.values[field])
    
    def get_bool_value(self, field):
        if field not in self.values:
            return False

        is_int, ivalue = try_int(self.values[field])
        
        if not is_int:
            return True
        
        return ivalue > 0
    
    def get_values(self):
        return self.values

    def __str__(self):
        config_str = []
        for field in self.get_values():
            config_str.append(pretty_text(field.replace('_', ' ')))
            config_str.append('\t[')
            value = self.get_value(field)
            if isinstance(value, int):
                config_str.append(value > 0 and 'Yes' or 'No')
            else:
                config_str.append('"' + value + '"')
            config_str.append(']')
            config_str.append('\n')
        
        if len(config_str) > 0:
            config_str.pop()
        config_str = ''.join(config_str).expandtabs(30)
        return config_str
      
    def printable(self, only_bool=False):
        config_str = []
        for field in self.get_values():
            value = self.get_value(field)
            if isinstance(value, int):
                config_str.append(pretty_text(field.replace('_', ' ')))
                config_str.append('\t[')
                config_str.append(value > 0 and 'Yes' or 'No')
                config_str.append(']')
                config_str.append('\n')
        
        if len(config_str) > 0:
            config_str.pop()
        config_str = ''.join(config_str).expandtabs(30)
        return config_str 
    def printme(self):
        print(str(self))
import os
import datetime as dt

def file_is_being_used(f):
    if os.path.exists(f):
        try:
            os.rename(f, f)
            return False
        except OSError as e:
            return True

    return False

def pretty_print(text1='', text2='', et=30):
    text = text1 + '\t' + text2
    print(text.expandtabs(et))

def pretty_log(text1='', et=11):
    text = '[' + dt.datetime.now().strftime("%H:%M:%S") + ']\t' + text1
    print(text.expandtabs(et))

def pretty_text(text1=''):
    splitted = text1.split(' ')
    new = []
    for word in splitted:
        new.append(word.capitalize())

    return ' '.join(new)
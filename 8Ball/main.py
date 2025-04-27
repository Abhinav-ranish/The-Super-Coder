import random

def get_random_number(minimum, maximum):
    return random.randint(minimum, maximum)

@app.route('/')
def index():
    number = get_random_number(1, 8)
    if number == 1:
        return 'It is certain.'
    elif number == 2:
        return 'It is decidedly so.'
    elif number == 3:
        return 'Reply hazy, try again.'
    elif number == 4:
        return 'Cannot predict now.'
    elif number == 5:
        return 'Do not count on it.'
    elif number == 6:
        return 'My reply is no.'
    elif number == 7:
        return 'My sources say no.'
    elif number == 8:
        return 'Outlook good.'
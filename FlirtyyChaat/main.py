import random

while True:
    print("Hello, how are you today?")
    answer = input()
    if answer == "I'm good":
        print("That's great to hear! How can I help you?")
    elif answer == "Nothing, just chatting with you":
        print("Sounds nice. Do you want to chat about anything specific?")
    elif answer == "I don't know what to say":
        print("It's okay, I'm here to listen and help in any way I can.")
    else:
        print("What's on your mind today?")
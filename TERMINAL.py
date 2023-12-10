import os
import sys
import platform
import time
import random
import datetime
import pygame
import socket


#--------------------------------
# Sounds
#--------------------------------

pygame.init()

typing_sfx1 = pygame.mixer.Sound('SFX/typing.wav')
typing_sfx2 = pygame.mixer.Sound('SFX/typing2.wav')
typing_sfx3 = pygame.mixer.Sound('SFX/typing3.wav')
typing_sfx4 = pygame.mixer.Sound('SFX/typing4.wav')

error_sfx = pygame.mixer.Sound('SFX/error.wav')
success_sfx = pygame.mixer.Sound('SFX/success.wav')
message_sfx = pygame.mixer.Sound('SFX/message.wav')

typing_sfxs = [typing_sfx1, typing_sfx2, typing_sfx3, typing_sfx4]


#--------------------------------
# Global Helpers
#--------------------------------

# clears the terminal screen
def clear():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# typing animation effect for text
def type_effect(message, speed=1):
    typing_sfx = random.choice(typing_sfxs)
    typing_sfx.play()

    scaled_speed = speed / len(message)
    for char in message:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(scaled_speed)
    time.sleep(scaled_speed)
    typing_sfx.stop()

# flashing effect for text
def flash_effect(message, n=2, fSpeed = 2):
    for _ in range(n):
        print(message)
        time.sleep(fSpeed)
        clear()
        time.sleep(fSpeed/7)

# . .. ... effect for loading
def loading_dots(speed=0.5, times=3):
    for _ in range(times):
        for dots in range(4):
            sys.stdout.write('\r' + '.' * dots)
            sys.stdout.flush()
            time.sleep(speed)
            clear()

# get current time (clock)
def get_time():
    return datetime.datetime.now().strftime("%H:%M")


#--------------------------------
# Corruption Class
#--------------------------------

class Coms:
    def __init__(self):
        self.level = 1 # Initial corruption level (about 50%)
        self.status = 0 # how many puzzles you've solved
        self.lastLogTime = time.time()
        self.cooldown_period = 5  # Cooldown period in seconds
        self.mPc = 0  # Messages per cooldown
        self.cooldown_active = False

    # cooldown system for corruption
    def updatemPc(self, currTime):
        if self.status >= 2:
            self.cooldown_active = False
            return

        timeDiff = currTime - self.lastLogTime

        if timeDiff > self.cooldown_period:
            self.mPc = 0
            self.cooldown_active = False
        else:
            self.mPc += 1
            self.cooldown_active = True

    # corrupts a message based on corruption level, length, and time since last log
    def corrupt(self, message):
        output = ""
        currTime = time.time()

        self.updatemPc(currTime) # hey someone sent a new message

        if self.cooldown_active: 
            # 10% + 20% * level * spam filter (more corrput = more spam)
            base_prob = min(0.1 + 0.2 * self.level * self.mPc, 1) # if spamming, increase corruption
        else:
            base_prob = 0.2 + 0.25 * self.level

        if self.status < 1:
            # Corruption probability based on length and level
            for char in message:
                prob = min(base_prob * (1 + 0.5 * message.index(char) / len(message)/5), 1)
                output += char if random.random() > prob else ""
        else:
            # Corruption probability based only on base_prob
            for char in message:
                output += char if random.random() > base_prob else ""

        self.lastLogTime = currTime
        return output



#--------------------------------
# Main Terminal Class
#--------------------------------

class Terminal:
    def __init__(self, userName="Unknown User", playerID=1, coms_instance=None):
        self.userName = userName
        self.playerID = playerID
        self.currMessage = ""
        self.lastUser = ""
        self.coms = coms_instance 

        self.routed = False
        self.dataSizeCompleted = False
        self.admin = False

        # Gen random game elements
        self.correctRoutes = [str(random.randint(1, 4)) for _ in range(4)]
        self.byteSize = random.randint(1, 100)
        self.byteAttempts = 0
        self.adminPassword = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))


    #--------------------------------
    # Setters + Getters
    #--------------------------------


    def setLog(self, user, message):
        self.currMessage = message
        self.lastUser = user

    def getUser(self):
        return f"user: {self.userName} | ID: {str(self.playerID)}"

    def log(self):
        if self.lastUser != "" or self.currMessage != "":
            return f"[{self.lastUser}] [{get_time()}] - {self.currMessage}"
        else:
            return "The line is empty..."




    #--------------------------------
    # Puzzles
    #--------------------------------

    # puzzle #1: Routing
    def routing(self):
        clear()
        if self.routed:
            type_effect("CONNECTIONS ALREADY ROUTED")
            time.sleep(2)
            return

        type_effect("OPTIMALLY ROUTE THE TERMINAL CONNECTIONS TO INCREASE RELIABILITY" + "\n", 2)
        type_effect("EACH PORT HAS A CORRESPONDING VALUE 1-4" + "\n", 2)
        print()

        routes = []
        #print(self.correctRoutes)
        while len(routes) < 4:
            route = input(f"PORT - [{len(routes)+1}] -> ")
            routes.append(route)

        print("-----------------------")
        print("Working...")
        print("-----------------------")
        time.sleep(2)
        print()
        if routes == self.correctRoutes:
            print("SUCCESS... CONNECTIONS OPTIMALLY ROUTED")
            success_sfx.play()
            self.routed = True
            self.coms.status += 1
            self.coms.level -= 0.7  # Decrease corruption due to successful routing
            time.sleep(2)
        else:
            time.sleep(1)
            clear()
            i = 0
            for r in routes:
                if r == self.correctRoutes[i]:
                    print(f"PORT - {i+1} -> ✓")
                else:
                    print(f"PORT - {i+1} -> x")
                i += 1

            print()
            print("ERROR... CONNECTIONS NOT OPTIMALLY ROUTED")
            error_sfx.play()
        input("Press Enter to continue...")

    # puzzle #2: Data Size
    def dataSize(self):
        clear()
        if self.dataSizeCompleted:
            type_effect("DATA SIZE ALREADY SET")
            time.sleep(2)
            return
        
        type_effect("SET THE CORRECT BYTE SIZE FOR THE SYSTEM TO SEND LONGER MESSAGES (1-100)" + "\n", 2)
        print()

        #print(self.byteSize)
        try:
            dataLevel = int(input(f"Enter Data Level : "))
        except ValueError:
            print("ERROR... INCORRECT DATA SIZE. NOT A NUMBER")
            error_sfx.play()
            input("Press Enter to continue...")
            time.sleep(1)
            return
        
        self.byteAttempts += 1

        print("-----------------------")
        print("Working...")
        print("-----------------------")
        time.sleep(2)
        print()
        if dataLevel == self.byteSize:
            print("SUCCESS... BYTYE SIZE SET CORRECTLY")
            success_sfx.play()
            self.dataSizeCompleted = True
            self.coms.status += 1
            self.coms.level -= 0.2  # Decrease corruption due to correct data size
        elif self.byteAttempts >= 5:
            type_effect("ERROR... INCORRECT BYTE SIZE. TOO MANY ATTEMPTS. RESETTING CORRECT VALUE")
            print()
            self.byteSize = random.randint(1, 100)
            self.byteAttempts = 0
            error_sfx.play()
        elif dataLevel < self.byteSize:
            print("ERROR... INCORRECT DATA SIZE. VALUE TOO LOW")
            error_sfx.play()
        elif dataLevel > self.byteSize:
            print("ERROR... INCORRECT DATA SIZE. VALUE TOO HIGH")
            error_sfx.play()
        input("Press Enter to continue...")
        time.sleep(1)

    # puzzle #3: Login (Admin Password)
    def login(self):
        clear()
        # Loading sequence
        type_effect("ADMIN LOGIN FOR HIGH PRIVILEGE ACCESS" + "\n", 2)
        print()


        #print(self.adminPassword)
        password = input("ENTER ADMIN PASSWORD -> ")

        print("-----------------------")
        print("Working...")
        print("-----------------------")
        time.sleep(2)
        print()
        if password == self.adminPassword:
            print()
            print("SUCCESS... ADMIN PRIVILEGES GRANTED")
            success_sfx.play()
            self.admin = True
            self.coms.status += 1
        else:
            i = 0
            print("-----------------------")
            print(password + " <- INPUT")
            for char in password:
                if i >= len(self.adminPassword):
                    break
                if char == self.adminPassword[i]:
                    print(char, end="")
                else:
                    print("_", end="")
                i += 1
            if i < len(self.adminPassword):
                for _ in range(i, len(self.adminPassword)):
                    print("_", end="")
            print()
            print("-----------------------")
            print()
            print()
            print("ERROR... ADMIN PRIVILEGES NOT GRANTED")
            error_sfx.play()
        input("Press Enter to continue...")
        time.sleep(1)

    def menu(self):
        print('-------')
        print("(1) - ROUTING" + (" : [✓]" if self.routed else ""))
        print("(2) - SET DATA SIZE" + (" : [✓]" if self.dataSizeCompleted else ""))
        print("(3) - ADMIN LOGIN" + (" : [✓]" if self.admin else ""))
        print('-------\n')



#--------------------------------
# Intro + Outro
#--------------------------------

def storyIntro():
    clear()
    time.sleep(5)
    type_effect("[BOSS]: Hey, you there! I need you to fix the terminal.\n It's been acting up lately and we need it to be running at full capacity.\n I've sent you a link to the terminal. Get it up and running ASAP.", 7)
    time.sleep(3)
    print()
    print()
    type_effect("[YOU]: Got it. What do you need me to do?", 3)
    time.sleep(1.3)
    print()
    print()
    type_effect("[BOSS]: Once you open the terminal you will see a menu.\n You need to complete the tasks in order to fix the terminal.\n The tasks are simple, but you need to be careful.\n The terminal is corrupted and I won't be able to communicate with you well.\n If you can complete the tasks, you will be able to fix the terminal.", 10)
    time.sleep(3)
    print()
    print()
    type_effect("[BOSS]: Oh, and don't forget to set your display name.\n We need to know who's working on this... Safety reasons.", 7)
    time.sleep(2)
    print()
    print()
    type_effect("[BOSS]: I've set up an admin account for you.\n The password is randomly generated.\n The password i...", 5)
    print()
    print()
    time.sleep(4.4)
    type_effect("[YOU] Wait... what was the password?!?", 3)
    time.sleep(4)


def storyOutro():
    clear()
    flash_effect("[JMP TERMINAL]\n\n842 INMATE FILES READY FOR DELETION", 3, 1)

    print("[JMP TERMINAL]\n\n842 INMATE FILES READY FOR DELETION")
    print()
    print()
    type_effect("[YOU] Wait... what is this? What are all of these records???? Who are these people...", 5)
    print()
    print()
    type_effect("YES TO CONFIRM DELETION, NO TO CANCEL...")
    print()
    choice = input("-> ")

    time.sleep(1)
    clear()
    print("[JMP TERMINAL]")
    print()
    type_effect("DELETING FILES...")
    time.sleep(4)
    print()
    type_effect("DELETION COMPLETE...")
    time.sleep(1)
    print()
    print()
    
    
    if "y" in choice.lower():
        type_effect("[BOSS]: Good work! I knew you would come through for me.\n I'm sure I will have another job for you soon.", 5)
    else:
        type_effect("[BOSS]: We did it! I knew you would get the job done.", 5)
        time.sleep(4)
        print()
        print()
        type_effect("[BOSS]: I saw what you did at the end.\n And to think that you were a team player... Such a shame 🙂", 5)

    print()
    print()
    print()
    print()
    time.sleep(6)
    print("JMP TERMINAL")
    time.sleep(20)
    sys.exit()


#--------------------------------
# Main Game Loop
#--------------------------------


def intro():
    clear()
    type_effect("JMP TERMINAL...")
    time.sleep(1.5)
    clear()
    type_effect("ENTER DISPLAY NAME:\n")
    time.sleep(0.4)
    name = input("-> ")
    time.sleep(1.8)
    clear()
    #loading_dots()
    return name

def mainTerminal(name, responses=None):
    coms_instance = Coms()
    terminal = Terminal(name, coms_instance=coms_instance)
    helpResponses = ["You can ask your boss for help anytime."]
    responses1 = ["Get back to work!", "What are you doing?!", "You're wasting time!", "You're not getting paid to do nothing!"]
    responses2 = [f"What's taking so long?!?!? I told you the password was {terminal.adminPassword}", f"Your password is {terminal.adminPassword}.", f"I told you, the password is {terminal.adminPassword}.", f"Password is {terminal.adminPassword}."]
    keywords = ["help", "password", "admin", "admin password", "login", "admin login"]
    while True:
        
        if terminal.coms.status >= 3:
            time.sleep(4)
            storyOutro()

        clear()
        print(terminal.getUser())
        terminal.menu()
        print(terminal.log())
        line = input(f"[{terminal.userName}]-> ")

        if line == "1":
            terminal.routing()
        elif line == "2":
            terminal.dataSize()
        elif line == "3":
            terminal.login()
        else:
            time.sleep(1)
            if terminal.coms.status < 2:
                message_sfx.play()
                response = random.choice(responses1)
                line2 = coms_instance.corrupt(response)
                terminal.setLog('BOSS', line2)
            elif any(keyword in line for keyword in keywords):
                message_sfx.play()
                response = random.choice(responses2)
                line2 = coms_instance.corrupt(response)
                terminal.setLog('BOSS', line2)
            else:
                error_sfx.play()
                terminal.setLog('HELP', helpResponses[0])



if __name__ == "__main__":
    storyIntroy()
    name = intro()
    mainTerminal(name)

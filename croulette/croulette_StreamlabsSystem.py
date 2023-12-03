#!/usr/bin/python
#
# Casino-style roulette command
# Author: djm
# 11/06/23
#
# How to Use
# ----------
# Specify 1 argument corresponding to the type of bet you want. Pretty much that
# simple.
#
# The argument is not case-sensitive; i.e., "d1" is the same as "D1" and "e" is
# the same as "E".
#
#       examples:   !croulette 00   (straight bet for 00)
#                   !croulette 34   (straight bet for 34)
#                   !croulette e    (bet on all even numbers)
#                   !croulette d1   (bet on first dozen, excluding 0 and 00)
#                   etc.
#
# Payouts are "realistic", meaning they correspond to what a casino would pay
# (e.g., a straight bet win would pay 35:1), except payout is in XP instead of
# money - what a ripoff!
#
# Valid Bet Types
# ----
# <number>      Exact (straight) bet for that wheel number: 0, 00, or 1-36.
#               Pays 35:1
#
# b             Bet on all black numbers (see BLACK constant array below).
#               Pays 1:1
#
# r             Bet on all red numbers (see RED constant array below).
#               Pays 1:1
#
# e             Bet on all even numbers (excludes 0, 00).
#               Pays 1:1
#
# o             Bet on all odd numbers.
#               Pays 1:1
#
# l             Bet on all low numbers (1-18 only).
#               Pays 1:1
#
# h             Bet on all high numbers (19-36 only).
#               Pays 1:1
#
# c1, c2, c3    Bet on first, second, or third vertical column (excludes 0, 00).
#               c1 = 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34
#               c2 = 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35
#               c3 = 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36
#               Pays 2:1
#
# d1, d2, d3    Bet on first, second, or third dozen (excludes 0, 00).
#               d1 = 1-12
#               d2 = 13-24
#               d3 = 25-36
#               Pays 2:1
# ----
#
# Imports
#
import codecs
import ctypes
import json
import os
import random

#
# Script Information
#
ScriptName = "croulette"
Website = "https://twitch.tv/"
Description = "Casino-style roulette chat command"
Creator = "djm"             # just some random guy
Version = "1.0"

#
# Constants
#
# settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# MessageBoxW icon constants
MB_INFO = 0x40              # information
MB_WARN = 0x30              # warning
MB_ERROR = 0x10             # error

# Standard US "double zero" roulette wheel
# Numbers are in wheel order (clockwise), starting with 0
WHEEL = ["0","28","9","26","30","11","7","20","32","17","5","22","34","15",
"3","24","36","13","1","00","27","10","25","29","12","8","19","31","18","6",
"21","33","16","4","23","35","14","2"]

# All red numbers
RED = ["1","3","5","7","9","12","14","16","18","19","21","23","25","27","30",
"32","34","36"]

# All black numbers
BLACK = ["2","4","6","8","10","11","13","15","17","20","22","24","26","28","29",
"31","33","35"]

# Valid bet types (see header comments)
BETS = ["b", "r", "o", "e", "h", "l", "c1", "c2", "c3", "d1", "d2", "d3"]

#
# Local Variables
#
CmdSettings = None                          # "global" settings object
MBox = ctypes.windll.user32.MessageBoxW     # message box

#
# Initialize the command on Chatbot load.
#
def Init():
    global CmdSettings, MBox
    if(not SetSettings()):                  # attempt to load user settings
        SetDefaults()                       # defer to defaults on failure
    return

#
# Execute the command... just like it sounds.
#
def Execute(data):
    global CmdSettings, MBox

    # user didn't run this command?
    cmdName = CmdSettings["command"]        # command name
    if(data.GetParam(0) != cmdName):
        return                              # oops - we shouldn't be here!

    outMessage = ""                         # outgoing message

    # variables for convenient reference
    cmdCost = CmdSettings["cost"]               # command cost
    currencyName = CmdSettings["currencyName"]  # channel currency name
    msgInvalid = CmdSettings["msgInvalidBet"]   # invalid bet message
    msgBase = CmdSettings["msgBase"]            # base message for result
    msgLoss = CmdSettings["msgLoss"]            # loss message

    # user doesn't have enough XP?
    if(Parent.GetPoints(data.User) < cmdCost):
        outMessage = CmdSettings["msgNotEnough"].format(data.User,
          str(cmdCost), currencyName)
        Parent.SendStreamMessage(outMessage)
        return

    # still on user cooldown?
    if(Parent.IsOnUserCooldown(ScriptName, cmdName, data.User)):
        cooldown = Parent.GetUserCooldownDuration(ScriptName,
          cmdName, data.User)
        mins = str(cooldown / 60)
        secs = str(cooldown % 60).zfill(2)
        outMessage = CmdSettings["msgUserCooldown"].format(data.User,
          mins, secs)
        Parent.SendStreamMessage(outMessage)
        return

    if(len(data.GetParam(1)) == 0):         # user must supply a bet
        outMessage = msgInvalid.format(data.User)
        Parent.SendStreamMessage(outMessage)
        return
    else:
        userBet = data.GetParam(1).lower()

    if(userBet not in WHEEL and             # oh, and the bet must be valid
       userBet not in BETS):
        outMessage = msgInvalid.format(data.User)
        Parent.SendStreamMessage(outMessage)
        return

    result = random.choice(WHEEL)       # I can almost feel the excitement...
    iResult = int(result)               # integer form of result
    mult = 0                            # payout multiplier

    if(userBet == "b"):                 # user bet on black
        if(result in BLACK):            # payout is 1:1
            mult = 1
    elif(userBet == "r"):               # user bet on red
        if(result in RED):              # payout is 1:1
            mult = 1
    elif(userBet == "o"):               # user bet on odd
        if((iResult & 1) == 1):         # bitwise "and" is faster
            mult = 1                    # payout is 1:1
    elif(userBet == "e"):               # user bet on even
        if(iResult > 0 and              # 0, 00 not included
          (iResult & 1) == 0):          # bitwise "and" is faster
            mult = 1                    # payout is 1:1
    elif(userBet == "h"):               # user bet "high"
        if(iResult >= 19 and            # payout is 1:1
           iResult <= 36):
            mult = 1
    elif(userBet == "l"):               # user bet "low"
        if(iResult >= 1 and             # payout is 1:1
           iResult <= 18):
            mult = 1
    elif(userBet == "c1"):              # user bet column 1
        if(iResult > 0 and              # 0, 00 not included
           iResult % 3 == 1):           # these all have remainder 1 when / 3
            mult = 2                    # payout is 2:1
    elif(userBet == "c2"):              # user bet column 2
        if(iResult > 0 and              # 0, 00 not included
           iResult % 3 == 2):           # these all have remainder 2 when / 3
            mult = 2                    # payout is 2:1
    elif(userBet == "c3"):              # user bet column 3
        if(iResult > 0 and              # 0, 00 not included
           iResult % 3 == 0):           # these all have remainder 0 when / 3
            mult = 2                    # payout is 2:1
    elif(userBet == "d1"):              # user bet first dozen
        if(iResult >= 1 and             # payout is 2:1
           iResult <= 12):
            mult = 2
    elif(userBet == "d2"):              # user bet second dozen
        if(iResult >= 13 and            # payout is 2:1
           iResult <= 24):
            mult = 2
    elif(userBet == "d3"):              # user bet third dozen
        if(iResult >= 25 and            # payout is 2:1
           iResult <= 36):
            mult = 2
    elif(userBet == result):            # user made a straight bet and matched
        mult = 35                       # payout is 35:1
    else:                               # none of the above matched
        mult = 0                        # user lost

    payout = cmdCost * mult             # calculate payout
    outMessage = msgBase.format(data.User, result) + " ... "

    if(mult == 0):
        Parent.RemovePoints(data.User, data.UserName, cmdCost)
        outMessage = outMessage + msgLoss.format(str(cmdCost), currencyName)
        Parent.SendStreamMessage(outMessage)
    else:
        Parent.AddPoints(data.User, data.UserName, payout)

        if(mult == 35):
            winMessage = CmdSettings["msgJackpot"]
        elif(mult == 2):
            winMessage = CmdSettings["msg2to1"]
        else:
            winMessage = CmdSettings["msg1to1"]

        winMessage = winMessage.format(str(payout), currencyName)
        outMessage = outMessage + winMessage
        Parent.SendStreamMessage(outMessage)

    Parent.AddUserCooldown(ScriptName, cmdName, data.User, CmdSettings["userCooldown"])
    return

#
# Required Tick function (no-op)
#
def Tick():
    return

#
# Reads the settings file and sets the settings accordingly.
#
def SetSettings():
    global CmdSettings, MBox
    try:
        with codecs.open(SETTINGS_FILE, encoding="utf-8-sig", mode="r") as f:
            CmdSettings = json.load(f, encoding="utf-8-sig")
            if(len(CmdSettings["currencyName"]) == 0):
                MBox(0, u"Channel Currency Name is required.", u"Error", MB_ERROR)
                return False

            try:
                int(CmdSettings["cost"])
            except ValueError:
                MBox(0, u"Cost must be a number.", u"Error", MB_ERROR)
                return False

            try:
                int(CmdSettings["userCooldown"])
            except ValueError:
                MBox(0, u"User Cooldown must be a number.", u"Error", MB_ERROR)
                return False

            if(len(CmdSettings["msgBase"]) == 0):
                MBox(0, u"Base Message is required.", u"Error", MB_ERROR)
                return False

            if(len(CmdSettings["msgUserCooldown"]) == 0):
                MBox(0, u"User Cooldown Message is required.", u"Error", MB_ERROR)
                return False

            if(len(CmdSettings["msgInvalidBet"]) == 0):
                MBox(0, u"Invalid Bet Message is required.", u"Error", MB_ERROR)
                return False

            if(len(CmdSettings["msgNotEnough"]) == 0):
                MBox(0, u"Not Enough Currency Message is required.", u"Error", MB_ERROR)
                return False

            if(len(CmdSettings["msgLoss"]) == 0):
                MBox(0, u"Loss Message is required.", u"Error", MB_ERROR)
                return False

            if(len(CmdSettings["msgJackpot"]) == 0):
                MBox(0, u"Jackpot Message is required.", u"Error", MB_ERROR)
                return False

            if(len(CmdSettings["msg2to1"]) == 0):
                MBox(0, u"2:1 Win Message is required.", u"Error", MB_ERROR)
                return False

            if(len(CmdSettings["msg1to1"]) == 0):
                MBox(0, u"1:1 Win Message is required.", u"Error", MB_ERROR)
                return False
    except:
        return False

    return True

#
# Sets default settings if there were errors loading the settings file.
#
def SetDefaults():
    global CmdSettings, MBox
    MBox(0, u"Default settings are being used.", u"Warning", MB_WARN)
    CmdSettings = {
        "command": "!croulette",
        "currencyName": "XP",
        "cost": 50,
        "userCooldown": 300,
        "msgBase": "{0}, result: {1}",
        "msgUserCooldown": "{0}, the command is still on user cooldown for {1}:{2}!",
        "msgInvalidBet": "{0}, specify a valid bet: 0, 00, 1-36, b, r, o, e, h, l, c1, c2, c3, d1, d2, or d3",
        "msgNotEnough": "{0}, you don't have enough {2} to play! ({1} {2} required)",
        "msgLoss": "You lost {0} {1}. Better luck next time? riPepperonis",
        "msgJackpot": "JACKPOT! Congratulations. You might be a genius... or just really lucky. {0} {1} FlawlessVictory",
        "msg2to1": "You took a risk and it paid off! ... I think. {0} {1} SeemsGood",
        "msg1to1": "Alright, that was probably a little too easy. {0} {1} TwitchLit"
    }
    return

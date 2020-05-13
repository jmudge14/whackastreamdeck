# Whack-A-Streamdeck - Whack-A-Mole game for the Elgato Stream Deck
# Author: Jack Mudge <jack@mudge.dev>
# 

import Deck
from random import randint
from time import time
from time import sleep
import threading


class MoleGame():
    def __init__(this, deck, numMoles=3, minDelay=500, maxDelay=1000, explosionDisplayTime=500): # Initial State
        this.hill = []
        this.deck = deck
        this.numMoles = numMoles
        this.minDelay = minDelay
        this.maxDelay = maxDelay
        this.score = 0
        this.startTime = -1
        this.nextUpdateTime = -1

        # Mark where the last mole was whacked, to show an explosion
        this.explosion = None
        this.explosionUpdateTime = -1
        this.explosionDisplayTime = explosionDisplayTime

        # Game assets
        this.moleImage = Deck.getAsset(deck,"Mole.jpeg")
        this.blankImage = Deck.getAsset(deck, "Blank.jpeg")
        this.explosionImage = Deck.getAsset(deck, "Explosion.jpeg")

        # Thread management
        this.updateLock = threading.Lock()


    def randbutton(this):
        return randint(0, this.deck.key_count()-1)

    def start(this):
        def keyCallback(deck, key, state):
            this.keyCallback(key,state)
        this.deck.set_key_callback(keyCallback)
        # Mole positions are randomized in update()
        this.nextUpdateTime = 0 # Force initial update; time()>0 in all cases.
        this.startTime = time()
        this.update()

    def duration(this):
        return time()-this.startTime

    def update(this):
        t = time()
        # Reset explosion if enough time has passed
        if t>this.explosionUpdateTime:
            this.explosion = None
        if t>this.nextUpdateTime:
            this.nextUpdateTime = t+randint(this.minDelay, this.maxDelay)
        else:
            return

        # Populate the mole hill with new moles
        this.updateLock.acquire()
        nextHill = []
        for _ in range(this.numMoles):
            nextMole = this.randbutton()
            # Force the mole to *look* like it has moved: It can't overlap in the new
            # hill, and it should be different from any occupied spot in the old hill.
            while nextMole in nextHill or nextMole in this.hill:
                nextMole = this.randbutton()
            nextHill.append(nextMole)
        this.hill = nextHill
        this.updateLock.release()
        this.redraw()

    def redraw(this):
        # Set explosion first in case a mole has covered it.
        if this.explosion is not None:
            this.deck.set_key_image(this.explosion, this.explosionImage)

        for key in range(this.deck.key_count()):
            if key in this.hill:
                image = this.moleImage
            else:
                image = this.blankImage
            this.deck.set_key_image(key, image)


    def keyCallback(this, key, state):
        if state and key in this.hill:
            this.updateLock.acquire()
            this.score += 1
            # Move the mole that was just whacked
            nextMole = this.randbutton()
            while nextMole in this.hill:
                nextMole = this.randbutton()
            this.hill.remove(key)
            this.hill.append(nextMole)
            this.explosion = key
            this.explosionUpdateTime = time()+this.explosionDisplayTime
            this.updateLock.release()
            this.redraw()




if __name__ == "__main__":
    deck = Deck.getInitializedDeck(background="green");
    game = MoleGame(deck)
    game.start()
    while game.duration() < 20:
        print("Time elapsed: " + str(game.duration()))
        print("Score: " + str(game.score))
        print("")
        game.update()
        game.redraw()
        sleep(1)
    deck.close()






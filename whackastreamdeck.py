# Whack-A-Streamdeck - Whack-A-Mole game for the Elgato Stream Deck
# Author: Jack Mudge <jack@mudge.dev>
# 

import Deck
from random import randint
from time import time
from time import sleep
import threading


class MoleGame():
    def __init__(this, deck, numMoles=3, minDelay=500, maxDelay=1000, explosionDisplayTime=500, gameTime=60000): # Initial State
        this.hill = []
        this.deck = deck
        this.numMoles = numMoles
        this.minDelay = minDelay
        this.maxDelay = maxDelay
        this.gameTime = gameTime
        this.score = 0
        this.startTime = -1
        this.nextUpdateTime = -1
        this.gameOverTime = -1

        # Mark where the last mole was whacked, to show an explosion
        this.explosions = []
        this.explosionUpdateTime = -1
        this.explosionDisplayTime = explosionDisplayTime

        # Game assets
        this.moleImage = Deck.getAsset(deck,"Mole.jpeg")
        this.blankImage = Deck.getAsset(deck, "Blank.jpeg")
        this.explosionImage = Deck.getAsset(deck, "Explosion.jpeg")

        # Process management
        this.updateLock = threading.Lock()

        def keyCallback(deck, key, state):
            this.keyCallback(key,state)
        this.deck.set_key_callback(keyCallback)

        # Storyboard Management
        this.storyboard = "notstarted"

        this.redraw()

    def tick(this):
        this.update()
        this.redraw()
        if this.storyboard != "gameover":
            threading.Timer((randint(this.minDelay, this.maxDelay)/1000.0), this.tick).start()

    def randbutton(this):
        return randint(0, this.deck.key_count()-1)

    def start(this):
        # Mole positions are randomized in update()
        this.storyboard = "started"
        this.nextUpdateTime = -1 # Force initial update
        this.startTime = time()
        this.gameOverTime = this.startTime+(this.gameTime/1000)
        this.tick() # set everything in motion!

    def duration(this):
        return time()-this.startTime

    def update(this):
        if this.storyboard != "started":
            return

        t = time()
        # Check if any further updates are required
        if t>this.gameOverTime:
            this.storyboard = "gameover"
            return
        #elif t>this.nextUpdateTime:
        #    this.nextUpdateTime = t+(randint(this.minDelay, this.maxDelay)/1000.0)
        #else:
        #    return

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
            # Remove any covered explosions from the list
            try:
                this.explosions.remove(nextMole)
            except ValueError:
                pass

        this.hill = nextHill
        this.updateLock.release()
        this.redraw()

    def redraw(this):
        if this.storyboard == "notstarted":
            Deck.renderString(this.deck, " PRESS   KEY TO  START", background="black", color="white")
        elif this.storyboard == "gameover":
            Deck.renderString(this.deck, "GAME    OVER.   SCORE:  {}".format(this.score))
        else:
            for key in range(this.deck.key_count()):
                if key in this.hill:
                    image = this.moleImage
                elif key in this.explosions:
                    image = this.explosionImage
                else:
                    image = this.blankImage
                this.deck.set_key_image(key, image)


    def removeExplosion(this, key):
        this.updateLock.acquire()
        try:
            this.explosions.remove(key)
        except ValueError:
            pass
        this.updateLock.release()

    def keyCallback(this, key, state):
        if not state: 
            return
        if this.storyboard in ("gameover", "quit"):
            if key == 7:
                this.storyboard = "quit"
                deck.reset()
                deck.close()
            return
        elif this.storyboard == "notstarted":
            this.start()
        elif key in this.hill:
            this.updateLock.acquire()

            this.score += 1
            # Move the mole that was just whacked
            nextMole = this.randbutton()
            while nextMole in this.hill:
                nextMole = this.randbutton()
            this.hill.remove(key)
            this.hill.append(nextMole)

            # Display an explosion icon for some time
            this.explosions.append(key)
            this.updateLock.release()

            threading.Timer(this.explosionDisplayTime/1000.0, this.removeExplosion, args=(key,)).start()

            this.redraw()




if __name__ == "__main__":
    deck = Deck.getInitializedDeck(background="green");
    game = MoleGame(deck, gameTime=10000)
    print("Good luck!")
    while game.storyboard != "quit":
        #game.update()
        sleep(0.1)
    print("Score: " + str(game.score))




# Utility functions for manipulating the StreamDeck
#
# For documentation and other examples, see:
#   https://github.com/abcminiuser/python-elgato-streamdeck
# MIT license: see LICENSE file.
#

import os
from PIL import Image
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

def getAsset(deck, assetFilename):
    """ Load an image asset from the given filename. 
        Returned in the native format of `deck`
    """
    image = PILHelper.create_image(deck)

    # Resize the source image asset to best-fit the dimensions of a single key,
    # and paste it onto our blank frame centered as closely as possible.
    icon = Image.open(os.path.join(ASSETS_PATH, assetFilename)).convert("RGBA")
    icon.thumbnail((image.width, image.height - 20), Image.LANCZOS)
    icon_pos = ((image.width - icon.width) // 2, 0)
    image.paste(icon, icon_pos, icon)

    return PILHelper.to_native_format(deck, image)

def getInitializedDeck(initBrightness=30,deviceNum=0,background='black'):
    """ Initialize and return the first stream deck device or None. """
    streamdecks = DeviceManager().enumerate()
    if streamdecks and len(streamdecks)>=deviceNum+1:
        deck = streamdecks[deviceNum]
        deck.open()
        deck.reset()
        deck.set_brightness(initBrightness)

        # Blank background of provided color
        keyImage = PILHelper.to_native_format(deck, PILHelper.create_image(deck,background))
        for keyNum in range(deck.key_count()):
            deck.set_key_image(keyNum, keyImage)

        return deck
    print("Unable to open any stream deck devices.")
    return None


# I'm too lazy to bother with unit tests for this simple game.
# This should suffice for practical purposes.
if __name__ == "__main__":
    print("Performing sanity check:")
    print("    Initializing first stream deck with a red background and setting Mole image on first and last key.")
    print("    If this looks right, the test passed.")
    print("Press enter to exit.")
    deck = getInitializedDeck(background="red")
    moleImg = getAsset(deck, "Mole.jpeg")
    deck.set_key_image(0, moleImg)
    deck.set_key_image(deck.key_count()-1, moleImg)
    input()
    deck.reset()
    deck.close()



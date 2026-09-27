import os.path

__author__ = "Daniel Calderon"
__license__ = "MIT"

def getAssetPath(filename):

    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    parentFolderPath = os.path.dirname(thisFolderPath)
    assetsDirectory = os.path.join(parentFolderPath, "assets")
    requestedPath = os.path.join(assetsDirectory, filename)
    return requestedPath

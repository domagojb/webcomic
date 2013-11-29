#!/usr/bin/python

"""
    Requires python3 and higher.

    This module checks for new specified comics and loads them.
    Every comic is defined as a new object of the class ComicLoader.

    The class takes two main parameters:

        siteURL : The URL of the webcomic that is going to be loaded.
        pathImgURLexp : The URL regular expression which is used for
                        finding the comic image in the website data.

    These two parameters must be found "by hand", e.g. specified by the user.
    The image URL can be found by inspecting the comics site source code or by
    any other metod of inspecting the url. Some comics have already been included
    in the "mycomics.txt" file.

    The class downloads the data from the site of the comic, finds the image URL
    and compares it to the saved image URL(which is saved in a text file called
    by the webcomic). When they are different that means a new comic has been
    published and opens it.

    Trivial usage:

    comicObjectName = ComicLoader("siteURL", "pathImgURLexp")
    comicObjectName.load()

    e.g.:
    xkcd = ComicLoader("http://xkcd.com/", "http://imgs.xkcd.com/comics/\S+\.\w+")
    xkcd.load()

    The function "load" does everything for you. Checks for new comics and loads them.
"""

import urllib.request
import re
import webbrowser
import os

class ComicLoader:

    def __init__(self, siteURL, pathImgURLexp):
        """
            This method initializes the object.

            siteURL : The URL of the webcomic that is goind to be loaded
            pathImgURLexp : The URL path expression to the image of the comic which is used
                            for finding the comic image in the website data.
            filename : The file where the url of the latest loaded img is being saved.
        """

        self.siteURL = siteURL
        self.pathImgURLexp = pathImgURLexp
        self.filename = self.setFilename()

    def setFilename(self):
        """ Sets a filename by the name of the comic. """

        # Create the .webcomic directory in $HOME
        dir_path = os.environ["HOME"] + "/.webcomic"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        filename = re.search("w*\.*([\w-]+)\.", self.siteURL)
        return dir_path + "/" + filename.group(1)

    def getFilename(self):
        return self.filename

    def load(self):
        """
            Loads the comic and returns TRUE(1). Returns FALSE(0) if there is
            no new comic or ERROR(-1) if an error occured.
        """

        #If the comic has not been defined, load newest
        if not self.isDefined():
            # If an error had occured
            if self.loadNew() == -1:
                return (-1)
            self.saveNewURL()
            return 1 # Returns TRUE since a new comic has been published

        #else it checks if a new comic has been posted
        is_new = self.isNew()
        if is_new == 1:
            self.loadNew()
            self.saveNewURL()
            return 1 # Returns TRUE since a new comic has been published
        elif is_new == -1:
            return (-1)
        else:
            print("No new comic on " + self.siteURL)
            return 0 # Returns FALSE since no new comic has been published

    def isDefined(self):
        """
            Check wether the comic has already been defined/saved in the file.
            Returns TRUE(1) if yes, and FALSE(0) if no.
        """

        try:
            comicFile = open(self.filename, "r")
            comicsURL = comicFile.read()
            comicFile.close()
        except IOError:
            return 0 # File does not exist, comic isn't defined

        # Searches for the url
        foundURL = re.search(self.pathImgURLexp, comicsURL)
        if foundURL:
            return 1 # Comic defined in file
        else:
            return 0 # Comic not defined in file

    def getImgURL(self):
        """
            Finds the newest comic image and returns it.
            If it can't be found, returns ERROR(-1).
        """

        filename = os.environ["HOME"] + "/.webcomic/comicdata.txt"
        urllib.request.urlretrieve(self.siteURL, filename)
        dataFile = open(filename, "r")
        try:
            data = dataFile.read()
            dataFile.close()
        except:
            print("ERROR: Could not read data from file for " + self.siteURL)
            return (-1)

        #Find the image url in the data
        expression = self.pathImgURLexp
        imageURL = re.search(expression, data)
        #If it can't be found
        if not imageURL:
            print("No image for " + self.siteURL + " could be found" )
            return (-1)

        return imageURL.group()

    def getSavedURL(self):
        """
            Finds the saved image url and returns it.
            If there has been an error, returns -1.
        """

        try:
            comicFile = open(self.filename, "r")
            comicsURL = comicFile.read()
            comicFile.close()
        except IOError:
            print("No saved URL's found")
            return (-1)

        #Return the whole file since only the image url is saved
        return comicsURL

    def isNew(self):
        """
            Checks wether the published comic is newer than the saved one.
            Returns TRUE(1) if it is newer or FLASE(0) if not.
            If there has been an error returns -1.
        """

        dwnlImgURL = self.getImgURL() # The downloaded image url
        #If there has been an error
        if dwnlImgURL == -1:
            return (-1)

        savedImgURL = self.getSavedURL()
        #If there has been an error
        if savedImgURL == -1:
            return (-1)

        if savedImgURL == dwnlImgURL:
            return 0 # There has been no new comic published
        else:
            return 1 # A new comic has been published

    def loadNew(self):
        """
            Loads the newest published comic, opens it in the browser.
            Returns 1 if true or -1 if there has been an error.
        """

        #The downloaded image url
        dwnlImgURL = self.getImgURL()
        #If there has been an error
        if dwnlImgURL == -1:
            return (-1)

        print("Loading comic for " + self.siteURL)

        #Loads the comic in the browser
        webbrowser.open_new_tab(dwnlImgURL)

        return 1

    def saveNewURL(self):
        """
            Saves the newest image url into the file.
            Returns -1 if there has been an error or 1 if no error happened.
        """

        dwnlImgURL = self.getImgURL()
        #If there has been an error
        if dwnlImgURL == -1:
            return (-1)

        #Writes the url to the file
        comicFile = open(self.filename, "w")
        comicFile.write(dwnlImgURL)
        comicFile.close()

        return 1



"""
    The class HTMLCreator takes a list of comics and transforms them into a
    single html document. Each of the separate comics is a separate <div>
    with the class "commic".

        <div class="comic"><img src="<path to image>" /></div>

    To make a personal style, create a file names "webcomic.css" in "~/.webcomic/".

    How to use:
        - create ComicLoader type objects
        - parse them to a HTMLCreator object as a list
        - call loadHTML method

    example:

        xkcd            = ComicLoader("http://www.xkcd.com/",              "http://imgs.xkcd.com/comics/\S+\.\w+")
        explosm         = ComicLoader("http://www.explosm.net/comics/",    "http://www.explosm.net/db/files/Comics/\S+\.\w+")
        smbc            = ComicLoader("http://www.smbc-comics.com/",       "http://www.smbc-comics.com/comics/\d+\.\w+")

        test = HTMLcreator([xkcd, explosm, smbc])
        test.loadHTML()
"""

class HTMLcreator:

    def __init__(self, queue):
        self.queue = queue

        dir_path = os.environ["HOME"] + "/.webcomic"
        self.htmlfilename = (dir_path +
                            "/webcomic" +
                            self.hash(queue) +
                            ".html")

    def hash(self, key):
        """
            Returns a hash for the filename.
        """

        buff = ""
        for i in range(0, len(key)):
            buff = buff + key[i].getFilename()[len(key[i].getFilename()) - 1]

        return buff

    def newComics(self):
        """
            Returns a list of unread comics in queue.
        """

        newQueue = []
        for i in range(0, len(self.queue)):
            #If the comic has not been defined
            if not self.queue[i].isDefined():
                newQueue.append(self.queue[i])
                continue

            if self.queue[i].isNew() == 1:
                newQueue.append(self.queue[i])
            else:
                print("No new comic on " + self.queue[i].siteURL)

        return newQueue

    def createHTMLfile(self):
        """
            Creates the html file with the comics from queue.
        """

        htmlfile = open(self.htmlfilename, "w")

        htmlfile.write("<!DOCTYPE html>\n" +
                       "<html>\n" +
                       "<head>\n" +
                       "<link type=\"text/css\" rel=\"stylesheet\" href=\"stylesheets/webcomic.css\" />\n" +
                       "<title>Webcomic</title>\n" +
                       "</head>\n>" +
                       "<body>\n")

        for i in range(0, len(self.queue)):
            htmlfile.write("<div class=\"comic\"><img src=\"" +
                           str(self.queue[i].getImgURL()) +
                           "\"></div>\n")

        htmlfile.write("</body>\n" +
                       "</html>")

        htmlfile.close()

    def loadHTML(self):
        """
            Creates the HTML file out of the newest comics, and loads them.
        """

        #Get new comics and create html file
        self.queue = self.newComics()
        self.createHTMLfile()
        webbrowser.open_new_tab(self.htmlfilename)

        #Set all comics as read
        for i in range(0, len(self.queue)):
            self.queue[i].saveNewURL()



xkcd            = ComicLoader("http://www.xkcd.com/",              "http://imgs.xkcd.com/comics/\S+\.\w+")
explosm         = ComicLoader("http://www.explosm.net/comics/",    "http://www.explosm.net/db/files/Comics/\S+\.\w+")
darklegacycomicscy = ComicLoader("http://www.darklegacycomics.com/",  "http://darklegacycomics.com/\d+\.\w+")
smbc            = ComicLoader("http://www.smbc-comics.com/",       "http://www.smbc-comics.com/comics/\d+\.\w+")
pennyarcade     = ComicLoader("http://www.penny-arcade.com/comic", "http://art.penny-arcade.com/photos/.+.jpg")
licd            = ComicLoader("http://www.leasticoulddo.com/",     "http://cdn.leasticoulddo.com/comics/\d+\.\w+")
dinosaurcomics  = ComicLoader("http://www.qwantz.com/index.php",   "http://www.qwantz.com/comics/\S+\.\w+")
doghousediaries = ComicLoader("http://www.thedoghousediaries.com", "http://thedoghousediaries.com/comics/uncategorized/.+.png")
buttersafe      = ComicLoader("http://buttersafe.com/",            "http://buttersafe.com/comics/.+.jpg")

test = HTMLcreator([xkcd, explosm, smbc])
test.loadHTML()

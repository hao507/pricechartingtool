#!/usr/bin/env python3
##############################################################################
# Description:
#
#   Adds various sets of artifacts to the Soybeans chart.
#
##############################################################################

import copy

# For logging.
import logging

# For timestamps and timezone information.
import datetime
import pytz

# For PyQt UI classes.
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Include some PriceChartingTool modules.
from ephemeris import Ephemeris
from data_objects import *
from pricebarchart import PriceBarChartGraphicsScene
from astrologychart import AstrologyUtils

##############################################################################
# Global variables
##############################################################################

# For logging.
#logLevel = logging.DEBUG
logLevel = logging.INFO
logging.basicConfig(format='%(levelname)s: %(message)s')
moduleName = globals()['__name__']
log = logging.getLogger(moduleName)
log.setLevel(logLevel)

# Default for the maximum time difference between the exact planetary
# combination timestamp, and the one calculated.  This would define
# the accuracy of the calculations.  This is a datetime.timedelta object.
#
#defaultMaxErrorJd = datetime.timedelta(hours=1)

##############################################################################

class PlanetaryCombinationsLibrary:
    """Class that holds several static functions to create
    PriceBarChartArtifacts that represent various planetary
    combinations.
    """

    scene = PriceBarChartGraphicsScene()
    
    @staticmethod
    def addVerticalLine(pcdd, dt, highPrice, lowPrice, tag, color):
        """Adds a vertical line at the given timestamp, from highPrice
        to lowPrice, with the given tag and color.

        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        dt        - datetime.datetime object for timestamp
                    of the vertical line.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        tag       - str value for the tag to add to the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        """

        # Create the artifact at the timestamp.
        log.debug("Creating line artifact at: {} ...".\
                  format(Ephemeris.datetimeToStr(dt)))
        
        lineX = \
            PlanetaryCombinationsLibrary.scene.datetimeToSceneXPos(dt)
        lineLowY = \
            PlanetaryCombinationsLibrary.scene.priceToSceneYPos(lowPrice)
        lineHighY = \
            PlanetaryCombinationsLibrary.scene.priceToSceneYPos(highPrice)
        
        lineArtifact = PriceBarChartLineSegmentArtifact()
        lineArtifact.addTag(tag)
        lineArtifact.setTiltedTextFlag(False)
        lineArtifact.setAngleTextFlag(False)
        lineArtifact.setColor(color)
        lineArtifact.setStartPointF(QPointF(lineX, lineLowY))
        lineArtifact.setEndPointF(QPointF(lineX, lineHighY))
        
        # Append the artifact.
        log.info("Adding '{}' line artifact at: {} (jd == {}) ...".\
                 format(tag,
                        Ephemeris.datetimeToStr(dt),
                        Ephemeris.datetimeToJulianDay(dt)))
        pcdd.priceBarChartArtifacts.append(lineArtifact)

        
    @staticmethod
    def addHelioVenusJupiter120xVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Venus and Jupiter are multiples of 120
        degrees apart, heliocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of green will be used for 0 deg, 120 deg, and 240 deg.
        color1 = QColor(0x008020)
        color2 = QColor(0x00A040)
        color3 = QColor(0x00C060)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=4)

        # Differencial multiple we are looking for, in degrees.
        #
        # Note, the below algorithm assumes that 360 is evenly
        # divisible by 'desiredDiffMultiple'.  Otherwise it will
        # not catch all cases (e.g. if we are looking for 14
        # degree multiples, it will catch if the diffDeg is 14,
        # but not if the diffDeg is -14).
        desiredDiffMultiple = 120.0

        # Count of artifacts added.
        numArtifactsAdded = 0
        
        # Iterate through, creating artfacts and adding them as we go.
        prevDt = copy.deepcopy(startDt)
        currDt = copy.deepcopy(startDt)

        prevDiff = None
        currDiff = None
        
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while currDt < endDt:
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getVenusPlanetaryInfo(currDt)
            p2 = Ephemeris.getJupiterPlanetaryInfo(currDt)

            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.heliocentric['sidereal']['longitude']))
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.heliocentric['sidereal']['longitude']))

            diffDeg = \
                p1.heliocentric['sidereal']['longitude'] - \
                p2.heliocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0

            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg % desiredDiffMultiple

            if prevDiff == None:
                prevDiff = currDiff

            log.debug("prevDiff == {}".format(prevDiff))
            log.debug("currDiff == {}".format(currDiff))
            
            # If the currDiff modulus (remainder of the division) is
            # less the prevDiff modulus, that means between the
            # previous timestamp and the current one, we passed the
            # point of exact.  We need to now narrow the point down to
            # within the 'maxErrorTd' datetime.timedelta.
            if currDiff < prevDiff:
                log.debug("Crossed over!")
                
                # This is the upper-bound of the error timedelta.
                t1 = prevDt
                t2 = currDt
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getVenusPlanetaryInfo(testDt)
                    p2 = Ephemeris.getJupiterPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.heliocentric['sidereal']['longitude'] - \
                            p2.heliocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0

                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < currDiff:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        currDt = t2
                        currDiff = testDiff
                    else:
                        t1 = testDt
                        
                    currErrorTd = t2 - t1

                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 120:
                        color = color2
                    elif round(abs(diffDeg)) == 240:
                        color = color3
                    else:
                        color = color1
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            # Update prevDiff as the currDiff.
            prevDiff = currDiff
                
            # Increment currDt.
            prevDt = copy.deepcopy(currDt)
            currDt += stepSizeTd

        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv

    @staticmethod
    def addHelioMars150NeptuneVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Mars aspects Neptune at 150 degrees,
        heliocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of green will be used for 0 deg, 120 deg, and 240 deg.
        if color == None:
            color = QColor(Qt.darkMagenta)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=4)

        # Desired differential.
        desiredDiff = 150

        # Count of artifacts added.
        numArtifactsAdded = 0
        
        # Iterate through, creating artfacts and adding them as we go.
        prevDt = copy.deepcopy(startDt)
        currDt = copy.deepcopy(startDt)

        prevDiff = None
        currDiff = None
        
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while currDt < endDt:
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getNeptunePlanetaryInfo(currDt)
            p2 = Ephemeris.getMarsPlanetaryInfo(currDt)
            
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.heliocentric['sidereal']['longitude']))
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.heliocentric['sidereal']['longitude']))
            
            diffDeg = \
                p1.heliocentric['sidereal']['longitude'] - \
                p2.heliocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0

            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg
            
            if prevDiff == None:
                prevDiff = currDiff
            
            log.debug("prevDiff == {}".format(prevDiff))
            log.debug("currDiff == {}".format(currDiff))
            
            if prevDiff > desiredDiff and currDiff < desiredDiff:
                log.debug("Crossed over!")
                
                # This is the upper-bound of the error timedelta.
                t1 = prevDt
                t2 = currDt
                currErrorTd = t2 - t1
                
                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getNeptunePlanetaryInfo(testDt)
                    p2 = Ephemeris.getMarsPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.heliocentric['sidereal']['longitude'] - \
                            p2.heliocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0

                    if diffDeg > desiredDiff:
                        t1 = testDt
                    else:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        currDt = t2
                        currDiff = diffDeg
                        
                    currErrorTd = t2 - t1

                log.debug("diffDeg == {}".format(diffDeg))
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                
                numArtifactsAdded += 1
                
            # Update prevDiff as the currDiff.
            prevDiff = currDiff
                
            # Increment currDt.
            prevDt = copy.deepcopy(currDt)
            currDt += stepSizeTd

        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv


    @staticmethod
    def addHelioNeptune150MarsVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Neptune aspects Mars at 150 degrees,
        heliocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of green will be used for 0 deg, 120 deg, and 240 deg.
        if color == None:
            color = QColor(Qt.magenta)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=4)

        # Desired differential.
        desiredDiff = 150

        # Count of artifacts added.
        numArtifactsAdded = 0
        
        # Iterate through, creating artfacts and adding them as we go.
        prevDt = copy.deepcopy(startDt)
        currDt = copy.deepcopy(startDt)

        prevDiff = None
        currDiff = None
        
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while currDt < endDt:
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getMarsPlanetaryInfo(currDt)
            p2 = Ephemeris.getNeptunePlanetaryInfo(currDt)
            
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.heliocentric['sidereal']['longitude']))
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.heliocentric['sidereal']['longitude']))
            
            diffDeg = \
                p1.heliocentric['sidereal']['longitude'] - \
                p2.heliocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0

            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg
            
            if prevDiff == None:
                prevDiff = currDiff
            
            log.debug("prevDiff == {}".format(prevDiff))
            log.debug("currDiff == {}".format(currDiff))
            
            if prevDiff < desiredDiff and currDiff > desiredDiff:
                log.debug("Crossed over!")
                
                # This is the upper-bound of the error timedelta.
                t1 = prevDt
                t2 = currDt
                currErrorTd = t2 - t1
                
                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getNeptunePlanetaryInfo(testDt)
                    p2 = Ephemeris.getMarsPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.heliocentric['sidereal']['longitude'] - \
                            p2.heliocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0

                    if diffDeg < desiredDiff:
                        t1 = testDt
                    else:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        currDt = t2
                        currDiff = diffDeg
                        
                    currErrorTd = t2 - t1

                log.debug("diffDeg == {}".format(diffDeg))
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                
                numArtifactsAdded += 1
                
            # Update prevDiff as the currDiff.
            prevDiff = currDiff
                
            # Increment currDt.
            prevDt = copy.deepcopy(currDt)
            currDt += stepSizeTd

        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv

    @staticmethod
    def addHelioVenus150NeptuneVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Venus aspects Neptune at 150 degrees,
        heliocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of green will be used for 0 deg, 120 deg, and 240 deg.
        if color == None:
            color = QColor(Qt.darkYellow)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=4)

        # Desired differential.
        desiredDiff = 150

        # Count of artifacts added.
        numArtifactsAdded = 0
        
        # Iterate through, creating artfacts and adding them as we go.
        prevDt = copy.deepcopy(startDt)
        currDt = copy.deepcopy(startDt)

        prevDiff = None
        currDiff = None
        
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while currDt < endDt:
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getNeptunePlanetaryInfo(currDt)
            p2 = Ephemeris.getVenusPlanetaryInfo(currDt)
            
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.heliocentric['sidereal']['longitude']))
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.heliocentric['sidereal']['longitude']))
            
            diffDeg = \
                p1.heliocentric['sidereal']['longitude'] - \
                p2.heliocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0

            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg
            
            if prevDiff == None:
                prevDiff = currDiff
            
            log.debug("prevDiff == {}".format(prevDiff))
            log.debug("currDiff == {}".format(currDiff))
            
            if prevDiff > desiredDiff and currDiff < desiredDiff:
                log.debug("Crossed over!")
                
                # This is the upper-bound of the error timedelta.
                t1 = prevDt
                t2 = currDt
                currErrorTd = t2 - t1
                
                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getNeptunePlanetaryInfo(testDt)
                    p2 = Ephemeris.getVenusPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.heliocentric['sidereal']['longitude'] - \
                            p2.heliocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0

                    if diffDeg > desiredDiff:
                        t1 = testDt
                    else:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        currDt = t2
                        currDiff = diffDeg
                        
                    currErrorTd = t2 - t1

                log.debug("diffDeg == {}".format(diffDeg))
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                
                numArtifactsAdded += 1
                
            # Update prevDiff as the currDiff.
            prevDiff = currDiff
                
            # Increment currDt.
            prevDt = copy.deepcopy(currDt)
            currDt += stepSizeTd

        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv


    @staticmethod
    def addHelioNeptune150VenusVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Neptune aspects Venus at 150 degrees,
        heliocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of green will be used for 0 deg, 120 deg, and 240 deg.
        if color == None:
            color = QColor(Qt.yellow)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=4)

        # Desired differential.
        desiredDiff = 150

        # Count of artifacts added.
        numArtifactsAdded = 0
        
        # Iterate through, creating artfacts and adding them as we go.
        prevDt = copy.deepcopy(startDt)
        currDt = copy.deepcopy(startDt)

        prevDiff = None
        currDiff = None
        
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while currDt < endDt:
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getVenusPlanetaryInfo(currDt)
            p2 = Ephemeris.getNeptunePlanetaryInfo(currDt)
            
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.heliocentric['sidereal']['longitude']))
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.heliocentric['sidereal']['longitude']))
            
            diffDeg = \
                p1.heliocentric['sidereal']['longitude'] - \
                p2.heliocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0

            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg
            
            if prevDiff == None:
                prevDiff = currDiff
            
            log.debug("prevDiff == {}".format(prevDiff))
            log.debug("currDiff == {}".format(currDiff))
            
            if prevDiff < desiredDiff and currDiff > desiredDiff:
                log.debug("Crossed over!")
                
                # This is the upper-bound of the error timedelta.
                t1 = prevDt
                t2 = currDt
                currErrorTd = t2 - t1
                
                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getNeptunePlanetaryInfo(testDt)
                    p2 = Ephemeris.getVenusPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.heliocentric['sidereal']['longitude'] - \
                            p2.heliocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0

                    if diffDeg < desiredDiff:
                        t1 = testDt
                    else:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        currDt = t2
                        currDiff = diffDeg
                        
                    currErrorTd = t2 - t1

                log.debug("diffDeg == {}".format(diffDeg))
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                
                numArtifactsAdded += 1
                
            # Update prevDiff as the currDiff.
            prevDiff = currDiff
                
            # Increment currDt.
            prevDt = copy.deepcopy(currDt)
            currDt += stepSizeTd

        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv

    @staticmethod
    def addGeoVenusSaturn120xVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Venus and Saturn are multiples of 120
        degrees apart, geocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of red will be used for 0 deg, 120 deg, and 240 deg.
        color1 = QColor(0xFF0000)
        color2 = QColor(0xFC0000)
        color3 = QColor(0xFA0000)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=1)

        # Differencial multiple we are looking for, in degrees.
        #
        # Note, the below algorithm assumes that 360 is evenly
        # divisible by 'desiredDiffMultiple'.  Otherwise it will
        # not catch all cases (e.g. if we are looking for 14
        # degree multiples, it will catch if the diffDeg is 14,
        # but not if the diffDeg is -14).
        desiredDiffMultiple = 120.0
        
        # Parameter for a test to show that it actually crossed over
        # the boundary of the degree differential multiple.
        crossoverRequirement = (2/3) * desiredDiffMultiple
        
        # Count of artifacts added.
        numArtifactsAdded = 0
        
        steps = []
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        
        diffs = []
        diffs.append(None)
        diffs.append(None)
        diffs.append(None)
        
        # Iterate through, creating artfacts and adding them as we go.
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while steps[2] < endDt:
            
            currDt = steps[2]
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getVenusPlanetaryInfo(currDt)
            p2 = Ephemeris.getSaturnPlanetaryInfo(currDt)

            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.geocentric['sidereal']['longitude']))
            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.geocentric['sidereal']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p1.name,
            #                 p1.geocentric['tropical']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p2.name,
            #                 p2.geocentric['tropical']['longitude']))
            
            
            diffDeg = \
                p1.geocentric['sidereal']['longitude'] - \
                p2.geocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0
                
            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg % desiredDiffMultiple
            
            if diffs[0] == None:
                diffs[0] = currDiff
            if diffs[1] == None:
                diffs[1] = currDiff
            diffs[2] = currDiff
            
            log.debug("steps[0] == {}".format(steps[0]))
            log.debug("steps[1] == {}".format(steps[1]))
            log.debug("steps[2] == {}".format(steps[2]))
            
            log.debug("diffs[0] == {}".format(diffs[0]))
            log.debug("diffs[1] == {}".format(diffs[1]))
            log.debug("diffs[2] == {}".format(diffs[2]))

            if diffs[2] < diffs[0] and \
                   diffs[2] < diffs[1] and \
                   (diffs[1] - diffs[2] > crossoverRequirement):
                
                # Crossed over to above 0 while increasing over
                # 'desiredDiffMultiple'.  This happens when planets
                # are moving in direct motion.
                log.debug("Crossed over to above 0 while increasing over {}".\
                          format(desiredDiffMultiple))

                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getVenusPlanetaryInfo(testDt)
                    p2 = Ephemeris.getSaturnPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[2]:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                    else:
                        t1 = testDt
                        
                    currErrorTd = t2 - t1

                currDt = steps[2]
                
                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 120:
                        color = color2
                    elif round(abs(diffDeg)) == 240:
                        color = color3
                    else:
                        color = color1
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            elif diffs[2] > diffs[1] and \
                     diffs[2] > diffs[0] and \
                     (diffs[2] - diffs[1] > crossoverRequirement):
                
                # Crossed over to under 'desiredDiffMultiple' while
                # decreasing under 0.  This can happen when planets
                # are moving in retrograde motion.
                log.debug("Crossed over to under {} while decreasing under 0".\
                          format(desiredDiffMultiple))
                
                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getVenusPlanetaryInfo(testDt)
                    p2 = Ephemeris.getSaturnPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[1]:
                        t1 = testDt
                    else:
                        t2 = testDt
                        
                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                        
                    currErrorTd = t2 - t1
                    
                currDt = steps[2]
                
                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 120:
                        color = color2
                    elif round(abs(diffDeg)) == 240:
                        color = color3
                    else:
                        color = color1
                        
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            # Prepare for the next iteration.
            steps.append(copy.deepcopy(steps[-1]) + stepSizeTd)
            del steps[0]
            diffs.append(diffs[-1])
            del diffs[0]
            
        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv

    @staticmethod
    def addGeoMarsJupiter30xVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Mars and Jupiter are multiples of 30
        degrees apart, geocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of blue will be used.
        color1 = QColor(0x000080)
        color2 = QColor(0x00008F)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=1)

        # Differencial multiple we are looking for, in degrees.
        #
        # Note, the below algorithm assumes that 360 is evenly
        # divisible by 'desiredDiffMultiple'.  Otherwise it will
        # not catch all cases (e.g. if we are looking for 14
        # degree multiples, it will catch if the diffDeg is 14,
        # but not if the diffDeg is -14).
        desiredDiffMultiple = 30.0
        
        # Parameter for a test to show that it actually crossed over
        # the boundary of the degree differential multiple.
        crossoverRequirement = (2/3) * desiredDiffMultiple
        
        # Count of artifacts added.
        numArtifactsAdded = 0
        
        steps = []
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        
        diffs = []
        diffs.append(None)
        diffs.append(None)
        diffs.append(None)
        
        # Iterate through, creating artfacts and adding them as we go.
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while steps[2] < endDt:
            
            currDt = steps[2]
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getMarsPlanetaryInfo(currDt)
            p2 = Ephemeris.getJupiterPlanetaryInfo(currDt)

            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.geocentric['sidereal']['longitude']))
            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.geocentric['sidereal']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p1.name,
            #                 p1.geocentric['tropical']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p2.name,
            #                 p2.geocentric['tropical']['longitude']))
            
            
            diffDeg = \
                p1.geocentric['sidereal']['longitude'] - \
                p2.geocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0
                
            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg % desiredDiffMultiple
            
            if diffs[0] == None:
                diffs[0] = currDiff
            if diffs[1] == None:
                diffs[1] = currDiff
            diffs[2] = currDiff
            
            log.debug("steps[0] == {}".format(steps[0]))
            log.debug("steps[1] == {}".format(steps[1]))
            log.debug("steps[2] == {}".format(steps[2]))
            
            log.debug("diffs[0] == {}".format(diffs[0]))
            log.debug("diffs[1] == {}".format(diffs[1]))
            log.debug("diffs[2] == {}".format(diffs[2]))

            if diffs[2] < diffs[0] and \
                   diffs[2] < diffs[1] and \
                   (diffs[1] - diffs[2] > crossoverRequirement):
                
                # Crossed over to above 0 while increasing over
                # 'desiredDiffMultiple'.  This happens when planets
                # are moving in direct motion.
                log.debug("Crossed over to above 0 while increasing over {}".\
                          format(desiredDiffMultiple))

                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getMarsPlanetaryInfo(testDt)
                    p2 = Ephemeris.getJupiterPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[2]:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                    else:
                        t1 = testDt
                        
                    currErrorTd = t2 - t1

                currDt = steps[2]
                
                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 0 or round(abs(diffDeg)) == 360:
                        color = color1
                    else:
                        color = color2
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            elif diffs[2] > diffs[1] and \
                     diffs[2] > diffs[0] and \
                     (diffs[2] - diffs[1] > crossoverRequirement):
                
                # Crossed over to under 'desiredDiffMultiple' while
                # decreasing under 0.  This can happen when planets
                # are moving in retrograde motion.
                log.debug("Crossed over to under {} while decreasing under 0".\
                          format(desiredDiffMultiple))
                
                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getMarsPlanetaryInfo(testDt)
                    p2 = Ephemeris.getJupiterPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[1]:
                        t1 = testDt
                    else:
                        t2 = testDt
                        
                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                        
                    currErrorTd = t2 - t1
                    
                currDt = steps[2]
                
                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 0 or round(abs(diffDeg)) == 360:
                        color = color1
                    else:
                        color = color2
                        
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            # Prepare for the next iteration.
            steps.append(copy.deepcopy(steps[-1]) + stepSizeTd)
            del steps[0]
            diffs.append(diffs[-1])
            del diffs[0]
            
        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv

    @staticmethod
    def addGeoMarsSaturn120xVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Mars and Saturn are multiples of 120
        degrees apart, geocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of gray will be used for 0 deg, 120 deg, and 240 deg.
        color1 = QColor(0x808080)
        color2 = QColor(0xA0A0A4)
        color3 = QColor(0xA0A0A4)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=1)

        # Differencial multiple we are looking for, in degrees.
        #
        # Note, the below algorithm assumes that 360 is evenly
        # divisible by 'desiredDiffMultiple'.  Otherwise it will
        # not catch all cases (e.g. if we are looking for 14
        # degree multiples, it will catch if the diffDeg is 14,
        # but not if the diffDeg is -14).
        desiredDiffMultiple = 120.0
        
        # Parameter for a test to show that it actually crossed over
        # the boundary of the degree differential multiple.
        crossoverRequirement = (2/3) * desiredDiffMultiple
        
        # Count of artifacts added.
        numArtifactsAdded = 0
        
        steps = []
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        
        diffs = []
        diffs.append(None)
        diffs.append(None)
        diffs.append(None)
        
        # Iterate through, creating artfacts and adding them as we go.
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while steps[2] < endDt:
            
            currDt = steps[2]
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getMarsPlanetaryInfo(currDt)
            p2 = Ephemeris.getSaturnPlanetaryInfo(currDt)

            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.geocentric['sidereal']['longitude']))
            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.geocentric['sidereal']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p1.name,
            #                 p1.geocentric['tropical']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p2.name,
            #                 p2.geocentric['tropical']['longitude']))
            
            
            diffDeg = \
                p1.geocentric['sidereal']['longitude'] - \
                p2.geocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0
                
            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg % desiredDiffMultiple
            
            if diffs[0] == None:
                diffs[0] = currDiff
            if diffs[1] == None:
                diffs[1] = currDiff
            diffs[2] = currDiff
            
            log.debug("steps[0] == {}".format(steps[0]))
            log.debug("steps[1] == {}".format(steps[1]))
            log.debug("steps[2] == {}".format(steps[2]))
            
            log.debug("diffs[0] == {}".format(diffs[0]))
            log.debug("diffs[1] == {}".format(diffs[1]))
            log.debug("diffs[2] == {}".format(diffs[2]))

            if diffs[2] < diffs[0] and \
                   diffs[2] < diffs[1] and \
                   (diffs[1] - diffs[2] > crossoverRequirement):
                
                # Crossed over to above 0 while increasing over
                # 'desiredDiffMultiple'.  This happens when planets
                # are moving in direct motion.
                log.debug("Crossed over to above 0 while increasing over {}".\
                          format(desiredDiffMultiple))

                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getMarsPlanetaryInfo(testDt)
                    p2 = Ephemeris.getSaturnPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[2]:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                    else:
                        t1 = testDt
                        
                    currErrorTd = t2 - t1

                currDt = steps[2]
                
                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 120:
                        color = color2
                    elif round(abs(diffDeg)) == 240:
                        color = color3
                    else:
                        color = color1
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            elif diffs[2] > diffs[1] and \
                     diffs[2] > diffs[0] and \
                     (diffs[2] - diffs[1] > crossoverRequirement):
                
                # Crossed over to under 'desiredDiffMultiple' while
                # decreasing under 0.  This can happen when planets
                # are moving in retrograde motion.
                log.debug("Crossed over to under {} while decreasing under 0".\
                          format(desiredDiffMultiple))
                
                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getMarsPlanetaryInfo(testDt)
                    p2 = Ephemeris.getSaturnPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[1]:
                        t1 = testDt
                    else:
                        t2 = testDt
                        
                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                        
                    currErrorTd = t2 - t1
                    
                currDt = steps[2]
                
                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 120:
                        color = color2
                    elif round(abs(diffDeg)) == 240:
                        color = color3
                    else:
                        color = color1
                        
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            # Prepare for the next iteration.
            steps.append(copy.deepcopy(steps[-1]) + stepSizeTd)
            del steps[0]
            diffs.append(diffs[-1])
            del diffs[0]
            
        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv

    @staticmethod
    def addGeoMercuryJupiter90xVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Mercury and Jupiter are multiples of 90
        degrees apart, geocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # If color was not explicitly defined, then the following
        # shades of cyan will be used for 0, and 90, 180, 270 deg.
        color1 = QColor(0x008080)
        color2 = QColor(0x00A0A4)
        
        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=1)

        # Differencial multiple we are looking for, in degrees.
        #
        # Note, the below algorithm assumes that 360 is evenly
        # divisible by 'desiredDiffMultiple'.  Otherwise it will
        # not catch all cases (e.g. if we are looking for 14
        # degree multiples, it will catch if the diffDeg is 14,
        # but not if the diffDeg is -14).
        desiredDiffMultiple = 90.0
        
        # Parameter for a test to show that it actually crossed over
        # the boundary of the degree differential multiple.
        crossoverRequirement = (2/3) * desiredDiffMultiple
        
        # Count of artifacts added.
        numArtifactsAdded = 0
        
        steps = []
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        
        diffs = []
        diffs.append(None)
        diffs.append(None)
        diffs.append(None)
        
        # Iterate through, creating artfacts and adding them as we go.
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while steps[2] < endDt:
            
            currDt = steps[2]
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getMercuryPlanetaryInfo(currDt)
            p2 = Ephemeris.getJupiterPlanetaryInfo(currDt)

            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.geocentric['sidereal']['longitude']))
            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.geocentric['sidereal']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p1.name,
            #                 p1.geocentric['tropical']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p2.name,
            #                 p2.geocentric['tropical']['longitude']))
            
            
            diffDeg = \
                p1.geocentric['sidereal']['longitude'] - \
                p2.geocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0
                
            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg % desiredDiffMultiple
            
            if diffs[0] == None:
                diffs[0] = currDiff
            if diffs[1] == None:
                diffs[1] = currDiff
            diffs[2] = currDiff
            
            log.debug("steps[0] == {}".format(steps[0]))
            log.debug("steps[1] == {}".format(steps[1]))
            log.debug("steps[2] == {}".format(steps[2]))
            
            log.debug("diffs[0] == {}".format(diffs[0]))
            log.debug("diffs[1] == {}".format(diffs[1]))
            log.debug("diffs[2] == {}".format(diffs[2]))

            if diffs[2] < diffs[0] and \
                   diffs[2] < diffs[1] and \
                   (diffs[1] - diffs[2] > crossoverRequirement):
                
                # Crossed over to above 0 while increasing over
                # 'desiredDiffMultiple'.  This happens when planets
                # are moving in direct motion.
                log.debug("Crossed over to above 0 while increasing over {}".\
                          format(desiredDiffMultiple))

                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getMercuryPlanetaryInfo(testDt)
                    p2 = Ephemeris.getJupiterPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[2]:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                    else:
                        t1 = testDt
                        
                    currErrorTd = t2 - t1

                currDt = steps[2]
                
                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 0 or round(abs(diffDeg)) == 360:
                        color = color1
                    else:
                        color = color2
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            elif diffs[2] > diffs[1] and \
                     diffs[2] > diffs[0] and \
                     (diffs[2] - diffs[1] > crossoverRequirement):
                
                # Crossed over to under 'desiredDiffMultiple' while
                # decreasing under 0.  This can happen when planets
                # are moving in retrograde motion.
                log.debug("Crossed over to under {} while decreasing under 0".\
                          format(desiredDiffMultiple))
                
                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getMercuryPlanetaryInfo(testDt)
                    p2 = Ephemeris.getJupiterPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[1]:
                        t1 = testDt
                    else:
                        t2 = testDt
                        
                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                        
                    currErrorTd = t2 - t1
                    
                currDt = steps[2]
                
                log.debug("diffDeg == {}".format(diffDeg))
                usingDefaultColors = False
                if color == None:
                    usingDefaultColors = True
                    if round(abs(diffDeg)) == 0 or round(abs(diffDeg)) == 360:
                        color = color1
                    else:
                        color = color2
                        
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                if usingDefaultColors == True:
                    color = None
                numArtifactsAdded += 1
                
            # Prepare for the next iteration.
            steps.append(copy.deepcopy(steps[-1]) + stepSizeTd)
            del steps[0]
            diffs.append(diffs[-1])
            del diffs[0]
            
        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv

    @staticmethod
    def addHelioSaturnUranus15xVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Saturn and Uranus are multiples of 15
        degrees apart, heliocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # Set the color if it is not already set to something.
        if color == None:
            color = QColor(Qt.red)

        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=4)

        # Differencial multiple we are looking for, in degrees.
        #
        # Note, the below algorithm assumes that 360 is evenly
        # divisible by 'desiredDiffMultiple'.  Otherwise it will
        # not catch all cases (e.g. if we are looking for 14
        # degree multiples, it will catch if the diffDeg is 14,
        # but not if the diffDeg is -14).
        desiredDiffMultiple = 15.0

        # Count of artifacts added.
        numArtifactsAdded = 0
        
        # Iterate through, creating artfacts and adding them as we go.
        prevDt = copy.deepcopy(startDt)
        currDt = copy.deepcopy(startDt)

        prevDiff = None
        currDiff = None
        
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while currDt < endDt:
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getSaturnPlanetaryInfo(currDt)
            p2 = Ephemeris.getUranusPlanetaryInfo(currDt)

            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.heliocentric['sidereal']['longitude']))
            log.debug("{} heliocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.heliocentric['sidereal']['longitude']))

            diffDeg = \
                p1.heliocentric['sidereal']['longitude'] - \
                p2.heliocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0

            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg % desiredDiffMultiple

            if prevDiff == None:
                prevDiff = currDiff

            log.debug("prevDiff == {}".format(prevDiff))
            log.debug("currDiff == {}".format(currDiff))
            
            # If the currDiff modulus (remainder of the division) is
            # less the prevDiff modulus, that means between the
            # previous timestamp and the current one, we passed the
            # point of exact.  We need to now narrow the point down to
            # within the 'maxErrorTd' datetime.timedelta.
            if currDiff < prevDiff:
                log.debug("Crossed over!")
                
                # This is the upper-bound of the error timedelta.
                t1 = prevDt
                t2 = currDt
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getSaturnPlanetaryInfo(testDt)
                    p2 = Ephemeris.getUranusPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.heliocentric['sidereal']['longitude'] - \
                            p2.heliocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0

                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < currDiff:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        currDt = t2
                        currDiff = testDiff
                    else:
                        t1 = testDt
                        
                    currErrorTd = t2 - t1
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                numArtifactsAdded += 1
                
            # Update prevDiff as the currDiff.
            prevDiff = currDiff
                
            # Increment currDt.
            prevDt = copy.deepcopy(currDt)
            currDt += stepSizeTd

        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv


    @staticmethod
    def addGeoSaturnUranus15xVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where Saturn and Uranus are multiples of 15
        degrees apart, geocentrically.
        
        Note: Default tag used for the artifacts added is the name of this
        function, without the word 'add' at the beginning.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """


        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # Set the color if it is not already set to something.
        if color == None:
            color = QColor(Qt.darkYellow)

        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Set the step size.
        stepSizeTd = datetime.timedelta(days=1)

        # Differencial multiple we are looking for, in degrees.
        #
        # Note, the below algorithm assumes that 360 is evenly
        # divisible by 'desiredDiffMultiple'.  Otherwise it will
        # not catch all cases (e.g. if we are looking for 14
        # degree multiples, it will catch if the diffDeg is 14,
        # but not if the diffDeg is -14).
        desiredDiffMultiple = 15.0

        # Parameter for a test to show that it actually crossed over
        # the boundary of the degree differential multiple.
        crossoverRequirement = (2/3) * desiredDiffMultiple
        
        # Count of artifacts added.
        numArtifactsAdded = 0
        
        steps = []
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))
        steps.append(copy.deepcopy(startDt))

        diffs = []
        diffs.append(None)
        diffs.append(None)
        diffs.append(None)
        
        # Iterate through, creating artfacts and adding them as we go.
        log.debug("Stepping through timestamps from {} to {} ...".\
                  format(Ephemeris.datetimeToStr(startDt),
                         Ephemeris.datetimeToStr(endDt)))
        
        while steps[2] < endDt:
            
            currDt = steps[2]
            log.debug("Looking at currDt == {} ...".\
                      format(Ephemeris.datetimeToStr(currDt)))
            
            p1 = Ephemeris.getSaturnPlanetaryInfo(currDt)
            p2 = Ephemeris.getUranusPlanetaryInfo(currDt)

            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p1.name,
                             p1.geocentric['sidereal']['longitude']))
            log.debug("{} geocentric sidereal longitude is: {}".\
                      format(p2.name,
                             p2.geocentric['sidereal']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p1.name,
            #                 p1.geocentric['tropical']['longitude']))
            #log.debug("{} geocentric tropical longitude is: {}".\
            #          format(p2.name,
            #                 p2.geocentric['tropical']['longitude']))
            
            
            diffDeg = \
                p1.geocentric['sidereal']['longitude'] - \
                p2.geocentric['sidereal']['longitude']
            if diffDeg < 0:
                diffDeg += 360.0
                
            log.debug("diffDeg == {}".format(diffDeg))
            
            currDiff = diffDeg % desiredDiffMultiple
            
            if diffs[0] == None:
                diffs[0] = currDiff
            if diffs[1] == None:
                diffs[1] = currDiff
            diffs[2] = currDiff
            
            log.debug("steps[0] == {}".format(steps[0]))
            log.debug("steps[1] == {}".format(steps[1]))
            log.debug("steps[2] == {}".format(steps[2]))
            
            log.debug("diffs[0] == {}".format(diffs[0]))
            log.debug("diffs[1] == {}".format(diffs[1]))
            log.debug("diffs[2] == {}".format(diffs[2]))

            if diffs[2] < diffs[0] and \
                   diffs[2] < diffs[1] and \
                   (diffs[1] - diffs[2] > crossoverRequirement):
                
                # Crossed over to above 0 while increasing over
                # 'desiredDiffMultiple'.  This happens when planets
                # are moving in direct motion.
                log.debug("Crossed over to above 0 while increasing over {}".\
                          format(desiredDiffMultiple))

                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getSaturnPlanetaryInfo(testDt)
                    p2 = Ephemeris.getUranusPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[2]:
                        t2 = testDt

                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                    else:
                        t1 = testDt
                        
                    currErrorTd = t2 - t1

                currDt = steps[2]
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                numArtifactsAdded += 1
                
            elif diffs[2] > diffs[1] and \
                     diffs[2] > diffs[0] and \
                     (diffs[2] - diffs[1] > crossoverRequirement):
                
                # Crossed over to under 'desiredDiffMultiple' while
                # decreasing under 0.  This can happen when planets
                # are moving in retrograde motion.
                log.debug("Crossed over to under {} while decreasing under 0".\
                          format(desiredDiffMultiple))
                
                # Timestamp is between steps[2] and steps[1].
                
                # This is the upper-bound of the error timedelta.
                t1 = steps[1]
                t2 = steps[2]
                currErrorTd = t2 - t1

                # Refine the timestamp until it is less than the threshold.
                while currErrorTd > maxErrorTd:
                    log.debug("Refining between {} and {}".\
                              format(Ephemeris.datetimeToStr(t1),
                                     Ephemeris.datetimeToStr(t2)))
                    
                    # Check the timestamp between.
                    diffTd = t2 - t1
                    halfDiffTd = \
                        datetime.\
                        timedelta(days=(diffTd.days / 2.0),
                                  seconds=(diffTd.seconds / 2.0),
                                  microseconds=(diffTd.microseconds / 2.0))
                    testDt = t1 + halfDiffTd
                    
                    p1 = Ephemeris.getSaturnPlanetaryInfo(testDt)
                    p2 = Ephemeris.getUranusPlanetaryInfo(testDt)
                    
                    diffDeg = \
                            p1.geocentric['sidereal']['longitude'] - \
                            p2.geocentric['sidereal']['longitude']
                    if diffDeg < 0:
                        diffDeg += 360.0
            
                    testDiff = diffDeg % desiredDiffMultiple
                    if testDiff < diffs[1]:
                        t1 = testDt
                    else:
                        t2 = testDt
                        
                        # Update the curr values as the later boundary.
                        steps[2] = t2
                        diffs[2] = testDiff
                        
                    currErrorTd = t2 - t1
                    
                currDt = steps[2]
                
                # Create the artifact at the timestamp.
                PlanetaryCombinationsLibrary.\
                    addVerticalLine(pcdd, currDt,
                                    highPrice, lowPrice, tag, color)
                numArtifactsAdded += 1
                
            # Prepare for the next iteration.
            steps.append(copy.deepcopy(steps[-1]) + stepSizeTd)
            del steps[0]
            diffs.append(diffs[-1])
            del diffs[0]
            
        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
        
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv


    @staticmethod
    def addBayerTimeFactorsAstroVerticalLines(\
        pcdd, startDt, endDt,
        highPrice, lowPrice,
        color=None,
        maxErrorTd=datetime.timedelta(hours=1)):
        """Adds vertical lines to the PriceChartDocumentData object,
        at locations where all planets (excluding the Moon) transit
        across the following places, geocentrically, in the tropical zodiac:

        13 deg 36' 12" Taurus (43.6033333333333 degrees longitude)
        16 deg 21' 48" Virgo  (166.3633333333333 degrees longitude)
        11 deg 04' 56" Capricorn (281.0822222222222 degrees longitude)
        19 deg 15' 24" Capricorn (289.2566666666666 degrees longitude)
        
        Note: Default tag used for the artifacts added is the name of
        this function, without the word 'add' at the beginning, and
        with the str for the relevant planet name appended.
        
        Arguments:
        pcdd      - PriceChartDocumentData object that will be modified.
        startDt   - datetime.datetime object for the starting timestamp
                    to do the calculations for artifacts.
        endDt     - datetime.datetime object for the ending timestamp
                    to do the calculations for artifacts.
        highPrice - float value for the high price to end the vertical line.
        lowPrice  - float value for the low price to end the vertical line.
        color     - QColor object for what color to draw the lines.
                    If this is set to None, then the default color will be used.
        maxErrorTd - datetime.timedelta object holding the maximum
                     time difference between the exact planetary
                     combination timestamp, and the one calculated.
                     This would define the accuracy of the
                     calculations.  
        
        Returns:
        True if operation succeeded, False otherwise.
        """

        log.debug("Entered " + inspect.stack()[0][3] + "()")

        # Return value.
        rv = True

        # Make sure the inputs are valid.
        if endDt < startDt:
            log.error("Invalid input: 'endDt' must be after 'startDt'")
            rv = False
            return rv
        if lowPrice > highPrice:
            log.error("Invalid input: " +
                      "'lowPrice' is not less than or equal to 'highPrice'")
            rv = False
            return rv
        
        # Set the color if it is not already set to something.
        colorWasSpecifiedFlag = True
        if color == None:
            colorWasSpecifiedFlag = False
            #color = QColor(Qt.blue)

        # Set the tag str.
        tag = inspect.stack()[0][3]
        if tag.startswith("add") and len(tag) > 3:
            tag = tag[3:]
        log.debug("tag == '{}'".format(tag))
        
        # Initialize the Ephemeris with the birth location.
        log.debug("Setting ephemeris location ...")
        Ephemeris.setGeographicPosition(pcdd.birthInfo.longitudeDegrees,
                                        pcdd.birthInfo.latitudeDegrees,
                                        pcdd.birthInfo.elevation)

        # Count of artifacts added.
        numArtifactsAdded = 0
        
        # Set the step size.
        stepSizeTd = datetime.timedelta(days=1)

        # Differencial multiple we are looking for, in degrees.
        #
        # Note, the below algorithm assumes that 360 is evenly
        # divisible by 'desiredDiffMultiple'.  Otherwise it will
        # not catch all cases (e.g. if we are looking for 14
        # degree multiples, it will catch if the diffDeg is 14,
        # but not if the diffDeg is -14).
        desiredDiffMultiple = 360.0

        # Parameter for a test to show that it actually crossed over
        # the boundary of the degree differential multiple.
        crossoverRequirement = (2/3) * desiredDiffMultiple
        
        # Now, in UTC.
        now = datetime.datetime.now(pytz.utc)
        
        # Get planetary ids that we want to get info for.
        planetIds = []
        planetIds.append(Ephemeris.getSunPlanetaryInfo(now).id)
        #planetIds.append(Ephemeris.getMoonPlanetaryInfo(now).id)
        planetIds.append(Ephemeris.getMercuryPlanetaryInfo(now).id)
        planetIds.append(Ephemeris.getVenusPlanetaryInfo(now).id)
        planetIds.append(Ephemeris.getMarsPlanetaryInfo(now).id)
        planetIds.append(Ephemeris.getJupiterPlanetaryInfo(now).id)
        planetIds.append(Ephemeris.getSaturnPlanetaryInfo(now).id)
        planetIds.append(Ephemeris.getUranusPlanetaryInfo(now).id)
        planetIds.append(Ephemeris.getNeptunePlanetaryInfo(now).id)
        planetIds.append(Ephemeris.getPlutoPlanetaryInfo(now).id)
        

        # Cross-over points.
        # 13 deg 36' 12" Taurus (43.6033333333333 degrees longitude)
        # 16 deg 21' 48" Virgo  (166.3633333333333 degrees longitude)
        # 11 deg 04' 56" Capricorn (281.0822222222222 degrees longitude)
        # 19 deg 15' 24" Capricorn (289.2566666666666 degrees longitude)
        crossOverPoints = [43.6033333333333,
                           166.3633333333333,
                           281.0822222222222,
                           289.2566666666666]

        copIndex = None
        
        for copIndex in range(len(crossOverPoints)):
            cop = crossOverPoints[copIndex]
            log.info("Working on cross-over-point {} ({})".\
                     format(AstrologyUtils.\
                            convertLongitudeToStrWithRasiAbbrev(cop),
                            cop))
                               
            if colorWasSpecifiedFlag == False:
                # Use custom colors for each index of the crossOverPoints.
                if copIndex == 0:
                    color = QColor(Qt.blue)
                elif copIndex == 1:
                    color = QColor(Qt.red)
                elif copIndex == 2:
                    color = QColor(Qt.green)
                elif copIndex == 3:
                    color = QColor(Qt.darkYellow)
            
            for planetId in planetIds:
                log.info(\
                    "Working on planet {} for cross-over-point {} ({})".\
                    format(Ephemeris.getPlanetNameForId(planetId),
                           AstrologyUtils.\
                           convertLongitudeToStrWithRasiAbbrev(cop),
                           cop))
                               

                steps = []
                steps.append(copy.deepcopy(startDt))
                steps.append(copy.deepcopy(startDt))
                steps.append(copy.deepcopy(startDt))

                diffs = []
                diffs.append(None)
                diffs.append(None)
                diffs.append(None)
        
                # Iterate through, creating artfacts and adding them as we go.
                log.debug("Stepping through timestamps from {} to {} ...".\
                          format(Ephemeris.datetimeToStr(startDt),
                                 Ephemeris.datetimeToStr(endDt)))
        
                while steps[2] < endDt:
                    
                    currDt = steps[2]
                    log.debug("Looking at currDt == {} ...".\
                              format(Ephemeris.datetimeToStr(currDt)))
                    
                    p1 = Ephemeris.getPlanetaryInfo(planetId, currDt)
        
                    #log.debug("{} geocentric sidereal longitude is: {}".\
                    #          format(p1.name,
                    #                 p1.geocentric['sidereal']['longitude']))
                    #log.debug("{} geocentric sidereal longitude is: {}".\
                    #          format(p2.name,
                    #                 p2.geocentric['sidereal']['longitude']))
                    log.debug("{} geocentric tropical longitude is: {}".\
                              format(p1.name,
                                     p1.geocentric['tropical']['longitude']))
                    #log.debug("{} geocentric tropical longitude is: {}".\
                    #          format(p2.name,
                    #                 p2.geocentric['tropical']['longitude']))
                    
                    diffDeg = \
                        p1.geocentric['tropical']['longitude'] - cop
                    if diffDeg < 0:
                        diffDeg += 360.0
                        
                    log.debug("diffDeg == {}".format(diffDeg))
                    
                    currDiff = diffDeg % desiredDiffMultiple
                    
                    if diffs[0] == None:
                        diffs[0] = currDiff
                    if diffs[1] == None:
                        diffs[1] = currDiff
                    diffs[2] = currDiff
                    
                    log.debug("steps[0] == {}".format(steps[0]))
                    log.debug("steps[1] == {}".format(steps[1]))
                    log.debug("steps[2] == {}".format(steps[2]))
                    
                    log.debug("diffs[0] == {}".format(diffs[0]))
                    log.debug("diffs[1] == {}".format(diffs[1]))
                    log.debug("diffs[2] == {}".format(diffs[2]))

                    if diffs[2] < diffs[0] and \
                           diffs[2] < diffs[1] and \
                           (diffs[1] - diffs[2] > crossoverRequirement):
                        
                        # Crossed over to above 0 while increasing over
                        # 'desiredDiffMultiple'.  This happens when planets
                        # are moving in direct motion.
                        log.debug("Crossed over to above 0 " +
                                  "while increasing over {}".\
                                  format(desiredDiffMultiple))
        
                        # Timestamp is between steps[2] and steps[1].
                        
                        # This is the upper-bound of the error timedelta.
                        t1 = steps[1]
                        t2 = steps[2]
                        currErrorTd = t2 - t1
        
                        # Refine the timestamp until it is less than the threshold.
                        while currErrorTd > maxErrorTd:
                            log.debug("Refining between {} and {}".\
                                      format(Ephemeris.datetimeToStr(t1),
                                             Ephemeris.datetimeToStr(t2)))
                            
                            # Check the timestamp between.
                            diffTd = t2 - t1
                            halfDiffTd = \
                                datetime.\
                                timedelta(days=(diffTd.days / 2.0),
                                          seconds=(diffTd.seconds / 2.0),
                                          microseconds=(diffTd.microseconds / 2.0))
                            testDt = t1 + halfDiffTd
                            
                            p1 = Ephemeris.getPlanetaryInfo(planetId, currDt)
                            
                            diffDeg = \
                                    p1.geocentric['tropical']['longitude'] - cop
                            if diffDeg < 0:
                                diffDeg += 360.0
                    
                            testDiff = diffDeg % desiredDiffMultiple
                            if testDiff < diffs[2]:
                                t2 = testDt
        
                                # Update the curr values as the later boundary.
                                steps[2] = t2
                                diffs[2] = testDiff
                            else:
                                t1 = testDt
                                
                            currErrorTd = t2 - t1
        
                        currDt = steps[2]
                        
                        # Create the artifact at the timestamp.
                        PlanetaryCombinationsLibrary.\
                            addVerticalLine(pcdd, currDt,
                                            highPrice, lowPrice, tag + "_" + p1.name, color)
                        numArtifactsAdded += 1
                        
                    elif diffs[2] > diffs[1] and \
                             diffs[2] > diffs[0] and \
                             (diffs[2] - diffs[1] > crossoverRequirement):
                        
                        # Crossed over to under 'desiredDiffMultiple' while
                        # decreasing under 0.  This can happen when planets
                        # are moving in retrograde motion.
                        log.debug("Crossed over to under {} while decreasing under 0".\
                                  format(desiredDiffMultiple))
                        
                        # Timestamp is between steps[2] and steps[1].
                        
                        # This is the upper-bound of the error timedelta.
                        t1 = steps[1]
                        t2 = steps[2]
                        currErrorTd = t2 - t1
        
                        # Refine the timestamp until it is less than the threshold.
                        while currErrorTd > maxErrorTd:
                            log.debug("Refining between {} and {}".\
                                      format(Ephemeris.datetimeToStr(t1),
                                             Ephemeris.datetimeToStr(t2)))
                            
                            # Check the timestamp between.
                            diffTd = t2 - t1
                            halfDiffTd = \
                                datetime.\
                                timedelta(days=(diffTd.days / 2.0),
                                          seconds=(diffTd.seconds / 2.0),
                                          microseconds=(diffTd.microseconds / 2.0))
                            testDt = t1 + halfDiffTd
                            
                            p1 = Ephemeris.getPlanetaryInfo(planetId, testDt)
                            
                            diffDeg = \
                                    p1.geocentric['tropical']['longitude'] - cop
                            if diffDeg < 0:
                                diffDeg += 360.0
                    
                            testDiff = diffDeg % desiredDiffMultiple
                            if testDiff < diffs[1]:
                                t1 = testDt
                            else:
                                t2 = testDt
                                
                                # Update the curr values as the later boundary.
                                steps[2] = t2
                                diffs[2] = testDiff
                                
                            currErrorTd = t2 - t1
                            
                        currDt = steps[2]
                        
                        # Create the artifact at the timestamp.
                        PlanetaryCombinationsLibrary.\
                            addVerticalLine(pcdd, currDt,
                                            highPrice, lowPrice, tag + "_" + p1.name, color)
                        numArtifactsAdded += 1
                        
                    # Prepare for the next iteration.
                    steps.append(copy.deepcopy(steps[-1]) + stepSizeTd)
                    del steps[0]
                    diffs.append(diffs[-1])
                    del diffs[0]
                    
        log.info("Number of artifacts added: {}".format(numArtifactsAdded))
                
        log.debug("Exiting " + inspect.stack()[0][3] + "()")
        return rv


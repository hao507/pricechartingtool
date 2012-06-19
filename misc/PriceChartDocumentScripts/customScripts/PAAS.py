#!/usr/bin/env python3
##############################################################################
# Description:
#
#   Module for adding various PriceBarChartArtifacts to a
#   PriceChartDocumentData object that are relevant to a PAAS
#   chart.
#
##############################################################################

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

# Holds functions for adding artifacts for various aspects.
from planetaryCombinationsLibrary import PlanetaryCombinationsLibrary

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

# Start and ending timestamps for drawing.
startDt = datetime.datetime(year=1995, month=1, day=1,
                            hour=0, minute=0, second=0,
                            tzinfo=pytz.utc)
#startDt = datetime.datetime(year=2008, month=1, day=1,
#                            hour=0, minute=0, second=0,
#                            tzinfo=pytz.utc)

endDt   = datetime.datetime(year=2012, month=4, day=1,
                            hour=0, minute=0, second=0,
                            tzinfo=pytz.utc)

# High and low price limits for drawing the vertical lines.
highPrice = 50.0
lowPrice = 1.0

##############################################################################

def processPCDD(pcdd, tag):
    """Module for adding various PriceBarChartArtifacts that are
    relevant to the chart.  The tag str used for the created
    artifacts is based the name of the function that is being called,
    without the 'add' string at the beginning.
    
    Arguments:
    pcdd - PriceChartDocumentData object that will be modified.
    tag  - str containing the tag.
           This implementation does not use this value.

    Returns:
    0 if the changes are to be saved to file.
    1 if the changes are NOT to be saved to file.
    """

    global highPrice
    global lowPrice
    
    # Return value.
    rv = 0

    stepSizeTd = datetime.timedelta(days=3)
    #highPrice = 800.0
    #highPrice = 600.0
    #lowPrice = 600.0
    #lowPrice = 300.0


    #######################################
    # From my paper notes dated April 21, 2012 on PAAS, it gives the
    # following about PAAS that works somewhat well and is worth of
    # investigating further.
    #
    # Mars-Venus connection (would need to apply a filter)
    # Venus-MeanNode connection.
    # 45-degree increments of Uranus-Earth Heliocentric.
    # 51.X-degree increments of Venus-Pluto, Geocentric.
    # Mars 51.X to natal Venus.
    # TrueNorthNode 3-degree increments to natal Venus.
    # May want to check out Venus-Chiron Geocentric.
    # Test more planet transits to natal positions.
    #######################################
    
    # This is a cycle in PAAS.
    if False:
        step = 360 / 14.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Sun", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    # This is a cycle in PAAS.
    if False:
        step = 360 / 7.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    # Investigate this one more closely.
    if False:
        step = 360 / 24.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Mars", "geocentric", "tropical",
                "Venus", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    # Definitely worth keeping an eye on.  
    if False:
        step = 360 / 5.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Mars", "geocentric", "tropical",
                "Venus", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 14.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 42.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Sun", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 24.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Mercury", "geocentric", "tropical",
                "Mars", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 8.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Mercury", "heliocentric", "tropical",
                "Mars", "heliocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 12.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "heliocentric", "tropical",
                "Mercury", "heliocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 24.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "heliocentric", "tropical",
                "Mars", "heliocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 7.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "MeanNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 5.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "MeanNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 5.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    # Investigate further.
    if False:
        step = 360 / 8.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Uranus", "heliocentric", "tropical",
                "Earth", "heliocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 8.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Neptune", "heliocentric", "tropical",
                "Earth", "heliocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 25
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "heliocentric", "tropical",
                "Saturn", "heliocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 7.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "Venus", "heliocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 12.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Sun", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    # Investigate more closely.
    if False:
        step = 360 / 8.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "heliocentric", "tropical",
                "Mars", "heliocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    
    if True:
        step = 360 / 8.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "Chiron", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
            
    if False:
        step = 360 / 7.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "Pluto", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
        
    if False:
        step = 360 / 8.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "Jupiter", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
        
    if False:
        step = 360 / 7.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "Jupiter", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    # Did not work well.
    if False:
        step = 360 / 24.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "Uranus", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
        
    if False:
        # The below natal positions are for the date March 7, 1979.
        
        #start = 16.6666 + (11 * 30) # Sun position
        start = 4.5333 + (10 * 30) # Venus position
        #start = 4.6 # Mercury position
        #start = 28.89 + (10 * 30) # Mars Helio position
        #start = (3 * 30) + 8.4 # Moon position.
        #start = (5 * 30) + 10.066 # Saturn position
        #start = (5 * 30) + 17.5 # TNode position
        #divisor = 5
        #divisor = 2
        divisor = 7
        #divisor = 8
        #divisor = 24
        #divisor = 25
        #divisor = 120
        for i in range(divisor):
            degreeValue = Util.toNormalizedAngle(start + (i * 360 / divisor))
            success = PlanetaryCombinationsLibrary.\
                      addPlanetCrossingLongitudeDegVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "geocentric", "tropical",
                #"heliocentric", "tropical",
                "Mars", degreeValue)
                #"TrueNorthNode", degreeValue)


    ####################################################################

    # DId not work as well as I would have liked. 
    if False:
        step = 360 / 28.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Jupiter", "geocentric", "tropical",
                "Saturn", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 16.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Jupiter", "geocentric", "tropical",
                "Saturn", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    # Worth investigating more closely.
    if False:
        step = 360 / 16.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "Saturn", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 7.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Venus", "geocentric", "tropical",
                "Pluto", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 28.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Jupiter", "geocentric", "tropical",
                "Uranus", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    # THis works kinda well.
    if False:
        step = 360 / 24.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Jupiter", "geocentric", "tropical",
                "Uranus", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    # This works pretty well.
    if False:
        step = 360 / 24.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Saturn", "geocentric", "tropical",
                "Uranus", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 24.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Saturn", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 14.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Saturn", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 14.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Jupiter", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step

    if False:
        step = 360 / 24.0
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            success = PlanetaryCombinationsLibrary.\
                addLongitudeAspectVerticalLines(\
                pcdd, startDt, endDt, highPrice, lowPrice,
                "Jupiter", "geocentric", "tropical",
                "TrueNorthNode", "geocentric", "tropical",
                degreeDiff)
            degreeDiff += step
    
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Mercury", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Mars", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Uranus", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Saturn", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="MeanOfFive", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="CycleOfEight", 
    #    color=None, stepSizeTd=stepSizeTd)

    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice=700, lowPrice=660,
    #    planetName="Moon", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Mercury", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Mars", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Jupiter", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Saturn", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Uranus", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Neptune", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Pluto", 
    #    color=None, stepSizeTd=stepSizeTd)

    
    p = 1000
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H1")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H2")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H3")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H4")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H5")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H6")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H7")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H8")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H9")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H10")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H11")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H12")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="ARMC")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Vertex")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="EquatorialAscendant")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="CoAscendant1")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="CoAscendant2")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="PolarAscendant")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Sun")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Moon")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Mercury")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Venus")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Mars")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Jupiter")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Saturn")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Uranus")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Neptune")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Pluto")
    #p += 200



    #success = PlanetaryCombinationsLibrary.\
    #    addZeroDeclinationVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Venus")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addDeclinationVelocityPolarityChangeVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Venus")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoLongitudeElongationVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Venus")
     
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoLongitudeElongationVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Mercury")
     
    #success = PlanetaryCombinationsLibrary.\
    #    addContraparallelDeclinationAspectVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planet1Name="Venus", planet2Name="Mars")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addParallelDeclinationAspectVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planet1Name="Venus", planet2Name="Mars")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetOOBVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus")
    
    #success =  PlanetaryCombinationsLibrary.\
    #    addGeoLatitudeLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus")
    #success =  PlanetaryCombinationsLibrary.\
    #    addGeoLatitudeLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Jupiter", stepSizeTd=datetime.timedelta(days=7))
    #success =  PlanetaryCombinationsLibrary.\
    #    addGeoLatitudeLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Saturn", stepSizeTd=datetime.timedelta(days=7))
    #success =  PlanetaryCombinationsLibrary.\
    #    addGeoLatitudeLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Uranus", stepSizeTd=datetime.timedelta(days=7))
    
    #success =  PlanetaryCombinationsLibrary.\
    #    addZeroLatitudeVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus")

    #success = PlanetaryCombinationsLibrary.\
    #    addLatitudeVelocityPolarityChangeVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Venus")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addContraparallelLatitudeAspectVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planet1Name="Venus", planet2Name="Mars")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addParallelLatitudeAspectVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planet1Name="Venus", planet2Name="Mars")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetLongitudeTraversalIncrementsVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "geocentric", "sidereal", 
    #    planetEpocDt=datetime.datetime(year=1976, month=4, day=1,
    #                                   hour=13, minute=0, second=0,
    #                                   tzinfo=pytz.utc),
    #    degreeIncrement=18)

    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetLongitudeTraversalIncrementsVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "heliocentric", "sidereal", 
    #    planetEpocDt=datetime.datetime(year=1970, month=3, day=21,
    #                                   hour=0, minute=0, second=0,
    #                                   tzinfo=pytz.utc),
    #    degreeIncrement=30)

    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetLongitudeTraversalIncrementsVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Sun", "geocentric", "tropical", 
    #    planetEpocDt=datetime.datetime(year=1970, month=3, day=21,
    #                                   hour=6, minute=0, second=0,
    #                                   tzinfo=pytz.utc),
    #    degreeIncrement=15)

    #success = PlanetaryCombinationsLibrary.\
    #    addGeoLongitudeVelocityPolarityChangeVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Mercury")

    ############################################################################

    # Testing new functions for longitude aspect timestamps.
    if False:
        aspectGroup = []
        step = 180
        start = 0
        stop = 180
        degreeDiff = start
        while degreeDiff < stop or Util.fuzzyIsEqual(degreeDiff, stop):
            aspectGroup.append(degreeDiff)
            degreeDiff += step

        planet1ParamsList = [("Venus", "geocentric", "sidereal")]
        planet2ParamsList = [("Uranus", "geocentric", "sidereal")]
        uniDirectionalAspectsFlag = True
        
        for aspect in aspectGroup:
            degreeDifference = aspect
    
            # Get the timestamps of the aspect.
            timestamps = \
                PlanetaryCombinationsLibrary.getLongitudeAspectTimestamps(\
                pcdd, startDt, endDt,
                planet1ParamsList,
                planet2ParamsList,
                degreeDifference,
                uniDirectionalAspectsFlag)
    
            # Get the tag str for the aspect.
            tag = \
                PlanetaryCombinationsLibrary.getTagNameForLongitudeAspect(\
                planet1ParamsList,
                planet2ParamsList,
                degreeDifference,
                uniDirectionalAspectsFlag)
            
            # Get the color to apply.
            from astrologychart import AstrologyUtils
            color = AstrologyUtils.\
                    getForegroundColorForPlanetName(planet1ParamsList[0][0])
            
            # Draw the aspects.
            for dt in timestamps:
                PlanetaryCombinationsLibrary.addVerticalLine(\
                    pcdd, dt, highPrice, lowPrice, tag, color)
    
            log.info("Added {} artifacts for aspect {} degrees.".\
                      format(len(timestamps), degreeDifference))
        success = True
    
    ############################################################################

    if success == True:
        log.debug("Success!")
        rv = 0
    else:
        log.debug("Failure!")
        rv = 1

    return rv

##############################################################################

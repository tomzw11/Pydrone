
import time
import math
import sys
from bebop import *

drone = Bebop()

# Distance to move in [m] and dPsi [rad]
dX = 0
dY = 0
dZ = 0
dPsi = math.pi/2


def moveByFuncition():

    global moveDone
    moveDone = True # Flag to know when movements are done
    try:
        drone.takeoff()
        drone.wait( 1.0 )
        drone.hover()
        for i in range (0,4):
            print "Movement: ", i
            drone.moveBy( dX, dY, dZ, dPsi) # Command to move to a relative position
            moveByControl() # Stops the movements
        drone.hover()
        drone.wait( 1.0 )
        drone.land()
        sys.exit(0)
    except ManualControlException, e:
        print
        print "ManualControlException"
        if drone.flyingState is None or drone.flyingState == 1: # Taking off
            drone.emergency()
        drone.land()

def moveByControl():    # While Event != OK or != Interrupted, keep moving
    while moveDone:
        drone.update()
        try:
            (dX, dY, dZ, dPsi, Event) = drone.moveByEnd
            print "Drone moved [mts, rad]:", dX, dY, dZ, dPsi
            Events = ["OK. Relative displacement done", "UNKNOWN", "BUSY", "NOTAVAILABLE", "INTERRUPTED"]
            print "Move by event", Event, Events[Event]
            if Event == 0 or Event == 5:    # Arrived or Interrupted
                moveDone = False
        except Exception, e:    # Catch any error
            print "Error getting data from drone, error:", e
            pass
    moveDone = True
    drone.wait( 1.0 ) # Waits () secs after arrive to its position

if __name__ == "__main__":
    moveByFuncition()
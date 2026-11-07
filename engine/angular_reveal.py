"""Angular and radial visibility envelopes for geometry assembly."""
import numpy as np
from .geometry import smoothstep, TAU

def angular_reveal(theta, progress, direction='counterclockwise', softness=.18, start_angle=0.0):
    angle=np.mod(theta-start_angle,TAU)
    if direction=='clockwise': distance=np.mod(-angle,TAU)
    elif direction=='bidirectional': distance=np.minimum(np.mod(angle,TAU),np.mod(-angle,TAU))
    else: distance=angle
    return smoothstep((progress*TAU-distance+softness)/softness)

def radial_reveal(radius, progress, softness=.06):
    return smoothstep((progress-radius+softness)/softness)


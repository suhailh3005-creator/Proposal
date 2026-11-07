"""Seamless ring-first, bottom-up diamond assembly choreography."""
import numpy as np
from .geometry import smoothstep, TAU

PHASES=((0,5,'ring'),(5,9,'diamond'),(9,11,'text'),(11,15,'rotate'),(15,20,'fade'))

def phase_at(t):
    t=t%20
    for start,end,name in PHASES:
        if start<=t<end: return name,(t-start)/(end-start)
    return 'orbital',0.

def frame_state(t, angles, kinds, base, seed=42017):
    """Draw both ring arches from the bottom, then grow the diamond upward.

    The final fade reaches exactly zero at the loop seam, matching the empty
    first frame. Smoothstep easing gives both assembly and fade zero velocity
    at their endpoints.
    """
    t=t%20; phase,u=phase_at(t); n=len(base)
    pos=base.copy()
    ring=(kinds==0)|(kinds==1)
    diamond=kinds==2
    orbit=(kinds==3)|(kinds==4)
    stars=kinds==5
    opacity=np.zeros(n,dtype=float)
    tau_time=TAU*t/20
    aspect=1.12

    if phase=='ring':
        progress=smoothstep(u)
        # Ellipse theta=pi/2 is its screen-space bottom. The two fronts travel
        # in opposite directions and meet at theta=3pi/2, the top of the ring.
        delta=np.mod(angles-np.pi/2+np.pi,TAU)-np.pi
        distance=np.abs(delta)
        front=progress*(np.pi+.12)
        reveal=smoothstep((front-distance)/.12)
        opacity[ring]=reveal[ring]
    elif phase=='diamond':
        opacity[ring]=1
        progress=smoothstep(u)
        # Grow a circular front from the diamond's lower tip through its facets.
        bottom_y=float(np.max(base[diamond,1]))
        distance=np.hypot(base[:,0],base[:,1]-bottom_y)
        span=max(float(np.max(distance[diamond])),1e-6)
        order=distance/(span*1.16)
        opacity[diamond]=smoothstep((progress-order[diamond])/.08)
        opacity[orbit]=.34*progress
        opacity[stars]=.50*progress
    elif phase=='text':
        opacity[ring|diamond]=1
        progress=smoothstep(u)
        opacity[orbit]=.34*progress
        opacity[stars]=.50*progress
    elif phase=='rotate':
        opacity[ring|diamond]=1
        opacity[orbit]=.34
        opacity[stars]=.50
        # Two eased horizontal spins around the ring's bottommost point. The
        # x foreshortening models a turn around the vertical axis; mild depth
        # scaling keeps the rotation legible while the bottom pivot stays put.
        angle=2*TAU*smoothstep(u)
        c=np.cos(angle); s=np.sin(angle)
        moving=ring|diamond
        pivot=int(np.argmax(base[ring,1]))
        pivot_x=float(base[ring,0][pivot])
        pivot_y=float(base[ring,1][pivot])
        x=pos[moving,0].copy()-pivot_x
        y=pos[moving,1].copy()-pivot_y
        depth=x*s
        perspective=1+.12*depth
        pos[moving,0]=pivot_x+x*c*perspective
        pos[moving,1]=pivot_y+y*perspective
    elif phase=='fade':
        remaining=1-smoothstep(u)
        opacity[ring|diamond]=remaining
        opacity[orbit]=.34*remaining
        opacity[stars]=.50*remaining

    # Gentle, periodic shimmer keeps the completed sculpture alive without
    # moving its geometry or disturbing the clean circular outline.
    flicker=.92+.08*np.sin(tau_time*2+np.arange(n)*.17)
    opacity*=flicker
    opacity[stars]*=.78+.22*np.sin(tau_time+angles[stars])
    return pos,opacity,phase,aspect


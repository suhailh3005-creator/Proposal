"""Scalar easing and corresponding-point ring morphs."""
import numpy as np
from .geometry import smoothstep

def ease(x, kind='smoothstep'):
    x=np.clip(x,0,1)
    if kind=='cubic': return x*x*(3-2*x)
    if kind=='sine': return .5-.5*np.cos(np.pi*x)
    if kind=='exponential': return np.where(x==0,0,2**(10*x-10))
    if kind=='spring': return 1-np.exp(-7*x)*np.cos(10*x)
    return smoothstep(x)

def morph_ring(theta, radius, aspect_from, aspect_to, alpha):
    aspect=aspect_from+(aspect_to-aspect_from)*ease(alpha)
    return np.column_stack((radius*np.cos(theta),radius*aspect*np.sin(theta)))


"""Particle luminance and temporal glint modulation."""
import numpy as np
def luminance(base, phase, time, category):
    flicker=.78+.22*np.sin((2*np.pi*time/20)*7+phase*1.7)
    weights=np.choose(category,[1.0,1.22,1.28,.68,.42,.32])
    return np.clip(base*flicker*weights,0,1)


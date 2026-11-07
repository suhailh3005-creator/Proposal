"""Small vectorized coherent perturbations, deterministic by frame."""
import numpy as np
def coherent_noise(theta, time, amplitude=.003):
    return amplitude*(np.sin(theta*2+time*.7)+.45*np.sin(theta*5-time*.31))


"""Persistent vectorized particle attributes and bounded motion."""
from dataclasses import dataclass
import numpy as np
@dataclass
class ParticleField:
    base: np.ndarray
    kind: np.ndarray
    angle: np.ndarray
    phase: np.ndarray
    brightness: np.ndarray
    velocity: np.ndarray
    @classmethod
    def create(cls, count=5200, seed=42017, **geometry):
        from .geometry import make_scene
        p,k,a,ph,b=make_scene(count,seed,**geometry)
        return cls(p,k,a,ph,b,np.zeros_like(p))
    def drift(self, dt, rng, strength=.004):
        # Low amplitude Brownian impulse with damping preserves the attachment.
        self.velocity*=.88
        self.velocity+=rng.normal(0,strength,(len(self.base),2))*dt*30
        self.velocity=np.clip(self.velocity,-.025,.025)
        return self.base+self.velocity*dt


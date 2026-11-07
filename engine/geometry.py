"""Vectorized procedural geometry in normalized [-1, 1] coordinates."""
from __future__ import annotations
import numpy as np

TAU = np.pi * 2


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x*x*(3.0-2.0*x)

def ellipse(count, rx, ry, phase=0.0, thickness=0.0, rng=None):
    rng = rng or np.random.default_rng(0)
    a = np.linspace(0, TAU, count, endpoint=False) + phase
    r = 1 + rng.normal(0, thickness, count)
    return np.column_stack((rx*np.cos(a)*r, ry*np.sin(a)*r)), a

def line(a, b, count):
    u = np.linspace(0, 1, count)
    return np.column_stack((a[0]*(1-u)+b[0]*u, a[1]*(1-u)+b[1]*u))

def crown(count=800, width=.12, height=.32, bottom_y=-.356):
    """Inverted diamond: broad upper shoulders and a long downward tip."""
    shoulder=bottom_y-height*.83
    top=(0.,shoulder-height*.29)
    left=(-width,shoulder); right=(width,shoulder)
    bottom=(0.,shoulder+height*.83)
    mid=(0.,(shoulder+bottom[1])*.5)
    segments=[(top,left),(left,bottom),(bottom,right),(right,top),
              (top,bottom),(left,right),(left,mid),(right,mid),(mid,bottom)]
    # Reserve less than half the particles for line work so the diamond's
    # triangulated face stays visibly filled at terminal resolution.
    line_count=min(count,int(count*.46))
    each=line_count//len(segments)
    pts=np.concatenate([line(a,b,each) for a,b in segments],axis=0) if each else np.empty((0,2))
    # Uniform barycentric samples fill each triangular facet.
    rng=np.random.default_rng(19)
    n=max(0,count-len(pts))
    u=rng.random(n); v=rng.random(n)
    tri=rng.integers(0,4,n)
    vertices=np.array([[top,left,bottom],[top,bottom,right],[left,bottom,right],[top,left,right]],float)
    # Uniform barycentric samples, with a slight edge bias.
    w1=np.sqrt(u); w2=v*w1; w0=1-w1
    tri_pts=(vertices[tri,0]*w0[:,None]+vertices[tri,1]*(w1-w2)[:,None]+vertices[tri,2]*w2[:,None])
    return np.vstack((pts,tri_pts))

def make_scene(count=1380, seed=42017, ring_radius=.255, ring_aspect=1.12, ring_thickness=.014, ambient=95, diamond_width=.12, diamond_height=.32):
    """Return positions, kind ids and stable per-particle attributes."""
    rng=np.random.default_rng(seed)
    counts=[int(count*.52),int(count*.18),int(count*.22),int(count*.05),count-int(count*.97)]
    parts=[]; kinds=[]; angle=[]; phase=[]; brightness=[]
    # Main ring, edge glints, facets, orbits and axis; identities persist in time.
    ring_center_y=-.07
    p,a=ellipse(counts[0],ring_radius,ring_radius*ring_aspect,thickness=ring_thickness,rng=rng)
    p[:,1]+=ring_center_y  # leave room below the sculpture for the dot message
    parts.append(p); kinds.extend([0]*len(p)); angle.extend(a)
    p,a=ellipse(counts[1],ring_radius*.99,ring_radius*ring_aspect*.99,thickness=.038,rng=rng)
    p[:,1]+=ring_center_y
    parts.append(p); kinds.extend([1]*len(p)); angle.extend(a)
    diamond_bottom=ring_center_y-ring_radius*ring_aspect
    p=crown(counts[2],diamond_width,diamond_height,diamond_bottom); parts.append(p); kinds.extend([2]*len(p)); angle.extend(np.arctan2(p[:,1]+.32,p[:,0]))
    orbit=[]
    for i in range(counts[3]):
        a=rng.uniform(0,TAU); q=(i%3); rx=[.40,.34,.46][q]; ry=[.34,.48,.24][q]
        x=rx*np.cos(a); y=ry*np.sin(a); rot=[-.32,.65,.08][q]
        orbit.append((x*np.cos(rot)-y*np.sin(rot),x*np.sin(rot)+y*np.cos(rot)))
    p=np.array(orbit); parts.append(p); kinds.extend([3]*len(p)); angle.extend(np.arctan2(p[:,1],p[:,0]))
    axis=np.column_stack((rng.normal(0,.002,counts[4]),rng.uniform(-.44,.4,counts[4])))
    parts.append(axis); kinds.extend([4]*len(axis)); angle.extend(np.full(len(axis),np.pi/2))
    stars=np.column_stack((rng.uniform(-.96,.96,ambient),rng.uniform(-.94,.94,ambient)))
    parts.append(stars); kinds.extend([5]*ambient); angle.extend(np.arctan2(stars[:,1],stars[:,0]))
    pos=np.vstack(parts); kinds=np.asarray(kinds,dtype=np.int8); ang=np.asarray(angle)
    phase=rng.uniform(0,TAU,len(pos)); brightness=rng.uniform(.32,1.0,len(pos))
    return pos,kinds,ang,phase,brightness


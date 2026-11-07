import unittest
import numpy as np
from engine.geometry import ellipse, make_scene
from engine.animation import frame_state, phase_at
from engine.angular_reveal import angular_reveal
from engine.morphing import morph_ring
from engine.renderer import Renderer

class GeometryTests(unittest.TestCase):
    def test_ellipse_bounds_and_count(self):
        p,a=ellipse(300,.25,.4); self.assertEqual(p.shape,(300,2))
        self.assertAlmostEqual(float(np.max(np.abs(p[:,0]))),.25,places=3)
    def test_scene_is_deterministic_and_has_categories(self):
        a=make_scene(1200,17,ambient=20); b=make_scene(1200,17,ambient=20)
        np.testing.assert_array_equal(a[0],b[0]); self.assertEqual(set(np.unique(a[1])),set(range(6)))
    def test_crown_bounds(self):
        p,k,*_=make_scene(1000,ambient=20); crown=p[k==2]
        self.assertLess(crown[:,1].min(),-.55); self.assertGreater(crown[:,1].max(),-.42)
        self.assertLess(abs(float(crown[:,1].max())+.255*1.54),.02)

class AnimationTests(unittest.TestCase):
    def test_phase_boundaries(self):
        self.assertEqual(phase_at(14.6)[0],'bottom-up'); self.assertEqual(phase_at(20)[0],'orbital')
    def test_frame_and_reconstruction(self):
        p,k,a,*_=make_scene(1500,ambient=15)
        early=frame_state(14.55,a,k,p)[1]; late=frame_state(17.4,a,k,p)[1]
        self.assertTrue(np.isfinite(frame_state(8,a,k,p)[0]).all())
        self.assertGreater(float(late[k==0].mean()),float(early[k==0].mean()))
    def test_loop_endpoint_is_continuous(self):
        p,k,a,*_=make_scene(1200,ambient=15)
        p0,o0,_,_=frame_state(0,a,k,p); p1,o1,_,_=frame_state(19.999,a,k,p)
        self.assertLess(float(np.max(np.abs(p0-p1))),.002)
        self.assertLess(float(np.max(np.abs(o0-o1))),.01)
    def test_angular_wave(self):
        theta=np.linspace(0,2*np.pi,1000,endpoint=False)
        self.assertGreater(angular_reveal(theta,.8).mean(),angular_reveal(theta,.2).mean())
    def test_morph_endpoint(self):
        p=morph_ring(np.array([0.,np.pi/2]),.3,1.5,.5,1)
        self.assertAlmostEqual(p[1,1],.15)

class RendererTests(unittest.TestCase):
    def test_braille_frame(self):
        out=Renderer().render(np.array([[0.,0.]]),np.array([1.]))
        self.assertTrue(any('\u2800' <= ch <= '\u28ff' for ch in out)); self.assertTrue(out.startswith('\x1b[?25l'))
if __name__=='__main__': unittest.main()

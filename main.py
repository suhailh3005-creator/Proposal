#!/usr/bin/env python3
"""Live particle orbital art, with an optional offline GIF preview exporter."""
from __future__ import annotations
import argparse, pathlib, shutil, subprocess, sys, time, tomllib

ROOT=pathlib.Path(__file__).resolve().parent
def load_config():
    with (ROOT/'config.toml').open('rb') as f: return tomllib.load(f)

def frame(t, scene, brightness=.82):
    from engine.animation import frame_state
    from engine.lighting import luminance
    base,kinds,angles,phases,attrs=scene
    pos,opacity,phase,aspect=frame_state(t,angles,kinds,base)
    levels=luminance(attrs,phases,t,kinds)*opacity*brightness
    return pos,levels,phase,aspect

def export_gif(path, duration, fps, scene, brightness):
    """Export the live scene with a large, readable proposal caption."""
    import numpy as np
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg: raise RuntimeError('GIF export needs ffmpeg.')
    target=pathlib.Path(path); target.parent.mkdir(parents=True,exist_ok=True)
    work=target.parent/'.orbital-frames'; work.mkdir(exist_ok=True)
    # Dot cells keep the source image's 432x384 proportions.
    cols,rows=144,76; w,h=432,384
    for i in range(int(duration*fps)):
        pos,level,_,_=frame(i/fps,scene,brightness)
        cx=np.clip(((pos[:,0]+1)*.5*cols).astype(int),0,cols-1)
        cy=np.clip(((pos[:,1]+1)*.5*rows).astype(int),0,rows-1)
        img=np.zeros((h,w),dtype=np.uint8)
        for particle,(gx,gy) in enumerate(zip(cx,cy)):
            value=float(level[particle])
            if value<.12: continue
            ink=np.uint8(min(255,150+value*105))
            x=gx*3+1; y=gy*5+2
            if ink>img[y,x]: img[y,x]=ink
        (work/f'frame_{i:04d}.pgm').write_bytes(f'P5\n{w} {h}\n255\n'.encode()+img.tobytes())
    font_candidates=(
        '/usr/share/fonts/noto/NotoSansMono-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
        '/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf',
    )
    font=next((candidate for candidate in font_candidates if pathlib.Path(candidate).is_file()),None)
    if font is None and shutil.which('fc-match'):
        match=subprocess.run(['fc-match','-f','%{file}','monospace:style=Bold'],capture_output=True,text=True,check=True)
        font=match.stdout.strip()
    if not font: raise RuntimeError('GIF text overlay needs a monospace font (for example Noto Sans Mono).')
    font=font.replace('\\','\\\\').replace(':','\\:').replace("'","\\'")
    alpha="if(lt(t,9),0,if(lt(t,11),pow((t-9)/2,2)*(3-2*((t-9)/2)),if(lt(t,15),1,pow((20-t)/5,2)*(3-2*((20-t)/5)))))"
    text_filters=(
        f"drawtext=fontfile='{font}':text='WILL YOU MARRY ME':fontcolor=white:fontsize=22:x=(w-text_w)/2:y=270:alpha='{alpha}'",
        f"drawtext=fontfile='{font}':text='ANISHU...?':fontcolor=white:fontsize=22:x=(w-text_w)/2:y=302:alpha='{alpha}'",
    )
    video_filter=','.join(text_filters)+',split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse=dither=bayer'
    subprocess.run([ffmpeg,'-y','-v','error','-framerate',str(fps),'-i',str(work/'frame_%04d.pgm'),
                    '-vf',video_filter,
                    '-gifflags','0','-loop','0',str(target)],check=True)
    shutil.rmtree(work); print(f'Wrote {target}')

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--export',metavar='GIF',help='export the current animation as a GIF')
    parser.add_argument('--duration',type=float,default=None,help='preview duration in seconds'); args=parser.parse_args()
    from engine.geometry import make_scene
    from engine.hud import format_hud
    from engine.terminal import Terminal
    from engine.renderer import Renderer
    cfg=load_config(); anim=cfg['animation']; pcfg=cfg['particles']; geo=cfg['geometry']
    scene=make_scene(pcfg['count'],anim['seed'],geo['ring_radius'],geo['ring_aspect'],geo['ring_thickness'],pcfg['ambient'],geo['diamond_width'],geo['diamond_height'])
    if args.export:
        try: export_gif(args.export,args.duration or anim['duration'],anim['fps'],scene,pcfg['brightness'])
        except RuntimeError as exc: print(exc,file=sys.stderr); return 2
        return 0
    renderer=Renderer(cfg['render']['mode'],cfg['render']['color']); paused=False; debug=False
    show_hud=cfg['render']['hud']; show_orbits=True; outlines=True; speed=anim['speed']; t0=time.monotonic(); previous=t0
    try:
        with Terminal() as terminal:
            while True:
                now=time.monotonic(); dt=now-previous; previous=now; key=terminal.key()
                if key in ('q','Q','\x03'): break
                if key==' ': paused=not paused
                elif key in ('r','R'): t0=now
                elif key in ('[','{'): speed=max(.1,speed-.1)
                elif key in (']','}'): speed=min(4.,speed+.1)
                elif key in ('h','H'): show_hud=not show_hud
                elif key in ('d','D'): debug=not debug
                elif key in ('o','O'): show_orbits=not show_orbits
                elif key in ('g','G'): outlines=not outlines
                elif key in ('c','C'): renderer.color={'truecolor':'256','256':'mono','mono':'truecolor'}[renderer.color]
                elif key in ('p','P'): renderer.mode='hybrid' if renderer.mode in ('dots','ascii') else 'dots'
                elif key in ('+','='):
                    pcfg['count']=min(30000,pcfg['count']+500)
                    scene=make_scene(pcfg['count'],anim['seed'],geo['ring_radius'],geo['ring_aspect'],geo['ring_thickness'],pcfg['ambient'],geo['diamond_width'],geo['diamond_height'])
                elif key in ('-','_'):
                    pcfg['count']=max(1000,pcfg['count']-500)
                    scene=make_scene(pcfg['count'],anim['seed'],geo['ring_radius'],geo['ring_aspect'],geo['ring_thickness'],pcfg['ambient'],geo['diamond_width'],geo['diamond_height'])
                t=(0 if paused else (now-t0)*speed)%anim['duration']
                pos,levels,phase,aspect=frame(t,scene,pcfg['brightness'])
                if not show_orbits: levels[scene[1]==3]=0
                if not outlines: levels[(scene[1]==1)|(scene[1]==2)]*=.15
                hud=format_hud(t,phase,len(pos),1/max(dt,1e-6),aspect,debug) if show_hud else ''
                sys.stdout.write(renderer.render(pos,levels,hud)); sys.stdout.flush()
                time.sleep(max(0,1/anim['fps']-(time.monotonic()-now)))
    except KeyboardInterrupt: pass
    except RuntimeError as exc: print(exc,file=sys.stderr); return 2
    return 0
if __name__=='__main__': raise SystemExit(main())

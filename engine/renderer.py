"""Reference-proportioned ANSI dot renderer with optional Braille mode."""
import re
import shutil
import numpy as np

class Renderer:
    def __init__(self, mode='dots', color='truecolor'):
        self.mode=mode; self.color=color
    def dimensions(self):
        size=shutil.get_terminal_size((100,34))
        return max(20,size.columns),max(10,size.lines-1)
    def render(self, points, levels, hud=''):
        w,h=self.dimensions()
        hud_lines=hud.splitlines() if hud else []
        dot_mode=self.mode in ('dots','ascii')
        if dot_mode:
            # A terminal cell is roughly twice as tall as it is wide. Fit the
            # 432x384 reference composition without stretching its ring.
            image_h=max(8,h-len(hud_lines))
            image_h=min(image_h,max(8,int(w/(2*(432/384)))))
            image_w=min(w,int(round(image_h*2*(432/384))))
            left=(w-image_w)//2
            gw,gh=image_w,image_h
        else:
            left=0; gw,gh=w*2,h*4
        ix=np.clip(((points[:,0]+1)*.5*gw).astype(int),0,gw-1)
        iy=np.clip(((points[:,1]+1)*.5*gh).astype(int),0,gh-1)
        dots=np.zeros((gh,gw),dtype=np.float32)
        np.maximum.at(dots,(iy,ix),np.clip(levels,0,1))
        if dot_mode:
            dots=np.clip((dots-.025)*1.4,0,1)
        else:
            # Keep Braille samples crisp instead of spreading them into nearby
            # cells, which made adjacent dots merge into a soft silhouette.
            dots=np.clip((dots-.035)*1.5,0,1)
        out=['\x1b[?25l\x1b[H']
        masks=np.array([[1,8],[2,16],[4,32],[64,128]],dtype=np.uint16)
        render_h=gh if dot_mode else h
        render_w=gw if dot_mode else w
        for cy in range(render_h):
            last=''
            row=[' ']*left if dot_mode else []
            for cx in range(render_w):
                if dot_mode:
                    value=float(dots[cy,cx])
                    if value<.13:
                        row.append(' '); continue
                    ch='●'
                else:
                    block=dots[cy*4:cy*4+4,cx*2:cx*2+2]
                    value=float(block.max())
                    if value<.16: row.append(' '); continue
                    mask=int(np.sum((block>.16)*masks)); ch=chr(0x2800+mask)
                shade=int(92+163*min(1,value))
                if self.color=='truecolor': code=f'\x1b[38;2;{shade};{shade};{min(255,shade+3)}m'
                elif self.color=='256': code=f'\x1b[38;5;{232+round(value*23)}m'
                else: code='\x1b[37m'
                if code!=last: row.append(code); last=code
                row.append(ch)
            if dot_mode: row.extend([' ']*(w-left-render_w))
            row.append('\x1b[0m'); out.extend(row); out.append('\x1b[K\n')
        for line in hud_lines:
            plain=re.sub(r'\x1b\[[0-9;]*m','',line)
            out.extend([' '*max(0,(w-len(plain))//2),line,'\x1b[K\n'])
        return ''.join(out)

import math

def format_hud(t, phase, count, fps, aspect, debug=False):
    if phase in ('text','rotate','fade'):
        if phase=='text':
            u=max(0,min(1,(t-9)/2)); shade=round(45+210*u*u*(3-2*u))
        elif phase=='fade':
            u=max(0,min(1,(20-t)/5)); shade=round(255*u*u*(3-2*u))
        else:
            shade=255
        color=f'\x1b[1;38;2;{shade};{shade};{shade}m'
        return color+'WILL YOU MARRY ME\nANISHU...?'+'\x1b[0m'
    glints=int(count*.28*(1+1.96*math.sin(math.pi*(t%20)/20)**2))
    lines=[
        '@in_22ee · 2026',
        f' rotation {int((55+t*30)%360):03d}.00°   glints {glints}',
        f' letters {count:,}   {t%20:04.1f}s',
    ]
    if debug: lines[-1]+=f'   {fps:4.1f} fps   ring aspect {aspect:.2f}   {phase}'
    return '\x1b[90m'+'\n'.join(lines)+'\x1b[0m'


"""Terminal lifecycle and non-blocking keyboard input."""
import sys, termios, tty, atexit, select
class Terminal:
    def __enter__(self):
        if not sys.stdout.isatty() or not sys.stdin.isatty(): raise RuntimeError('Run this animation in an interactive terminal.')
        self.fd=sys.stdin.fileno(); self.old=termios.tcgetattr(self.fd); tty.setcbreak(self.fd)
        sys.stdout.write('\x1b[2J\x1b[H\x1b[?25l'); sys.stdout.flush(); atexit.register(self.restore); return self
    def restore(self):
        if getattr(self,'old',None) is not None:
            termios.tcsetattr(self.fd,termios.TCSADRAIN,self.old); self.old=None
            sys.stdout.write('\x1b[0m\x1b[?25h\n'); sys.stdout.flush()
    def key(self):
        if select.select([sys.stdin],[],[],0)[0]: return sys.stdin.read(1)
        return ''
    def __exit__(self,*_): self.restore()


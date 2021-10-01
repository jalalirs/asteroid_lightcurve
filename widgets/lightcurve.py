

class LightCurve:
    inUse = None
    def __init__(self,run):
        self.run = run
        self.metadata = {}
        self.mag = []
        self.jd = []
        self.err = []
    
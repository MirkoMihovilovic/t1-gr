__author__ = "Daniel Calderon"
__license__ = "MIT"

class PerformanceMonitor:

    def __init__(self, currentTime, period):

        self.currentTime = currentTime
        self.timer = 0.0
        self.period = period
        self.framesCounter = 0
        self.framesPerSecond = 0.0
        self.milisecondsPerFrame = 0.0

    def update(self, currentTime):

        self.framesCounter += 1
        self.deltaTime = currentTime - self.currentTime
        self.timer += self.deltaTime
        self.currentTime = currentTime

        if self.timer > self.period:
            self.framesPerSecond = self.framesCounter / self.timer
            self.milisecondsPerFrame = 1000.0 * self.timer / self.framesCounter
            self.framesCounter = 0
            self.timer = 0.0

    def getDeltaTime(self):

        return self.deltaTime

    def getFPS(self):

        return self.framesPerSecond

    def getMS(self):

        return self.milisecondsPerFrame

    def __str__(self):
        return f" [{self.framesPerSecond:.2f} fps - {self.milisecondsPerFrame:.2f} ms]"

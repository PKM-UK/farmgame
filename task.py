class Task():
    # * means a tuple of arguments
    def __init__(self, duration, completion, *callbackargs):
        self.duration = duration
        self.completion = completion
        self.progress = 0
        self.callbackargs = callbackargs

    def update(self, dt):
        self.progress += dt
        if self.progress >= self.duration:
            # * means unpack the tuple
            self.completion(*(self.callbackargs))
            return True
        else:
            #Just for testing - return False really
            print(f"Task is {self.progress / self.duration} complete")
            return False

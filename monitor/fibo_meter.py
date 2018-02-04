
class FiboMeter:

    fibA,fibB = 0,1

    def FiboMeter(self):

        while True:
            self.fibA, self.fibB = self.fibB, self.fibA+self.fibB
            yield self.fibA
    
    def fibo_next(self, current):
        if current > self.fibB:
            self.next()
            return True
        else:
            return False

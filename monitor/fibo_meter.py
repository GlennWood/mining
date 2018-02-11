# FiboMeter is a gadget that returns True less and less frequently with each iteration.
# We use it to send reminder textmsgs less and less frequently as time goes by
def FiboMeter(fibA,fibB,current):

    while True:
        current += 1
        if current > fibB:
            fibA, fibB = fibB, fibA+fibB
            yield True
        yield False
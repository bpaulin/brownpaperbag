from brownpaperbag.bpbgate import BpbGate


class BpbLight:
    def __init__(self, where, gate: BpbGate):
        self.where = str(where)
        self._gate = gate

    def turn_on(self):
        self._gate.turn_on_light(self.where)

    def turn_off(self):
        self._gate.turn_off_light(self.where)

    def is_on(self):
        return self._gate.is_light_on(self.where)
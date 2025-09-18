from .feature import Feature


class X1602(Feature):
    feature_id = 0x1602

    def startSession(self, name):
        return self.construct_and_process_request(0, name)

    def endSession(self, name):
        return self.construct_and_process_request(1, name)

    def passwd0(self, password: str):
        return self.construct_and_process_request(2, password)

    def passwd1(self, password: str):
        return self.construct_and_process_request(3, password)

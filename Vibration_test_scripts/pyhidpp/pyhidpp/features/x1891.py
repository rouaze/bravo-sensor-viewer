from .feature import Feature


class X1891(Feature):
    feature_id = 0x1891

    def RFSendPeriodicMsg(self, address, channel, power, period, condition, nbmsg, radiomode, payloadSize):
        # Extract each byte of the 5-byte 'address' variable
        address_byte1 = (address >> 32) & 0xFF  # Most significant byte
        address_byte2 = (address >> 24) & 0xFF
        address_byte3 = (address >> 16) & 0xFF
        address_byte4 = (address >> 8) & 0xFF
        destinationAddress = address & 0xFF  # Least significant byte

        # Extract each byte of the 2-byte 'nbMsg' variable
        nbmsg_byte1 = (nbmsg >> 8) & 0xFF  # Most significant byte
        nbmsg_byte2 = nbmsg & 0xFF  # Least significant bytenbMsg_bytes = [nbMsg_byte1, nbMsg_byte2]
        
        return self.construct_and_process_request(0, [address_byte1, 
                                                      address_byte2, 
                                                      address_byte3, 
                                                      address_byte4, 
                                                      destinationAddress,
                                                      channel, 
                                                      power, 
                                                      period, 
                                                      condition, 
                                                      nbmsg_byte1, 
                                                      nbmsg_byte2, 
                                                      radiomode, 
                                                      payloadSize]).params

    def RFTxCW(self, channel, power, timeout, condition, radiomode):
        timeout_MSB = (timeout >> 8) & 0xFF  # Extract the most significant byte
        timeout_LSB = timeout & 0xFF         # Extract the least significant byte

        self.construct_and_process_request(1, [channel, 
                                               power, 
                                               timeout_MSB, 
                                               timeout_LSB, 
                                               condition, 
                                               radiomode])
    
    def RFRxContinuous(self, channel, power, timeout, condition, radiomode):
        timeout_MSB = (timeout >> 8) & 0xFF  # Extract the most significant byte
        timeout_LSB = timeout & 0xFF         # Extract the least significant byte
        
        self.construct_and_process_request(2, [channel, 
                                               power, 
                                               timeout_MSB, 
                                               timeout_LSB, 
                                               condition, 
                                               radiomode])

    def SetRfTxCWSweep(self, channelmin, channelmax, power, sweepperiod, condition, radiomode, nbsweep):
        nbsweep_MSB = (nbsweep >> 8) & 0xFF  # Extract the most significant byte
        nbsweep_LSB = nbsweep & 0xFF         # Extract the least significant byte
        
        self.construct_and_process_request(3, [channelmin, 
                                               channelmax, 
                                               power, 
                                               sweepperiod, 
                                               condition, 
                                               radiomode, 
                                               nbsweep_MSB, 
                                               nbsweep_LSB])

    def SetRfRxContinuousSweep(self, channelmin, channelmax, power, sweepperiod, condition, radiomode, nbsweep):
        nbsweep_MSB = (nbsweep >> 8) & 0xFF  # Extract the most significant byte
        nbsweep_LSB = nbsweep & 0xFF         # Extract the least significant byte

        self.construct_and_process_request(4, [channelmin, 
                                               channelmax, 
                                               power, 
                                               sweepperiod, 
                                               condition, 
                                               radiomode, 
                                               nbsweep_MSB, 
                                               nbsweep_LSB])

    def RFSendPeriodicMsgNoAck(self, address, channel, power, period, condition, nbmsg, radiomode, payloadSize):
        # Extract each byte of the 5-byte 'address' variable
        address_byte1 = (address >> 32) & 0xFF  # Most significant byte
        address_byte2 = (address >> 24) & 0xFF
        address_byte3 = (address >> 16) & 0xFF
        address_byte4 = (address >> 8) & 0xFF
        destinationAddress = address & 0xFF  # Least significant byte

        # Extract each byte of the 2-byte 'nbMsg' variable
        nbmsg_byte1 = (nbmsg >> 8) & 0xFF  # Most significant byte
        nbmsg_byte2 = nbmsg & 0xFF  # Least significant bytenbMsg_bytes = [nbMsg_byte1, nbMsg_byte2]
        
        self.construct_and_process_request(5, [address_byte1, 
                                               address_byte2, 
                                               address_byte3, 
                                               address_byte4, 
                                               destinationAddress, 
                                               channel, 
                                               power, 
                                               period, 
                                               condition, 
                                               nbmsg_byte1, 
                                               nbmsg_byte2, 
                                               radiomode, 
                                               payloadSize])

    def RFReceivePeriodicMsg(self, address, channel, power, condition, timeout, radiomode):
        # Extract each byte of the 5-byte 'address' variable
        address_byte1 = (address >> 32) & 0xFF  # Most significant byte
        address_byte2 = (address >> 24) & 0xFF
        address_byte3 = (address >> 16) & 0xFF
        address_byte4 = (address >> 8) & 0xFF
        destinationAddress = address & 0xFF  # Least significant byte

        timeout_MSB = (timeout >> 8) & 0xFF  # Extract the most significant byte
        timeout_LSB = timeout & 0xFF         # Extract the least significant byte

        self.construct_and_process_request(6, [address_byte1, 
                                               address_byte2, 
                                               address_byte3, 
                                               address_byte4, 
                                               destinationAddress, 
                                               channel, 
                                               power, 
                                               condition, 
                                               timeout_MSB, 
                                               timeout_LSB, 
                                               radiomode])
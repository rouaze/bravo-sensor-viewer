from .feature import Feature
from ..core.utils import u16_to_list_be
import time

# DEVLOPMENT FEATURE ONLY - FOR ENG PURPOSE
# https://docs.google.com/document/d/1FyznUkKKdmIKMyHuwwRH4UedVOzC73d2lV8UYCxOjG4/edit#heading=h.mn4ob8ygrtd3   
# 
class X920B(Feature):
    feature_id = 0x920b
    
    # [0] getCapabilities() → cmd, analogKeyNbr, LEDnbr, GTechFWinfo, kbdLayout
    def getCapabilities(self):
        res = self.construct_and_process_request(function_nb=0, params=[])
        return res

    # [1] setDataCmd(cmdAddr, cmdInfo, infoNbr, offset, data)
    def setDataCmd(self, cmdAddr, cmdInfo, infoNbr, offset, data):
        """
            Send a “set” GTech command specified by its address.
            See the “Hall Driver MCU, Technical Specification, 002_000_0A,  V1.03, 29 June 2023”.
        """
        payload = [cmdAddr, cmdInfo, infoNbr, offset]
        payload.extend(data)
        res = self.construct_and_process_request(function_nb=1, params=payload)
        return None

    # [2] getDataCmd(cmdAddr, cmdInfo)
    def getDataCmd(self, cmdAddr, cmdInfo, mode=0x00):
        """
            Read back the settings values from GTech internal registers.
            The data values are sent through the readDataSettingEvent notification.
            The number of the notifications sent is equal to the number of GTECH sensors used.
        """
        payload = [cmdAddr, cmdInfo, mode]
        res = self.construct_and_process_request(function_nb=2, params=payload)
        return None

    # [3] setLedCmd(infoNbr, offset, ledRed, ledGreen, ledBlue, ledBrightness)
    def setLedCmd(self, infoNbr, offset, data):
        """
        data = [R, G, B, Bright] x infoNb
        """
        payload = [infoNbr, offset]
        payload.extend(data)
        res = self.construct_and_process_request(function_nb=3, params=payload)
        return None

    # [4] setMonitorTest(count, threshold, cmdAddr, cmdInfo, infoNbr, offset)
    def setMonitorTest(self, count, trigger, cmdAdd, cmdInfo, infoNbr, offset):
        """
            Start monitor Test, returning various real time information. 
            Once the monitor test is launched, a total of count events monitorTestEvent will be sent (see event description) in HID++.
            To abort the test before completion, call setMonitorTest again with count = 0.
        """
        payload = u16_to_list_be(count)
        payload.append(trigger)
        payload.append(cmdAdd)
        payload.append(cmdInfo)
        payload.append(infoNbr)
        payload.append(offset)
        res = self.construct_and_process_request(function_nb=4, params=payload)
        return None

    # [5] resetSlaveMCU()
    def resetSlaveMCU(self):
        """
            Reset the slave MCU and reload registers with application values.
            After a sensor reset, slave MCU restarts in user mode.
        """
        res = self.construct_and_process_request(function_nb=5, params=[])
        return None

    # [6] suspendSlaveMCU(scanRate)
    def suspendSlaveMCU(self, scanRate):
        """
            0x00: Disable wakeup
            0x01: Enable wakeup, 100[ms] scan rate.
            0x02: Enable wakeup, 150[ms] scan rate.
            0x03: Enable wakeup, 200[ms] scan rate.
            0x04: Enable wakeup, 250[ms] scan rate.
            0x05: Enable wakeup, 300[ms] scan rate.
            0x06: Enable wakeup, 350[ms] scan rate.
            0x07: Enable wakeup, 400[ms] scan rate.
            0x08: Enable wakeup, 450[ms] scan rate.
            0x09: Enable wakeup, 500[ms] scan rate.
            0x0A: Enable wakeup, 550[ms] scan rate.
        """
        res = self.construct_and_process_request(function_nb=6, params=[scanRate, 0, 0])
        return None

    # [7] wakeUpSlaveMCU()
    def wakeUpSlaveMCU(self):
        """
            Restarts slave MCU after a suspend Slave MCU function.
        """
        res = self.construct_and_process_request(function_nb=7, params=[])
        return None

    # [8] shutdownSlaveMCU()
    def shutdownSlaveMCU(self):
        """
        Switch off GTECH functionality. Power supply of MCU slave and GTech IC chains is switched off. To recover GTech functionality send the resetSlaveMCU commands 
        """
        res = self.construct_and_process_request(function_nb=8, params=[])
        return None

    # [9] startCalibration()
    def startCalibration(self):
        """
        https://docs.google.com/document/d/1Fu3wunR2mhJM-lr8dhoQH3NZ_nW_Mrnckwe1Nh3Vncw/edit#heading=h.a73ylsep80xu 
        """
        res = self.construct_and_process_request(function_nb=9, params=[])
        return None

    # [10] stopCalibration(status)
    def stopCalibration(self, success=False):
        """
        https://docs.google.com/document/d/1Fu3wunR2mhJM-lr8dhoQH3NZ_nW_Mrnckwe1Nh3Vncw/edit#heading=h.a73ylsep80xu 
        """
        status = 1 if success else 0
        res = self.construct_and_process_request(function_nb=10, params=[status, 0, 0])
        return None

    # [11] stopKeyProcess(status)
    def stopKeyProcess(self, stop=True):
        """
        https://docs.google.com/document/d/1Fu3wunR2mhJM-lr8dhoQH3NZ_nW_Mrnckwe1Nh3Vncw/edit#heading=h.a73ylsep80xu 
        """
        status = 1 if stop else 0
        res = self.construct_and_process_request(function_nb=11, params=[status, 0, 0])
        return res

    



    
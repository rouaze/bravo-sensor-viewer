import logging
import os

from .encryption import AESCipher


from ..core.connected_device import ConnectedDevice


class SecurityManager:
    """Manage the secure access to TDE for secure devices"""

    hidpp: ConnectedDevice
    cipher: AESCipher

    def __init__(self, hidpp: ConnectedDevice, tdeOffuscatedFileName="passwords_enc_mecha.ini"):
        # The device we will interact with
        self.hidpp = hidpp
        # We need the tde offuscated file name.
        self.tdeOffuscatedFileName = tdeOffuscatedFileName
        # We need to know if we are authorised to perform the security process
        self.authentificatedUser = os.path.isfile(self.tdeOffuscatedFileName)
        if self.authentificatedUser:
            self.cipher = AESCipher(tdeOffuscatedFileName)
        # We will decrypt the json and store the content
        self.clearTdeDict = None
        # We need the FwName
        self.fwName = ""
        # We have to know the authentificationFeatureIndex when the device is protected
        self.authFeatureIndex = -1
        self.device_protected = False
        self.session_name = ""
        self.compl_session_name = "x1E02_Compl"
        self.manuf_session_name = "x1E02_Manuf"
        self.session_name_bytes = [ord(c) for c in self.session_name]
        self.session_pwd = None
        self.log = logging.getLogger("hidpp")

    def fetch_manuf(self):
        """Parse the clear dictionary according to the device authFeatureIndex and load
        the correspondings data phase(s).
        Will fail if the user is not already autentificated.
        Will fail if the Json dictionnary was not loaded first.
        """
        if not self.authentificatedUser:
            return
        # Set the key we are looking for
        manuf_pwd = self.cipher.decrypt(self.fwName, self.session_name)
        # Try to found the key in the dict
        if manuf_pwd:
            self.session_pwd = manuf_pwd

    def get_authentification_feature_index(self):
        """We get the feature for the authentification.
        Return negative value in case of error.
        """
        self.log.debug(f"connected: {self.hidpp.connected}")
        self.device_protected = self.hidpp.enumerate_feature(0x1E02)
        if not self.device_protected:
            self.log.debug("feature 1e02 not found...")
            return
        self.authFeatureIndex = self.hidpp.features.x1E02.get_react_info()
        if self.authFeatureIndex:
            self.log.debug(
                f"The feature index for the authentification is: 0X{self.authFeatureIndex:04X}"
            )
            if self.hidpp.enumerate_feature(self.authFeatureIndex):
                # pass
                self.log.debug(
                    f"We confirm the authentification feature: 0X{self.authFeatureIndex:04X}"
                )
            else:
                self.log.debug(
                    f"Bad we did not found the feature 0X{self.authFeatureIndex:04X}!"
                )
                self.authFeatureIndex = None

    def open(self):
        """Open a manufacturing session."""
        if not self.device_protected:
            return True  # Device not protected.
        if not self.authentificatedUser:
            return False  # Device protected but the user is not authentified.
        # For the moment we only support one authentification method
        if self.authFeatureIndex != 0x1602:
            return False
        # Here we are...
        return self.open1602()

    def close(self):
        """Close the manufacturing session."""
        if not self.hidpp.enumerate_feature(0x1E02):
            return True  # Device not protected.
        if not self.authentificatedUser:
            return False  # Device protected but the user is not authentified.
        # For the moment we only support one authentification method
        if self.authFeatureIndex != 0x1602:
            return False
        return self.close1602()

    def open1602(self):
        """Open a manufacturing session with the security feature 0x1602.
        return True in case of success.
        Will fail if the user is not already autentificated.
        """
        if not self.authentificatedUser:
            return False
        
        res = self.hidpp.features.x1602.startSession(self.session_name_bytes)
        if res:
            self.log.debug(res.params[0])  # we expect 0x01
        else:
            self.log.debug("Manager: open1602 dp1 fail")
            return False
        res = self.hidpp.features.x1602.passwd0(self.session_pwd)
        if res:
            self.log.debug(res.params[0])  # we expect x02
            return True
        else:
            self.log.debug("Manager: open1602 dp2 fail")
            return False

    def close1602(self):
        """
        Close a manufacturing session previously open with the security feature 0x1602.
        Will fail if the user is not already autentificated.
        """
        if not self.authentificatedUser:
            return False
        res = self.hidpp.features.x1602.endSession(self.session_name_bytes)
        if not res:
            self.log.debug("Manager: We fail to close the session.")
        return res

    def enable_deactivatable_features(self):
        """Enable deactivatable features for manufacturing."""
        bitfield = 0
        if self.session_name == self.compl_session_name:
            bitfield = 2
        elif self.session_name == self.manuf_session_name:
            bitfield = 1
        res = self.hidpp.features.x1E02.enable_features(bitfield)
        self.log.debug(res)
        # Check the status for the deactivatable features for manufacturing.
        [_, _, state_bit_map] = self.hidpp.features.x1E02.get_info()
        if res is not None:
            manufHidpp_flag = bool(state_bit_map & bitfield)
            if manufHidpp_flag:
                self.log.debug(
                    "successfully activated deactivable features for manufacturing"
                )
            else:
                self.log.debug("error in activating features")
            return manufHidpp_flag
        self.log.debug("none when requesting status of deactivable features")
        return -1

    def disable_deactivatable_features(self):
        """Disable deactivatable features for manufacturing."""
        bitfield = 0
        if self.session_name == self.compl_session_name:
            bitfield = 2
        elif self.session_name == self.manuf_session_name:
            bitfield = 1
        self.hidpp.features.x1E02.disable_features(bitfield)

    def is_using_deactivatable_features(self):
        """Return True if the device is using a security management."""
        return self.hidpp.enumerate_feature(0x1E02)

    def is_protected(self):
        """Return True if the device is using a security management."""
        if self.hidpp.enumerate_feature(0x1E02):
            return True
        else:
            return False

    def set_active_fw_name(self, fwName):
        """Set the FirmwareName we want to use"""
        self.fwName = fwName

    def look_for_active_fw_name(self):
        """Helper function, could be used to get the Fw Name."""
        ans = "nobody"
        reply = self.hidpp.features.x0003.get_device_info()
        if reply is not None:
            # print(f"reply = {reply}")
            entityCnt = reply.entity_count
        else:
            return "nobody"

        for entity in range(entityCnt):
            fw_info = self.hidpp.features.x0003.get_fw_info(entity)
            # print(f"firmware name = {fwName} active = {active}")
            if fw_info.active:
                ans = fw_info.fw_name
                break
        return ans

    def set_session_name(self, sessionName):
        self.session_name = sessionName
        self.session_name_bytes = [ord(c) for c in self.session_name]

    def unlock_device(self, mode = 'MANUF'):
        self.hidpp.features.x1E00.set_enable_hidden_features(True)
        self.get_authentification_feature_index()
        if mode == 'MANUF':
            self.set_session_name(self.manuf_session_name)
            firmWareName = self.look_for_active_fw_name()
            self.set_active_fw_name(firmWareName)
            if self.device_protected:
                if self.authentificatedUser:
                    self.fetch_manuf()
                    self.open()
                    self.enable_deactivatable_features()
                else:
                    self.log.error("You are not authentificated.")
        elif mode == 'COMPL':
            self.set_session_name(self.compl_session_name)
            self.set_active_fw_name('Compliance')
            if self.device_protected:
                if self.authentificatedUser:
                    self.fetch_manuf()
                    self.open()
                    self.enable_deactivatable_features()
                else:
                    self.log.error("You are not authentificated.")
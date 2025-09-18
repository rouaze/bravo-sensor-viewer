from .feature import Feature

class X19C0(Feature):
    """Force Sensing Button feature (0x19C0)
    
    This feature allows configuration of force sensing button thresholds.
    Provides access to L1 and L2 threshold values in ADC counts.
    """
    feature_id = 0x19C0

    def get_capabilities(self):
        """Get device general capabilities
        
        Returns:
            numButtons: Number of buttons supported by the device
        """
        res = self.construct_and_process_request(0, [])
        if res is None:
            return None
            
        if not hasattr(res, 'params') or len(res.params) < 1:
            print(f"ERROR: Invalid capabilities response - expected 1+ params, got {len(res.params) if hasattr(res, 'params') else 0}")
            return None
            
        try:
            num_buttons = res.params[0]
            return num_buttons
        except (IndexError, TypeError) as e:
            print(f"ERROR: Failed to parse capabilities data: {e}")
            return None

    def get_button_capabilities(self, button_id):
        """Returns the supported sensing button capabilities
        
        Args:
            button_id: Button ID (0..numButtons-1)
            
        Returns:
            tuple: (capabilities, defaultForce, maxForce, minForce, numOfThresholds)
        """
        res = self.construct_and_process_request(1, [button_id])
        if res is None:
            return None
            
        if not hasattr(res, 'params') or len(res.params) < 9:
            print(f"ERROR: Invalid button capabilities response - expected 9+ params, got {len(res.params) if hasattr(res, 'params') else 0}")
            return None
            
        try:
            # Parse capabilities (2 bytes)
            capabilities = (res.params[0] << 8) | res.params[1]
            
            # Parse force values (2 bytes each)
            default_force = (res.params[2] << 8) | res.params[3]
            max_force = (res.params[4] << 8) | res.params[5]
            min_force = (res.params[6] << 8) | res.params[7]
            
            # Parse number of thresholds
            num_of_thresholds = res.params[8]
            
            return (capabilities, default_force, max_force, min_force, num_of_thresholds)
        except (IndexError, TypeError) as e:
            print(f"ERROR: Failed to parse button capabilities data: {e}")
            return None

    def get_button_config(self, button_id):
        """Returns the current button configuration
        
        Args:
            button_id: Button ID (0..numButtons-1)
            
        Returns:
            tuple: (l1_threshold, l2_threshold) - L1 and L2 threshold values in ADC counts
        """
        res = self.construct_and_process_request(2, [button_id])
        if res is None:
            return None
            
        if not hasattr(res, 'params') or len(res.params) < 4:
            print(f"ERROR: Invalid button config response - expected 4+ params, got {len(res.params) if hasattr(res, 'params') else 0}")
            return None
            
        try:
            # Parse L1 threshold (2 bytes, MSB first)
            l1_threshold = (res.params[0] << 8) | res.params[1]
            
            # Parse L2 threshold (2 bytes, MSB first)  
            l2_threshold = (res.params[2] << 8) | res.params[3]
            
            return (l1_threshold, l2_threshold)
        except (IndexError, TypeError) as e:
            print(f"ERROR: Failed to parse button config data: {e}")
            return None

    def set_button_config(self, button_id, l1_threshold, l2_threshold):
        """Set the button configuration
        
        Args:
            button_id: Button ID (0..numButtons-1)
            l1_threshold: L1 threshold value in ADC counts
            l2_threshold: L2 threshold value in ADC counts
            
        Returns:
            tuple: (button_id, l1_threshold, l2_threshold) - Echo of applied values
        """
        # Split 16-bit values into MSB and LSB
        l1_msb = (l1_threshold >> 8) & 0xFF
        l1_lsb = l1_threshold & 0xFF
        l2_msb = (l2_threshold >> 8) & 0xFF
        l2_lsb = l2_threshold & 0xFF
        
        res = self.construct_and_process_request(3, [button_id, l1_msb, l1_lsb, l2_msb, l2_lsb])
        if res is None:
            return None
            
        if not hasattr(res, 'params') or len(res.params) < 5:
            print(f"ERROR: Invalid set config response - expected 5+ params, got {len(res.params) if hasattr(res, 'params') else 0}")
            return None
            
        try:
            # Parse response
            echo_button_id = res.params[0]
            echo_l1 = (res.params[1] << 8) | res.params[2]
            echo_l2 = (res.params[3] << 8) | res.params[4]
            
            return (echo_button_id, echo_l1, echo_l2)
        except (IndexError, TypeError) as e:
            print(f"ERROR: Failed to parse set config response: {e}")
            return None

    def reset_button_config(self, button_id):
        """Reset button configuration to default values
        
        Args:
            button_id: Button ID (0..numButtons-1)
            
        Returns:
            tuple: (l1_threshold, l2_threshold) - Default threshold values
        """
        res = self.construct_and_process_request(4, [button_id])
        if res is None:
            return None
            
        if not hasattr(res, 'params') or len(res.params) < 4:
            print(f"ERROR: Invalid reset config response - expected 4+ params, got {len(res.params) if hasattr(res, 'params') else 0}")
            return None
            
        try:
            # Parse default thresholds
            l1_threshold = (res.params[0] << 8) | res.params[1]
            l2_threshold = (res.params[2] << 8) | res.params[3]
            
            return (l1_threshold, l2_threshold)
        except (IndexError, TypeError) as e:
            print(f"ERROR: Failed to parse reset config response: {e}")
            return None
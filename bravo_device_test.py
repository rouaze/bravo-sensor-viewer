#!/usr/bin/env python3
"""
Simple test script for Bravo device to explore available features and functionality
"""

import sys
import logging
from pyhidpp.core.devices_manager import DevicesManager
from pyhidpp.security import SecurityManager

def test_device_discovery():
    """Test device discovery and connection"""
    print("=== DEVICE DISCOVERY TEST ===")
    
    dev_manager = DevicesManager(log_to_console=True, log_level=logging.INFO)
    
    # Try to connect to known devices
    compatible_devices = ["Bravo", "Malacca", "MX Master 3", "MX Master"]
    connected_device = None
    
    for device_name in compatible_devices:
        print(f"Trying to connect to: {device_name}")
        device = dev_manager.connect_with_name(device_name)
        if device:
            print(f"✅ Successfully connected to: {device_name}")
            connected_device = device
            break
        else:
            print(f"❌ Could not connect to: {device_name}")
    
    return connected_device

def explore_device_info(device):
    """Explore basic device information"""
    print("\n=== DEVICE INFO EXPLORATION ===")
    
    if not device:
        print("❌ No device connected")
        return False
    
    # Basic device info
    print(f"Device connected: {device.connected}")
    
    if hasattr(device, 'device_info'):
        info = device.device_info
        print(f"Product Name: {getattr(info, 'product_name', 'Unknown')}")
        print(f"Serial: {getattr(info, 'serial', 'Unknown')}")
        print(f"PID: 0x{getattr(info, 'pid', 0):04X}")
        print(f"VID: 0x{getattr(info, 'vid', 0):04X}")
        print(f"Sub Index: {getattr(info, 'sub_idx', 'Unknown')}")
    
    return True

def explore_features(device):
    """Explore available features"""
    print("\n=== FEATURE EXPLORATION ===")
    
    try:
        # Enumerate all features
        device.enumerate_all()
        
        if hasattr(device.device_info, 'features'):
            features = device.device_info.features
            print(f"Available Features: {len(features)}")
            
            for feat_id, feat_info in features.items():
                print(f"  * Feature 0x{feat_id:04X} at index {feat_info.idx}")
                
                # Try to get feature name if possible
                if hasattr(feat_info, 'name'):
                    print(f"    Name: {feat_info.name}")
        else:
            print("❌ No features information available")
            
    except Exception as e:
        print(f"❌ Error during feature enumeration: {e}")

def test_basic_features(device):
    """Test basic HID++ features that should be available on most devices"""
    print("\n=== BASIC FEATURE TESTS ===")
    
    # Test Feature 0x0000 (Root feature - should always be available)
    try:
        print("Testing Feature 0x0000 (Root)...")
        if hasattr(device, 'features') and hasattr(device.features, 'x0000'):
            root_feature = device.features.x0000
            print("✅ Root feature accessible")
            
            # Try to get feature count
            try:
                feature_count = root_feature.get_feature(0)
                print(f"✅ Feature count: {feature_count}")
            except Exception as e:
                print(f"⚠️ Could not get feature count: {e}")
                
        else:
            print("❌ Root feature not accessible through device.features")
            
    except Exception as e:
        print(f"❌ Error testing root feature: {e}")
    
    # Test Feature 0x0005 (Device Name - if available)
    try:
        print("\nTesting Feature 0x0005 (Device Name)...")
        if hasattr(device, 'features') and hasattr(device.features, 'x0005'):
            name_feature = device.features.x0005
            device_name = name_feature.get_device_name(0)
            print(f"✅ Device name: {device_name}")
        else:
            print("⚠️ Device name feature not available")
            
    except Exception as e:
        print(f"❌ Error getting device name: {e}")

def test_security_unlock(device):
    """Test security unlock functionality"""
    print("\n=== SECURITY TEST ===")
    
    try:
        # Look for password file
        password_files = [
            "./Vibration_test_scripts/passwords_enc_mecha.ini",
            "./passwords_enc_mecha.ini",
            "passwords_enc_mecha.ini"
        ]
        
        password_file = None
        for pf in password_files:
            try:
                with open(pf, 'r'):
                    password_file = pf
                    break
            except:
                continue
        
        if password_file:
            print(f"Found password file: {password_file}")
            security_manager = SecurityManager(device, tdeOffuscatedFileName=password_file)
            
            result = security_manager.unlock_device()
            print(f"Unlock result: {result}")
            
            if result is None:
                print("✅ Device unlocked successfully")
            else:
                print(f"⚠️ Unlock returned: {result}")
        else:
            print("⚠️ No password file found, skipping security test")
            
    except Exception as e:
        print(f"❌ Error during security unlock: {e}")

def main():
    """Main test function"""
    print("🔍 BRAVO DEVICE FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Connect to device
    device = test_device_discovery()
    
    if not device:
        print("❌ No compatible device found. Please check connections.")
        return
    
    try:
        # Run tests
        explore_device_info(device)
        explore_features(device)
        test_basic_features(device)
        test_security_unlock(device)
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        
    finally:
        # Clean up
        if device:
            print("\nDisconnecting device...")
            device.disconnect()

if __name__ == "__main__":
    main()
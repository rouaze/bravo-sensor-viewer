#!/usr/bin/env python3
"""
Simple console test to verify sensor is working continuously
"""

import time
import logging
from pyhidpp.core.devices_manager import DevicesManager
from pyhidpp.security import SecurityManager
from pyhidpp.features.x9402 import X9402

def test_continuous_readings():
    """Test continuous sensor readings in console"""
    
    print("🔍 Simple Sensor Test - Console Output")
    print("=" * 50)
    
    try:
        # Connect to device
        dev_manager = DevicesManager(log_to_console=False, log_level=logging.WARNING)
        mouse = dev_manager.connect_with_name("Bravo")
        
        if not mouse:
            print("❌ Could not connect to Bravo device")
            return
        
        print("✅ Connected to Bravo")
        
        # Security unlock
        security_manager = SecurityManager(mouse, tdeOffuscatedFileName="./Vibration_test_scripts/passwords_enc_mecha.ini")
        unlock_result = security_manager.unlock_device()
        print(f"Unlock result: {unlock_result}")
        
        # Enumerate features
        mouse.enumerate_all()
        
        # Initialize sensor
        sensor = X9402(mouse)
        
        # Test initial reading
        test_result = sensor.read_measurement(0)
        print(f"Initial sensor reading: {test_result}")
        
        if test_result is None:
            print("❌ Sensor not responding")
            return
        
        # Continuous reading test
        print("\n🔄 Starting continuous reading test (press Ctrl+C to stop)...")
        print("Format: [Reading#] ADC: val, Baseline: bl, Preload: pl")
        print("-" * 60)
        
        reading_count = 0
        
        while True:
            reading_count += 1
            
            # Read sensor
            result = sensor.read_measurement(0)
            
            if result is None:
                print(f"[{reading_count}] ❌ No data")
            else:
                val, bl, pl = result
                print(f"[{reading_count:3d}] ADC: {val:4d}, Baseline: {bl:4d}, Preload: {pl:3d}")
            
            # Wait before next reading
            time.sleep(0.1)  # 10 Hz
            
            # Stop after 100 readings for safety
            if reading_count >= 100:
                print("\n✅ Test completed (100 readings)")
                break
                
    except KeyboardInterrupt:
        print(f"\n⏹️ Test stopped by user after {reading_count} readings")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'mouse' in locals():
            mouse.disconnect()
            print("🔌 Device disconnected")

if __name__ == "__main__":
    test_continuous_readings()
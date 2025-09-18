from pyhidpp.pyhidpp.core.devices_manager import DevicesManager
from pyhidpp.pyhidpp.security import SecurityManager
from x9401 import X9401


haptic_feature = 0
def unlockMouse():
    global sense_vals
    global rest_vals
    global mouse
    global haptic_feature
    dev_manager = DevicesManager()
    compatible_mice = ["Malacca","Bravo"]
    for mouse_name in compatible_mice:
        mouse = dev_manager.connect_with_name(mouse_name)
        if mouse!=None: 
            break
    if mouse == None:
        print("No Malacca found.")
        exit()

    securityManager = SecurityManager(mouse)
    try:
        securityManager.unlock_device()
        print("Malacca unlocked.")
    except KeyError:
        print("Password not present in the password file.")
    sense_vals = []
    rest_vals = []
    haptic_feature = X9401(mouse)


unlockMouse()


ans = input("Press enter to play first waveform\n")

if "n" in ans:
    exit()

while True:
    wfnum = 30
    print(f"Playing waveform {wfnum}")

    haptic_feature.playWaveform(wfnum,100)

    ans = input("r + enter to repeat, enter to continue\n")
    if "r" in ans:
        continue
    else:
        break
    
wfnum+= 1
while True:
    print(f"Playing waveform {wfnum}")

    haptic_feature.playWaveform(wfnum,100)

    ans = input("r + enter to repeat, enter to continue\n")
    if "r" in ans:
        continue
    else:
        break

wfnum+= 1
while True:
    print(f"Playing waveform {wfnum}")

    haptic_feature.playWaveform(wfnum,100)

    ans = input("r + enter to repeat, enter to continue\n")
    if "r" in ans:
        continue
    else:
        break

wfnum+= 1
while True:
    print(f"Playing waveform {wfnum}")

    haptic_feature.playWaveform(wfnum,100)

    ans = input("r + enter to repeat, enter to continue\n")
    if "r" in ans:
        continue
    else:
        break

mouse.disconnect()
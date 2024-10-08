# User Manual for the Muscle Gesture Reading Device with EMG Sensor

## Table of Contents

1. [Introduction](#introduction)
2. [System Components](#system-components)
3. [System Installation](#system-installation)
4. [Preparation for Use](#preparation-for-use)
5. [Using the Device](#using-the-device)
6. [Sensor Placement on Key Muscles](#sensor-placement-on-key-muscles)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

This manual is designed to guide users in operating a muscle gesture reading device using an electromyographic (EMG) sensor. The device enables the recognition and translation of muscle gestures into commands that can be used to interact with a computer or other devices.

---

## System Components

1. **EMG Sensor (MyoWare)**: Captures electrical signals generated by the muscles.
2. **arduino RP2040 Connect**: Processor responsible for receiving and processing the EMG signals.
3. **Cables and Electrodes**: Connect the EMG sensor to the user.
4. **Edge Impulse Software**: Performs processing and classification of muscle gestures.

---

## System Installation

1. **Sensor Mounting**:
   - Connect the cables to the EMG sensor and ensure that the electrodes are properly placed on the skin.
   - Position the electrodes over the desired muscle (e.g., forearm).

2. **Hardware Connection**:
   - Connect the EMG sensor to the arduino RP2040 Connect using the appropriate ports.
   - Connect the arduino to a power source (micro-USB cable).

3. **Software Installation**:
   - Run the Python code to execute the software.

---

## Preparation for Use

1. **Skin Cleaning**:
   - Before placing the electrodes, clean the skin area with alcohol to ensure proper contact.

2. **Electrode Placement**:
   - Place the electrodes on the muscle to be monitored.
   - Ensure the electrodes are firmly attached to avoid signal interference.

3. **Connection Verification**:
   - Ensure all cables are properly connected.
   - Check the connection of the device to the computer.

---

## Using the Device

1. **Power On**:
   - Connect the device to the power source.
   - Start the .py software.

2. **Gesture Capture**:
   - Perform the muscle gestures as trained (e.g., hand movements or forearm contractions).
   - The device will detect the movements and send signals to the software.

3. **Gesture Classification**:
   - The model created in Edge Impulse will classify gestures in real-time.
   - The result will be displayed on the screen and can be used as keyboard commands or other interactions.

4. **Custom Commands**:
   - Configure custom gestures according to your needs in the gesture recognition software.

---

## Sensor Placement on Key Muscles

### Biceps Brachii:
- **Function**: Elbow flexion.
- **Location**: Front of the upper arm.
- **How to Locate**: Flex the elbow against resistance and place the sensor in the center of the muscle.

### Triceps Brachii:
- **Function**: Elbow extension.
- **Location**: Back of the upper arm.
- **How to Locate**: Extend the elbow against resistance and place the sensor on the thickest part of the muscle.

### Brachioradialis:
- **Function**: Assists in elbow flexion and forearm pronation.
- **Location**: Upper forearm, near the elbow.
- **How to Locate**: Flex the elbow against resistance and place the sensor on the outer side of the forearm.

### Forearm Flexors:
- **Function**: Wrist and finger flexion.
- **Location**: Inner side of the forearm.
- **How to Locate**: With the palm facing up, make a fist and place the sensor just below the elbow crease.

### Forearm Extensors:
- **Function**: Wrist and finger extension.
- **Location**: Outer side of the forearm.
- **How to Locate**: Extend the fingers or wrist against resistance and place the sensor on the thickest part of the muscle group.

### Finger Flexors:
- **Function**: Finger flexion.
- **Location**: Inner forearm, near the wrist.
- **How to Locate**: With the palm facing up, close the fingers into a fist and place the sensor slightly above the wrist.

---

## Maintenance

1. **Electrode Cleaning**:
   - Clean the electrodes with isopropyl alcohol after each use.
   - Replace electrodes when signs of wear are evident.

2. **Storage**:
   - Disconnect the device and store it in a dry and clean place when not in use.

---

## Troubleshooting

- **The device does not power on**:
  - Check the USB cable connection and power source.
  
- **Gestures are not recognized**:
  - Ensure electrodes are properly placed and skin is clean.
  
- **The device shows interference**:
  - Ensure cables are not tangled and electrodes have good contact with the skin.

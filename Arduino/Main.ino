#include <Tesis_EMG_inferencing.h>
#include <ArduinoBLE.h>

BLEService sensorService("12345678-1234-5678-1234-56789abcdef0"); // UUID del servicio
BLEIntCharacteristic sensorCharacteristic("abcdef01-1234-5678-1234-56789abcdef0", BLERead | BLENotify); // UUID de la característica

//#define FREQUENCY_HZ        EI_CLASSIFIER_FREQUENCY
#define FREQUENCY_HZ 200
#define INTERVAL_MS (1000 / (FREQUENCY_HZ))

static unsigned long last_interval_ms = 0;
// to classify 1 frame of data you need EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE values
float features[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];
// keep track of where we are in the feature array
size_t feature_ix = 0;

// Analog pin connected to your sensor
const int analogPin = 14;
const float conversion_factor = 3.3f / (1 << 12);

void setup() {
  //--------------------------------------------------------------------------------
  Serial.begin(115200);
  // -------------------------- Inicializa el BLE ----------------------------------
  if (!BLE.begin()) {
    Serial.println("Starting BLE failed!");
    while (1);
  }
  //--------------------------------------------------------------------------------
  // Define el nombre del dispositivo y el servicio BLE
  BLE.setLocalName("Sensor-BLE");
  BLE.setDeviceName("EMGType");
  BLE.setAdvertisedService(sensorService);

  // Agrega la característica al servicio y el servicio al BLE
  sensorService.addCharacteristic(sensorCharacteristic);
  BLE.addService(sensorService);

  // Configura la característica con un valor inicial
  sensorCharacteristic.writeValue(' '); // Inicializa con un espacio en blanco
  // Empieza a anunciar el servicio
  BLE.advertise();
  Serial.println("BLE device active, waiting for connections...");
  
  //--------------------------------------------------------------------------------
  analogReadResolution(12);
  Serial.println("Started");
  Serial.println("Edge Impulse Inferencing Demo");
  Serial.println(EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE);
  //--------------------------------------------------------------------------------
}

void loop() {

  BLEDevice central = BLE.central(); // Searches for the central device

  if (central) {
  
    while (central.connected()) {
      
      int sensorValue;

      if (millis() > last_interval_ms + INTERVAL_MS) {

        last_interval_ms = millis();

        //-------------------------- Read sensor data -------------------------------------------------

        sensorValue = analogRead(analogPin);
        float normalizedValue = sensorValue * (3.3 / 4095);
        features[feature_ix++] = normalizedValue;

        //-----------------------Features buffer full? then classify!----------------------------------

        if (feature_ix == EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE) {

          //-------------------- Create signal from features frame -------------------------------------

          ei_impulse_result_t result;
          signal_t signal;
          numpy::signal_from_buffer(features, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);

          // ------------------------- Run classifier -------------------------------------------------

          EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);
          ei_printf("run_classifier returned: %d\n", res);
          if (res != 0) return;

          // ------------------------- Print predictions ----------------------------------------------

          ei_printf("Predictions (DSP: %d ms., Classification: %d ms., Anomaly: %d ms.): \n",
                    result.timing.dsp,
                    result.timing.classification,
                    result.timing.anomaly);

          // ------------------------- Prediction results ----------------------------------------------

          if (result.classification[0].value >= 0.6) {
            //Keyboard.key_code_raw(KEY_A);
            int dato = 1;
            sensorCharacteristic.writeValue(dato);
          } else if (result.classification[1].value >= 0.6) {
            //Keyboard.key_code_raw(KEY_E);
            int dato = 2;
            sensorCharacteristic.writeValue(dato);
          } else if (result.classification[2].value >= 0.6) {
            //Keyboard.key_code_raw(KEY_I);
            int dato = 3;
            sensorCharacteristic.writeValue(dato);
          } else if (result.classification[3].value >= 0.6) {
            //Keyboard.key_code_raw(KEY_O);
            int dato = 4;
            sensorCharacteristic.writeValue(dato);
          } else if (result.classification[4].value >= 0.6) {
            //Keyboard.key_code_raw(KEY_U);
            int dato = 5;
            sensorCharacteristic.writeValue(dato);
          } else if (result.classification[5].value >= 0.6) {
            // Noise prediction
          }
          delay(1000);

          // --------------------------- print the predictions ----------------------------------------

          for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
            ei_printf("%s:\t%.5f\n", result.classification[ix].label, result.classification[ix].value);
          }
          #if EI_CLASSIFIER_HAS_ANOMALY == 1
                ei_printf("anomaly:\t%.3f\n", result.anomaly);
          #endif
              // reset features frame
              feature_ix = 0;

          //-------------------------------------------------------------------------------------------
        }
      }
    }
    //-------------------------------------------------------------------------------------------------

    Serial.print("Disconnected from central: ");
    Serial.println(central.address());

    //-------------------------------------------------------------------------------------------------
  }
}

void ei_printf(const char *format, ...) {
  static char print_buf[1024] = { 0 };

  va_list args;
  va_start(args, format);
  int r = vsnprintf(print_buf, sizeof(print_buf), format, args);
  va_end(args);

  if (r > 0) {
    Serial.write(print_buf);
  }
}

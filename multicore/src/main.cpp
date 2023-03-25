// My libraries for organizing code
#include "networking.h"
#include "led_control.h"

// Arduino and Espresso libraries
#include <WiFi.h>

// When I tried this the other way around (LEDs isolated on core 1),
// The LEDs froze up once every 5-10 seconds. I think there might be
// some kind of implicit networking or something also running on 
// core 1.
#define CORE_FOR_LED_CONTROL 0
#define CORE_FOR_EVERTHING_ELSE 1

void TaskOTA(void *pvParameters) {
  while (true) {
    networking::checkForOTAUpdate();
  }
}

void TaskLED(void *pvParameters) {
  while (true){
    led_control::mainLoop();
  }
}

void startTask(TaskFunction_t pvTaskCode, const char *const pcName, const BaseType_t xCoreID)
{
  // See https://docs.espressif.com/projects/esp-idf/en/v5.0/esp32/api-reference/system/freertos.html#functions
  // In most example code, they retain the task handle, which can be used
  // to suspend or stop a task. Since in this application, tasks are
  // never stopped, I simplify things by discarding the handle.
  TaskHandle_t handleToBeDiscarded;
  xTaskCreatePinnedToCore(
      pvTaskCode,           /* Task function. */
      pcName,               /* name of task. */
      10000,                /* Stack size of task */
      NULL,                 /* parameter of the task */
      1,                    /* priority of the task */
      &handleToBeDiscarded, /* Task handle to keep track of created task */
      xCoreID);             /* which core does the task run on */
}

void setup()
{
  Serial.begin(115200);
  Serial.println("Booting");

  led_control::setupFastLED();
  networking::setupWiFi();
  networking::setupOTA();

  Serial.println("WiFi Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  startTask(TaskOTA, "OTA", CORE_FOR_EVERTHING_ELSE);
  startTask(TaskLED, "LED Control", CORE_FOR_LED_CONTROL);
}

void loop()
{
  // Do nothing in the default task.  All application code
  // is in tasks started via xTaskCreatePinnedToCore.
}
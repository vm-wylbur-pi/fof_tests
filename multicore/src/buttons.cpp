#include "buttons.h"

#include "comms.h"
#include "led_control.h"

#include <Arduino.h>

// Physical Button on the Audio board
// Push down on the center of the button, perpendicular to the edge of the PCB
const uint8_t BUTTON_PRESS_PIN = 35;
// Rock the button upward, toward the end of the PCB where the USB port is
const uint8_t BUTTON_ROCK_TOWARD_AUDIO_PORT_PIN = 36;
// Rock the button downward, toward the audio port that is besid it.
const uint8_t BUTTON_ROCK_TOWARD_USB_PORT_PIN = 39;


namespace buttons
{
    // State variables for handling physical buttons.
    uint32_t lastButtonTimeMillis = 0;

    void setupButtons() {
        pinMode(BUTTON_PRESS_PIN, INPUT_PULLUP);
        pinMode(BUTTON_ROCK_TOWARD_AUDIO_PORT_PIN, INPUT_PULLUP);
        pinMode(BUTTON_ROCK_TOWARD_USB_PORT_PIN, INPUT_PULLUP);
    }

    void mainLoop() {
        // Protect against botton bounce.  This could be more sophisticated
        // if we cared, wanted to respond to held-down buttons, etc.
        bool longEnoughSinceLastButtonPress = millis() - lastButtonTimeMillis > 500;
        if (longEnoughSinceLastButtonPress) {
            if (digitalRead(BUTTON_ROCK_TOWARD_USB_PORT_PIN) == 0) {
                comms::sendDebugMessage("Physical button: rock forward");
                // Do something interesting.
                lastButtonTimeMillis = millis();
            }
            if (digitalRead(BUTTON_ROCK_TOWARD_AUDIO_PORT_PIN) == 0) {
                comms::sendDebugMessage("Physical button: rock backward");
                // Do something interesting.
                lastButtonTimeMillis = millis();
            }
            if (digitalRead(BUTTON_PRESS_PIN) == 0) {
                comms::sendDebugMessage("Physical button: press");
                // Run a hue pulse with all default parameters.
                led_control::commands::addPattern("HuePulse", "");
                // TODO move this code to the audio module, in a new command for mute/unmute
                // if (audio.getVolume() != 0) {
                //     volumeBeforeMuting = audio.getVolume();
                //     audio.setVolume(0);
                // } else {
                //     audio.setVolume(volumeBeforeMuting);
                // }
                lastButtonTimeMillis = millis();
            }
        }
    }
} // namespace buttons
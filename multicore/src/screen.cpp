#include "screen.h"

#include "comms.h"
#include "flower_info.h"

#include <Arduino.h> // For String type
#include <Wire.h>    // For global Wire object needed For I2C-connected screen
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

namespace screen
{
    // Based on example code at
    // https://github.com/adafruit/Adafruit_SSD1306/blob/master/examples/ssd1306_128x64_i2c/ssd1306_128x64_i2c.ino
    const uint8_t SCREEN_WIDTH = 128;    // OLED display width, in pixels
    const uint8_t SCREEN_HEIGHT = 64;    // OLED display height, in pixels
    const int8_t OLED_RESET_PIN = -1;    // Reset pin # (or -1 if sharing Arduino reset pin)
    // The following three values were verified for the MakePython board using
    // https://github.com/RuiSantosdotme/Random-Nerd-Tutorials/blob/master/Projects/LCD_I2C/I2C_Scanner.ino
    const uint8_t MAKEPYTHON_ESP32_SDA = 4;
    const uint8_t MAKEPYTHON_ESP32_SCL = 5;
    const uint8_t SCREEN_I2C_ADDRESS = 0x3C;

    // https://learn.adafruit.com/adafruit-gfx-graphics-library/rotating-the-display
    const uint8_t PORTRAIT_SCREEN_ROTATION = 3;

    Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET_PIN);

    bool initialized = false;
    String currentText = "";

    void setupScreen() {
        Wire.begin(MAKEPYTHON_ESP32_SDA, MAKEPYTHON_ESP32_SCL);
        // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
        if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_I2C_ADDRESS)) { 
            Serial.println("Screen initialization failed");
            comms::sendDebugMessage("Screen initialization failed");
        } else {
            initialized = true;
            display.setRotation(PORTRAIT_SCREEN_ROTATION);
            Serial.println("Screen initialized");
            comms::sendDebugMessage("Screen initialized");
            display.clearDisplay();
            display.display();
        }
    }

    void powerDown() {
        display.ssd1306_command(SSD1306_DISPLAYOFF);
    }

    namespace {
        void drawText(const String &newScreenText) {
            if (initialized)
            {
                display.clearDisplay();

                display.setTextSize(1);              // Normal 1:1 pixel scale
                display.setTextColor(SSD1306_WHITE); // Draw white text
                display.setCursor(0, 0);             // Start at top-left corner
                display.cp437(true);                 // Use full 256 char 'Code Page 437' font

                // Add a newline at the beginning because the screen is set back a little bit from
                // the hole in the birdhouse, so when viewed from a little above, the top line or
                // two is occulded by the edge of the birdhouse wall.
                String paddedText = "\n" + newScreenText;
                display.println(paddedText);
                display.display();
            }
        }
    }

    namespace commands
    {
        void setText(const String &newScreenText) {
            currentText = newScreenText;
            drawText(currentText);
        }
        void appendText(const String &textToAdd) {
            currentText += textToAdd;
            drawText(currentText);
        };
        void resetToFlowerSummary() {
            setText(flower_info::summaryForScreen());
        };
    } // namespace commands
} // namespace screen
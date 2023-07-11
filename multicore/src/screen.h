#ifndef SCREEN_H
#define SCREEN_H

#include <Arduino.h> // For String type

namespace screen
{
    // Should be called from the main app's setup()
    void setupScreen();

    // Turn the screen fully off. Used when entering sleep mode.
    // After calling powerDown, setupScreen() must be called before
    // runnin any of the commands below.
    void powerDown();

    namespace commands
    {
        void setText(const String &newScreenText);
        void appendText(const String &textToAdd);
    } // namespace commands
} // namespace screen

#endif // SCREEN_H
#ifndef SCREEN_H
#define SCREEN_H

#include <Arduino.h> // For String type

namespace screen
{
    // Should be called from the main app's setup()
    void setupScreen();

    namespace commands
    {
        void setText(const String &newScreenText);
        void appendText(const String &textToAdd);
    } // namespace commands
} // namespace screen

#endif // SCREEN_H
#ifndef BUTTONS_H
#define BUTTONS_H

#include <Arduino.h> 

namespace buttons
{
    // Should be called from the main app's setup()
    void setupButtons();

    // Should be called from the main app's loop(), or a task's forever-loop
    void mainLoop();

} // namespace buttons

#endif // BUTTONS_H
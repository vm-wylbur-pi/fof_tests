from . import game

class WholeFieldSleep(game.StatefulGame):
    def __init__(self, sleepIntervalSecs=5):
        self.hasSetRetainedSleepCommand = False
        self.sleepIntervalSecs = 5 * 60

    def runLoop(self, flowers, unused_field):
        if not self.hasSetRetainedSleepCommand:
            print("Setting retained sleep mode commands.")
            for flower in flowers:
                # This is a "Retained" MQTT message, which means the flowers will get it
                # right away, and will get it again every time they subscribe. Since they
                # re-subscribe to their MQTT command topic after waking from sleep, this
                # has the effect of keeping them asleep until the retained message is removed.
                flower.sendMQTTCommand(command="enterSleepMode",
                                       params=f'{self.sleepIntervalSecs * 1000}',
                                       retained=True)
            self.hasSetRetainedSleepCommand = True

    def isDone(self):
        # Keep the field asleep until this game is force-ended via the clearGames command
        return False

    def stop(self, flowers):
        print("Clearing retained sleep commands.")
        for flower in flowers:
            # You clear a retained MQTT message by sending a new one with an empty payload
            # If any flowers are currently awake (unlikely), this will cause them to sleep
            # one more time, for the default sleep duration (10 seconds)
            flower.sendMQTTCommand(
                command="enterSleepMode", params='', retained=True)
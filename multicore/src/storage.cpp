#include "storage.h"
#include "comms.h"
#include "screen.h"

#include <Arduino.h>
#include <SPI.h> // Serial peripheral interface, for integrating with the audio/SD board
#include <SD.h>  // SD card
#include <FS.h>  // Generic filesystem
#include <ESP-FTP-Server-Lib.h>  // FTP Server
#include <FTPFilesystem.h>       // FTP Server link targets for SD, SPIFFS, etc

// Good reference for understanding SPI
// https://randomnerdtutorials.com/esp32-spi-communication-arduino/

// SPI (Serial peripheral interface) pins needed for SD card initialization.
//////////////////////////////////////////////////
const uint8_t SD_CS = 22;     // Chip select for the SD card Peripheral
const uint8_t SPI_COPI = 23;  // Controller out - peripheral in
const uint8_t SPI_CIPO = 19;  // Conroller in - perpheral out
const uint8_t SPI_SCK = 18;   // Serial Clock

#define FTP_USER "fof"
#define FTP_PASSWORD "fof"

namespace storage
{
    FTPServer ftp;

    void setupSDCard() {
        // This is copy-pased without reading any docs.
        Serial.println("trying to connect to SD");
        pinMode(SD_CS, OUTPUT);
        digitalWrite(SD_CS, HIGH);

        // Initializes the SPI bus by setting SCK, COPI, and SS to outputs,
        // pulling SCK and COPI low, and SS high.
        SPI.begin(SPI_SCK, SPI_CIPO, SPI_COPI);
        SPI.setFrequency(1000000);
        if (!SD.begin(SD_CS, SPI))
        {
            Serial.println("Card Mount Failed");
            comms::sendDebugMessage("SD card filesystem mount failed.");
        }
        Serial.println("SD card filesystem mount succedded.");
        comms::sendDebugMessage("SD card filesystem mount succeeded.");
        screen::commands::appendText("SD Card mounted\n");
    }

    void setupFTP() {
        ftp.addUser(FTP_USER, FTP_PASSWORD);
        // This is the global SD filesystem reference, valid only after
        // it's been initialized via setupSDCard()
        // Using "SD" here means that the server will mount everything under the SD
        // filesystem in a folder named "SD" at the root of the FTP server. So audio
        // files are at, e.g. /SD/cool-sound.wav
        ftp.addFilesystem("SD", &SD);
        // Current design leaves the FTP server running all the time, for simplicity.
        // If this turns out to be a problem, we could instead start/stop it via
        // commands sent over MQTT.
        ftp.begin();

        const String ftpMessage = "FTP server started\n";
        Serial.println(ftpMessage);
        comms::sendDebugMessage(ftpMessage);
        screen::commands::appendText(ftpMessage);
    }

    void handleFTP() {
        ftp.handle();
    }

    String formatStorageUsage() {
        uint32_t mb_used = SD.usedBytes() / (1024 * 1024);
        uint32_t mb_total = SD.totalBytes() / (1024 * 1024);
        return "used " + String(mb_used) + "/" + String(mb_total) + " MB";
    }

    uint16_t listFilesInRootDir(String fileNames[30]) {
        // This should be in the .h file.
        const uint8_t maxFilenamesToReturn = 30;
        uint16_t numFiles = 0;

        Serial.println("opening root folter");
        File root = SD.open("/");
        if (!root) {
            comms::sendDebugMessage("Failed to open SD card root directory");
            return 0;
        }

        // This shuld use the FS::Dir object, but I don't know how to upgrade
        // the old SD.h library to the current SDFS.h version.
        File file = root.openNextFile();
        while (file) {
            if (!file.isDirectory() && !String(file.name()).startsWith(".")) {
                if (numFiles < maxFilenamesToReturn) {
                    fileNames[numFiles] = file.name();
                }
                numFiles++;
            }
            file = root.openNextFile();
        }
        return numFiles;
    }

} // namespace storage

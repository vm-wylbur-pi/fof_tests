#ifndef STORAGE_H
#define STORAGE_H

#include <Arduino.h>  // For String

namespace storage
{
    // Should be called from main app setup();
    void setupSDCard();

    // Get the names of files stored in the root directory of the SD card.
    // Directories and files that start with "." are ignored.
    // Returns at most 30 filenames.  Retrun value is the actual number of
    // files present, even if not all are returned in fileNames.
    uint16_t listFilesInRootDir(String fileNames[30]);

    // A string summarizing used and total space on the SD card
    // e.g. "used 27/14855 MB"
    String formatStorageUsage();
} // namespace storage

#endif // STORAGE_H
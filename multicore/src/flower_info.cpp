#include "flower_info.h"

#include <map>

#include <Arduino.h>
#include <WiFi.h> // For macAddress used in flowerID, and SSID for description

#include "comms.h"
#include "networking.h"
#include "version.h"

// This definition was gerated by tools/convert_flower_inventory_to_cpp.py
std::map<String, flower_info::FlowerInfo> FlowerInventory = {
  { "F0:6D:8C",  {1, "F0:6D:8C", poppy, -1}  },
  { "F0:70:1C",  {2, "F0:70:1C", aster, -1}  },
  { "F0:6F:04",  {3, "F0:6F:04", poppy, -1}  },
  { "DA:E7:10",  {4, "DA:E7:10", poppy, -1}  },
  { "F0:5F:EC",  {5, "F0:5F:EC", geranium, -1}  },
  { "F0:70:AC",  {6, "F0:70:AC", geranium, -1}  },
  { "F0:5F:E8",  {7, "F0:5F:E8", aster, -1}  },
  { "F0:70:48",  {8, "F0:70:48", poppy, -1}  },
  { "F0:6F:00",  {9, "F0:6F:00", geranium, -1}  },
  { "F0:6E:D4",  {10, "F0:6E:D4", geranium, -1}  },
  { "F0:6D:80",  {11, "F0:6D:80", poppy, -1}  },
  { "C0:30:24",  {12, "C0:30:24", geranium, -1}  },
  { "BA:5F:80",  {13, "BA:5F:80", aster, -1}  },
  { "BA:68:78",  {14, "BA:68:78", poppy, -1}  },
  { "C0:36:34",  {15, "C0:36:34", poppy, -1}  },
  { "F0:70:58",  {16, "F0:70:58", poppy, -1}  },
  { "C0:10:C4",  {17, "C0:10:C4", geranium, -1}  },
  { "CD:10:60",  {18, "CD:10:60", geranium, -1}  },
  { "F0:70:80",  {19, "F0:70:80", geranium, 40}  },
  { "F0:6F:E4",  {20, "F0:6F:E4", poppy, 46}  },
  { "C0:12:44",  {21, "C0:12:44", aster, 39}  },
  { "BA:59:F4",  {22, "BA:59:F4", geranium, 39}  },
  { "C0:38:FC",  {23, "C0:38:FC", geranium, 45.5}  },
  { "C0:3B:F8",  {24, "C0:3B:F8", geranium, 46}  },
  { "BA:6F:A0",  {25, "BA:6F:A0", poppy, 43}  },
  { "CC:FC:C0",  {26, "CC:FC:C0", aster, 43}  },
  { "F0:70:90",  {27, "F0:70:90", geranium, 46.5}  },
  { "C0:F0:2C",  {28, "C0:F0:2C", aster, 42}  },
  { "C0:1E:78",  {29, "C0:1E:78", aster, 45}  },
  { "BA:79:EC",  {30, "BA:79:EC", aster, 39}  },
  { "C0:21:F0",  {31, "C0:21:F0", aster, 39}  },
  { "CD:04:14",  {32, "CD:04:14", aster, 45}  },
  { "C0:1E:80",  {33, "C0:1E:80", geranium, 46}  },
  { "BA:86:C8",  {34, "BA:86:C8", geranium, 43}  },
  { "CC:FE:C8",  {35, "CC:FE:C8", aster, 45}  },
  { "C0:0D:A4",  {36, "C0:0D:A4", geranium, 42}  },
  { "C0:0E:1C",  {37, "C0:0E:1C", geranium, 42.5}  },
  { "BA:8C:98",  {38, "BA:8C:98", aster, 38}  },
  { "C0:39:CC",  {39, "C0:39:CC", aster, 40}  },
  { "C0:39:4C",  {40, "C0:39:4C", poppy, 40}  },
  { "CC:FE:B8",  {41, "CC:FE:B8", geranium, 48}  },
  { "BA:8D:1C",  {42, "BA:8D:1C", aster, 46}  },
  { "BA:7A:EC",  {43, "BA:7A:EC", geranium, 42}  },
  { "CD:10:54",  {44, "CD:10:54", geranium, 45}  },
  { "BA:53:58",  {45, "BA:53:58", aster, 38.5}  },
  { "C0:2B:A0",  {46, "C0:2B:A0", poppy, 43.5}  },
  { "BA:3E:10",  {47, "BA:3E:10", aster, 41}  },
  { "C0:2B:44",  {48, "C0:2B:44", poppy, 39}  },
  { "C0:31:58",  {49, "C0:31:58", aster, 39}  },
  { "BA:67:C8",  {50, "BA:67:C8", geranium, 45.5}  },
  { "C0:49:18",  {51, "C0:49:18", aster, 45.5}  },
  { "C0:38:D0",  {52, "C0:38:D0", aster, 41.5}  },
  { "BA:8D:70",  {53, "BA:8D:70", geranium, 46.5}  },
  { "C0:19:44",  {54, "C0:19:44", aster, 39}  },
  { "C0:12:B8",  {55, "C0:12:B8", geranium, 39}  },
  { "C0:10:74",  {56, "C0:10:74", geranium, 39}  },
  { "CC:F7:C4",  {57, "CC:F7:C4", geranium, 41.5}  },
  { "C0:2F:8C",  {58, "C0:2F:8C", aster, 45.5}  },
  { "C0:04:D4",  {59, "C0:04:D4", geranium, 39.5}  },
  { "CC:FC:40",  {60, "CC:FC:40", aster, 45.5}  },
  { "CC:FE:90",  {61, "CC:FE:90", aster, 44.5}  },
  { "C0:3B:98",  {62, "C0:3B:98", aster, 40}  },
  { "C0:2F:4C",  {63, "C0:2F:4C", geranium, 40}  },
  { "C0:21:18",  {64, "C0:21:18", aster, 39}  },
  { "BA:89:D8",  {65, "BA:89:D8", aster, 39}  },
  { "C0:1E:34",  {66, "C0:1E:34", aster, 39}  },
  { "CD:06:40",  {67, "CD:06:40", poppy, 44}  },
  { "F0:6E:E8",  {68, "F0:6E:E8", aster, 39}  },
  { "C0:16:A8",  {69, "C0:16:A8", geranium, 46}  },
  { "CC:FE:7C",  {70, "CC:FE:7C", poppy, 46}  },
  { "CC:FE:CC",  {71, "CC:FE:CC", geranium, 40}  },
  { "CC:33:A0",  {72, "CC:33:A0", geranium, 44.5}  },
  { "D5:11:80",  {73, "D5:11:80", geranium, 39}  },
  { "C0:38:1C",  {74, "C0:38:1C", aster, 38}  },
  { "C0:1C:94",  {75, "C0:1C:94", geranium, 40}  },
  { "BA:4E:50",  {76, "BA:4E:50", aster, 39}  },
  { "F0:6E:DC",  {77, "F0:6E:DC", geranium, 46}  },
  { "BA:8D:14",  {78, "BA:8D:14", geranium, 39.5}  },
  { "BA:8C:A4",  {79, "BA:8C:A4", geranium, 45.5}  },
  { "C0:38:6C",  {80, "C0:38:6C", geranium, 39}  },
  { "C0:05:14",  {81, "C0:05:14", geranium, 42}  },
  { "BA:5F:48",  {82, "BA:5F:48", geranium, 42.5}  },
  { "BA:8C:A4",  {83, "BA:8C:A4", geranium, 45.5 }  },
  { "C0:1F:90",  {84, "C0:1F:90", geranium, 39.5}  },
  { "BA:89:D4",  {85, "BA:89:D4", aster, 42}  },
  { "C0:2B:F0",  {86, "C0:2B:F0", geranium, 45}  },
  { "C0:11:28",  {87, "C0:11:28", poppy, 46}  },
  { "CC:FA:D0",  {88, "CC:FA:D0", aster, 45}  },
  { "D5:4B:5C",  {89, "D5:4B:5C", geranium, 39}  },
  { "C0:39:64",  {90, "C0:39:64", poppy, 39}  },
  { "C0:4A:B8",  {91, "C0:4A:B8", geranium, 40}  },
  { "C0:35:30",  {92, "C0:35:30", geranium, 45.5}  },
  { "C0:17:DC",  {93, "C0:17:DC", aster, 39.5}  },
  { "C0:21:08",  {94, "C0:21:08", geranium, 40}  },
  { "C0:17:A0",  {95, "C0:17:A0", aster, 41.5}  },
  { "BA:3F:AC",  {96, "BA:3F:AC", aster, 45.5}  },
  { "C0:3B:C8",  {97, "C0:3B:C8", poppy, 40}  },
  { "BA:40:24",  {98, "BA:40:24", geranium, 42.5}  },
  { "C0:12:90",  {99, "C0:12:90", geranium, 42}  },
  { "C0:37:58",  {100, "C0:37:58", aster, 42}  },
  { "BA:74:F0",  {101, "BA:74:F0", geranium, 45.5}  },
  { "C0:2B:98",  {102, "C0:2B:98", aster, 42}  },
  { "F0:6E:E4",  {103, "F0:6E:E4", geranium, 46.5}  },
  { "BA:7F:18",  {104, "BA:7F:18", geranium, 45}  },
  { "CD:06:64",  {105, "CD:06:64", poppy, 46}  },
  { "C0:37:90",  {106, "C0:37:90", geranium, 45.5}  },
  { "C0:4A:A4",  {107, "C0:4A:A4", aster, 42}  },
  { "C0:20:60",  {108, "C0:20:60", aster, 39}  },
  { "BA:67:D0",  {109, "BA:67:D0", geranium, 46}  },
  { "BA:7C:84",  {110, "BA:7C:84", poppy, 42}  },
  { "CD:0D:C4",  {111, "CD:0D:C4", geranium, 40}  },
  { "C0:2F:98",  {112, "C0:2F:98", aster, 40}  },
  { "C0:31:70",  {113, "C0:31:70", geranium, 42.5}  },
  { "BA:7C:60",  {114, "BA:7C:60", aster, 45}  },
  { "CC:1E:10",  {115, "CC:1E:10", geranium, 40}  },
  { "C0:49:C0",  {116, "C0:49:C0", aster, 39}  },
  { "BA:7B:EC",  {117, "BA:7B:EC", poppy, 45}  },
  { "BA:7E:A0",  {118, "BA:7E:A0", poppy, 46}  },
  { "BA:89:B8",  {119, "BA:89:B8", geranium, 40}  },
  { "BA:72:AC",  {120, "BA:72:AC", aster, 39}  },
  { "C0:20:0C",  {121, "C0:20:0C", aster, 42}  },
  { "CC:FE:C4",  {122, "CC:FE:C4", aster, 44.5}  },
  { "BA:69:98",  {123, "BA:69:98", aster, 39}  },
  { "CD:0D:D4",  {124, "CD:0D:D4", geranium, 38}  },
  { "BA:7A:60",  {125, "BA:7A:60", aster, 39}  },
  { "C0:0D:94",  {126, "C0:0D:94", aster, 40.5}  },
  { "CC:FE:D4",  {127, "CC:FE:D4", geranium, 40}  },
  { "F0:6F:E0",  {128, "F0:6F:E0", geranium, 43}  },
  { "C0:1E:00",  {129, "C0:1E:00", aster, 39}  },
  { "C0:34:BC",  {130, "C0:34:BC", geranium, 38.5}  },
  { "C0:1E:30",  {131, "C0:1E:30", aster, 39}  },
  { "C0:2B:68",  {132, "C0:2B:68", geranium, 45}  },
  { "C0:1E:DC",  {133, "C0:1E:DC", geranium, 45}  },
  { "BA:5C:7C",  {134, "BA:5C:7C", geranium, 41}  },
  { "BA:5A:00",  {135, "BA:5A:00", aster, 39}  },
  { "C0:35:18",  {136, "C0:35:18", aster, 44}  },
  { "C0:36:9C",  {137, "C0:36:9C", geranium, 39.5}  },
  { "BA:3B:98",  {138, "BA:3B:98", aster, 44.5}  },
  { "CC:FE:D0",  {139, "CC:FE:D0", aster, 38}  },
  { "BA:68:98",  {140, "BA:68:98", aster, 45}  },
  { "BA:5F:60",  {141, "BA:5F:60", aster, 39}  },
  { "F0:6E:C8",  {142, "F0:6E:C8", aster, 43}  },
  { "C0:11:A0",  {143, "C0:11:A0", aster, 39}  },
  { "D8:92:64",  {144, "D8:92:64", geranium, 42}  },
  { "C0:42:8C",  {145, "C0:42:8C", aster, 45}  },
  { "BA:7A:68",  {146, "BA:7A:68", geranium, 40}  },
  { "F0:70:28",  {147, "F0:70:28", aster, 39.5}  },
  { "C0:11:0C",  {148, "C0:11:0C", aster, 42.5}  },
  { "C0:11:10",  {149, "C0:11:10", aster, 42.5}  },
  { "BA:8C:60",  {150, "BA:8C:60", geranium, 45.5}  },
  { "CC:1E:08",  {151, "CC:1E:08", geranium, 42.5}  },
  { "F0:60:60",  {152, "F0:60:60", geranium, 42}  },
  { "C0:2D:C8",  {153, "C0:2D:C8", aster, 39}  },
  { "C0:10:6C",  {154, "C0:10:6C", aster, 42}  },
  { "C0:2B:58",  {155, "C0:2B:58", geranium, 43}  },
  { "CC:F7:F8",  {156, "CC:F7:F8", geranium, 45}  },
  { "C0:39:94",  {157, "C0:39:94", geranium, 40}  },
  { "F0:70:94",  {158, "F0:70:94", geranium, 42}  },
  { "C0:37:D0",  {159, "C0:37:D0", aster, 42.5}  },
  { "BA:82:88",  {160, "BA:82:88", aster, 39.5}  },
};

namespace flower_info {
    String flowerID() {
        // According to the docs, The MAC address is not guaranteed stable until WiFi
        // is connected.  But we want it sooner, right at boot time, so the LED control
        // task doesn't need to wait for networking to come up.  So just return it
        // without checking WiFi.status() == WL_CONNECTED.  This seems to work fine.
        return WiFi.macAddress().substring(9);
    }

    FlowerInfo flowerInfo() {
        auto info = FlowerInventory.find(flowerID());
        if (info != FlowerInventory.end()) {
            return info->second;
        } else {
            comms::sendDebugMessage("Flower missing from inventory: " + flowerID());
            return { -1, "unknown", unknown, -1.0};
        }
    }

    // Needed for converting the species enum to a String type
    // These must be in the same order as in the enum definition in flower_info.h
    String speciesNames[4] = {"unknown", "poppy", "geranium", "aster"};

    String summaryForScreen() {
        FlowerInfo info = flowerInfo();

        // Extra newlines at the start to push the text low enough to be readable
        // without bending down too low.
        String descrip = "\n\n";
        descrip += "I'm # " + String(info.sequenceNum) + "\n" + flowerID() + "\n";
        descrip += String(speciesNames[info.species]) + "\n\n";

        descrip += version::Name + "\n";
        descrip += "Built\n" + version::getBuildTime() + "\n\n";

        descrip += WiFi.SSID() + "\n";
        if (networking::isMQTTConnected()) {
            descrip += "MQTT OK\n";
        } else {
            descrip += "MQTT bad\n";
        }
        return descrip;
    }

} // namespace flower_info
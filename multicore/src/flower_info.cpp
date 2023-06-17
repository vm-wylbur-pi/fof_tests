#include "flower_info.h"

#include <map>

#include <Arduino.h>
#include <WiFi.h> // For macAddress used in flowerID

#include "comms.h"

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
  { "C0:0E:1C",  {37, "C0:0E:1C", geranium, 42.51}  },
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
};

namespace flower_info {
    String flowerID() {
        // The MAC address is not guaranteed stable until WiFi is connected.
        if (WiFi.status() != WL_CONNECTED) {
            return "ID-unavailable-WiFi-not-connected";
        } else {
            return WiFi.macAddress().substring(9);
        }
    }

    FlowerInfo flowerInfo() {
        auto info = FlowerInventory.find(flowerID());
        if (info != FlowerInventory.end()) {
            return info->second;
        } else {
            comms::sendDebugMessage("Failed to find flower info for " + flowerID());
            return { -1, "unknown", unknown, -1.0};
        }
    }

    // Needed for converting the species enum to a String type
    // These must be in the same order as in the enum definition in flower_info.h
    String speciesNames[4] = {"unknown", "poppy", "geranium", "aster"};

    String description() {
        FlowerInfo info = flowerInfo();
        return "#" + String(info.sequenceNum) + "\n" + info.id + "\n"
               + String(speciesNames[info.species]);
    }

} // namespace flower_info
#ifndef NETWORKING_H
#define NETWORKING_H

namespace networking {
  // Should be called from the main app setup().  Should be called before
  // any other networking:: functions.
  void setupWiFi();

  // Should be called from the main app setup(), after setupWiFi
  void setupOTA();

  // Should be called from the main app loop(), or a tasks forever-loop.
  // setupOTA must be called first.
  void checkForOTAUpdate();
}

#endif // NETWORKING_H

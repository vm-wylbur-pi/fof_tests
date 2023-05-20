// NeoPixel test program showing use of the WHITE channel for RGBW
// pixels only (won't look correct on regular RGB NeoPixel strips).

#include <Adafruit_NeoPixel.h>

#include "Arduino.h"
//#include "WiFiMulti.h"
#include <Audio.h>
#include "SPI.h"
#include "SD.h"
#include "FS.h"
#include <stdio.h>
#include <string.h>

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>


#define I2S_DOUT      27
#define I2S_BCLK      26
#define I2S_LRCK      25

#define SD_SCK    18
#define SD_MISO   19
#define SD_MOSI   23
#define SD_CS     22

//---- Audio Set ------------------------------------------


Audio audio;


struct Music_info
{
    String name;
    int length;
    int runtime;
    int volume;
    int status;
    int mute_volume;
} music_info = {"", 0, 0, 0, 0, 0};

String music_list[20];
int music_num = 0;
int music_index = 0;

#define FILE_AUDIO_01 "/MoonlightBay.mp3"
#define FILE_AUDIO_02 "/LoveStory.mp3"
#define FILE_AUDIO_03 "/CatchMyBreath.mp3"

const char *ssid = "Makerfabs";
const char *password = "20160704";

// digital pin 39 has a pushbutton attached to it. Give it a name:
int pushButton1 = 39;
int pushButton2 = 36;
int pushButton3 = 35;  //Pause/start

// Which pin on the Arduino is connected to the NeoPixels?
// On a Trinket or Gemma we suggest changing this to 1:
#define LED_PIN     13



// How many NeoPixels are attached to the Arduino?
#define LED_COUNT   66

// NeoPixel brightness, 0 (min) to 255 (max)
#define BRIGHTNESS  100

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
// Argument 1 = Number of pixels in NeoPixel strip
// Argument 2 = Arduino pin number (most are valid)
// Argument 3 = Pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)

uint8_t max_stations = 0;   //will be set later
uint8_t cur_station  = 0;   //current station(nr), will be set later

uint8_t showMode=0;//RGB LED

String stations[] ={
        "0n-80s.radionetz.de:8000/0n-70s.mp3",
        "mediaserv30.live-streams.nl:8000/stream",
        "www.surfmusic.de/m3u/100-5-das-hitradio,4529.m3u",
        "stream.1a-webradio.de/deutsch/mp3-128/vtuner-1a",
        "mp3.ffh.de/radioffh/hqlivestream.aac", //  128k aac
        "www.antenne.de/webradio/antenne.m3u",
        "listen.rusongs.ru/ru-mp3-128",
        "edge.audio.3qsdn.com/senderkw-mp3",
        "macslons-irish-pub-radio.com/media.asx",
};


String showString="";//

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void(* resetFunc) (void) = 0; //declare reset function at address 0

#define I2C_SDA 4
#define I2C_SCL 5


void sd_init()
{
    //SD(SPI)
    pinMode(SD_CS, OUTPUT);
    digitalWrite(SD_CS, HIGH);
    SPI.begin(SD_SCK, SD_MISO, SD_MOSI);
    //SPI.setFrequency(1000000);
    if (!SD.begin(SD_CS, SPI))
    {
        Serial.println("Card Mount Failed");
        while (1)
          delay(1000);
    }
    else
    {
        Serial.println("SD INIT OK");
    }
}


int get_music_list(fs::FS &fs, const char *dirname, uint8_t levels, String filelist[30])
{
    Serial.printf("Listing directory: %s\n", dirname);
    int i = 0;

    File root = fs.open(dirname);
    if (!root)
    {
        Serial.println("Failed to open directory");
        return i;
    }
    if (!root.isDirectory())
    {
        Serial.println("Not a directory");
        return i;
    }

    File file = root.openNextFile();
    while (file)
    {
        if (file.isDirectory())
        {
        }
        else
        {
            String temp = file.name();
            if (temp.endsWith(".wav"))
            {
                filelist[i] = temp;
                i++;
            }
            else if (temp.endsWith(".mp3"))
            {
                filelist[i] = temp;
                i++;
            }
        }
        file = root.openNextFile();
    }
    return i;
}

//----- Audio Function --------------------------------------------------

void open_new_song(String filename)
{
    //去掉文件名的根目录"/"和文件后缀".mp3",".wav"
    //remove root directory and file postfix ".mp3",".wav"
    music_info.name = filename.substring(1, filename.indexOf("."));
    audio.connecttoFS(SD, filename.c_str());
    music_info.runtime = audio.getAudioCurrentTime();
    music_info.length = audio.getAudioFileDuration();
    music_info.volume = audio.getVolume();
    music_info.status = 1;
    Serial.println("**********start a new sound************");
}


// optional
void audio_info(const char *info){
    Serial.print("info        "); Serial.println(info);
}
void audio_id3data(const char *info){  //id3 metadata
    Serial.print("id3data     ");Serial.println(info);
}
void audio_eof_mp3(const char *info){  //end of file
    Serial.print("eof_mp3     ");Serial.println(info);
}
void audio_showstation(const char *info){
    Serial.print("station     ");Serial.println(info);
}
void audio_showstreaminfo(const char *info){
    Serial.print("streaminfo  ");Serial.println(info);
}
void audio_showstreamtitle(const char *info){
    Serial.print("streamtitle ");Serial.println(info);
}
void audio_bitrate(const char *info){
    Serial.print("bitrate     ");Serial.println(info);
}
void audio_commercial(const char *info){  //duration in sec
    Serial.print("commercial  ");Serial.println(info);
}
void audio_icyurl(const char *info){  //homepage
    Serial.print("icyurl      ");Serial.println(info);
}
void audio_lasthost(const char *info){  //stream URL played
    Serial.print("lasthost    ");Serial.println(info);
}
void audio_eof_speech(const char *info){
    Serial.print("eof_speech  ");Serial.println(info);
}

// define two tasks for Music & uart
void TaskButton( void *pvParameters );
void TaskDisplay( void *pvParameters );

void setup() 
{

  // initialize serial communication at 115200 bits per second:
  Serial.begin(115200);
  
  // make the pushbutton's pin an input:
  pinMode(pushButton1, INPUT);
  pinMode(pushButton2, INPUT);
  pinMode(pushButton3, INPUT);


    Wire.begin(I2C_SDA, I2C_SCL);
    delay(1000);

    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
    {
        Serial.println("Now reset the board");
        delay(1000);
        resetFunc();//restart 
       delay(20);
    }
  }
  delay(500);
  display.clearDisplay();

  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);
  //Display static text
  display.println("www.makerfabs.com!");
  display.println("ESP32 Audio Player!");
  display.display();
  delay(2000);
  //max_stations= sizeof(stations)/sizeof(stations[0]); log_i("max stations %i", max_stations);
  
  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(50); // Set BRIGHTNESS to about 1/5 (max = 255)

  colorWipe(strip.Color(255,   255,   255)     , 50);//
  delay(1000);
  // Fill along the length of the strip in various colors...
  delay(500);
  colorWipe(strip.Color(200,   0,   0), 50); // Red
  delay(500);
  //colorWipe(strip.Color(  0, 255,   0), 50); // Green
  //delay(500);
  //colorWipe(strip.Color(  0,   0, 255), 50); // Blue
  //delay(500);
  //colorWipe(strip.Color(  0,   0,   0, 255), 50); // True white (not RGB white)
  //delay(1000);
 
/**
    //connect to WiFi
    Serial.printf("Connecting to %s ", ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println(" CONNECTED");
**/
    sd_init();

    // Read from SD
    music_num = get_music_list(SD, "/", 0, music_list);
    Serial.print("Music file count:");
    Serial.println(music_num);
    Serial.println("All music:");
    for (int i = 0; i < music_num; i++)
    {
        Serial.println(music_list[i]);
    }
    
    audio.setPinout(I2S_BCLK, I2S_LRCK, I2S_DOUT);
    audio.setVolume(21); // 0...21

    open_new_song(music_list[music_index]);

//    audio.connecttoFS(SD, "/320k_test.mp3");
//    audio.connecttoFS(SD, FILE_AUDIO_01);//ChildhoodMemory.mp3  //MoonRiver.mp3
//    audio.connecttoFS(SD, "test.wav");
//    audio.connecttohost("http://www.wdr.de/wdrlive/media/einslive.m3u");
//    audio.connecttohost("http://macslons-irish-pub-radio.com/media.asx");
//    audio.connecttohost("http://mp3.ffh.de/radioffh/hqlivestream.aac"); //  128k aac
//    audio.connecttohost("http://mp3.ffh.de/radioffh/hqlivestream.mp3"); //  128k mp3
//    audio.connecttospeech("Wenn die Hunde schlafen, kann der Wolf gut Schafe stehlen.", "de");
//    audio.connecttohost(stations[cur_station]);

  // some of time is may crash
  // Now set up two tasks to run independently.
  xTaskCreatePinnedToCore(
    TaskButton
    ,  "TaskButton"   // A name just for humans
    ,  12288  // This stack size can be checked & adjusted by reading the Stack Highwater
    ,  NULL
    ,  3  // Priority, with 3 (configMAX_PRIORITIES - 1) being the highest, and 0 being the lowest.
    ,  NULL 
    ,  1//,  ARDUINO_RUNNING_CORE  // Core you want to run the task on (0 or 1)
    );

  xTaskCreatePinnedToCore(
    TaskDisplay
    ,  "TaskDisplay"
    ,  8192  // Stack size
    ,  NULL
    ,  1  // Priority
    ,  NULL 
    ,  ARDUINO_RUNNING_CORE);

    // Now the task scheduler, which takes over control of scheduling individual tasks, is automatically started.
    Serial.println("Begin!");
    delay(1000);
}


/*--------------------------------------------------*/
/*---------------------- Tasks ---------------------*/
/*--------------------------------------------------*/

void TaskButton(void *pvParameters)  // This is a task.
{
  (void) pvParameters;

  Serial.println("Task Button Begin!");
  for (;;) // A Task shall never return or exit.
  {
      // read the input pin:
      int buttonState3 = digitalRead(pushButton3);
      if(!buttonState3) //not work fine should add debounce
      {
        audio.pauseResume();
        showMode=1;
      }
      
      int buttonState1 = digitalRead(pushButton1);
      if(!buttonState1) //not work fine should add debounce
      {
          showMode=2;
          audio.stopSong();
          vTaskDelay(500);
          music_index++;
          if (music_index >= music_num)
          {
              music_index = 0;
          }
          open_new_song(music_list[music_index]);
          Serial.print("Heap: ");Serial.println(ESP.getFreeHeap());
      }

      int buttonState2 = digitalRead(pushButton2);
      if(!buttonState2) //not work fine should add debounce
      {
          showMode=3;
          audio.stopSong();
          vTaskDelay(500);
          music_index--;
          if (music_index < 0)
          {
              music_index = music_num;
          }
          open_new_song(music_list[music_index]);
          Serial.print("Heap: ");Serial.println(ESP.getFreeHeap());
      }
      vTaskDelay(100);
  }
}

void TaskDisplay(void *pvParameters)  // This is a task.
{
  (void) pvParameters;
  
  Serial.println("ESP32 RGB Display Begin!");
  for (;;)
  {
    switch(showMode)
    {
      case 1:
        whiteOverRainbow(75, 5);
      case 2:
        colorWipe(strip.Color(  0, 255,   0), 50); // Green
        delay(500);
      break;
      case 3:
        colorWipe(strip.Color(  0,   0, 255), 50); // Blue
        break;
      
      default:
         rainbowFade2White(3, 3, 1);
      break;
    }
    vTaskDelay(1000);
  }
}

void loop() {

  audio.loop(); 
  delay(1);        // delay in between reads for stability 
}

// Fill strip pixels one after another with a color. Strip is NOT cleared
// first; anything there will be covered pixel by pixel. Pass in color
// (as a single 'packed' 32-bit value, which you can get by calling
// strip.Color(red, green, blue) as shown in the loop() function above),
// and a delay time (in milliseconds) between pixels.
void colorWipe(uint32_t color, int wait) {
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }
}

void whiteOverRainbow(int whiteSpeed, int whiteLength) {

  if(whiteLength >= strip.numPixels()) whiteLength = strip.numPixels() - 1;

  int      head          = whiteLength - 1;
  int      tail          = 0;
  int      loops         = 3;
  int      loopNum       = 0;
  uint32_t lastTime      = millis();
  uint32_t firstPixelHue = 0;

  for(;;) { // Repeat forever (or until a 'break' or 'return')
    for(int i=0; i<strip.numPixels(); i++) {  // For each pixel in strip...
      if(((i >= tail) && (i <= head)) ||      //  If between head & tail...
         ((tail > head) && ((i >= tail) || (i <= head)))) {
        strip.setPixelColor(i, strip.Color(0, 0, 0, 255)); // Set white
      } else {                                             // else set rainbow
        int pixelHue = firstPixelHue + (i * 65536L / strip.numPixels());
        strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(pixelHue)));
      }
    }

    strip.show(); // Update strip with new contents
    // There's no delay here, it just runs full-tilt until the timer and
    // counter combination below runs out.

    firstPixelHue += 40; // Advance just a little along the color wheel

    if((millis() - lastTime) > whiteSpeed) { // Time to update head/tail?
      if(++head >= strip.numPixels()) {      // Advance head, wrap around
        head = 0;
        if(++loopNum >= loops) return;
      }
      if(++tail >= strip.numPixels()) {      // Advance tail, wrap around
        tail = 0;
      }
      lastTime = millis();                   // Save time of last movement
    }
  }
}

void pulseWhite(uint8_t wait) {
  for(int j=0; j<256; j++) { // Ramp up from 0 to 255
    // Fill entire strip with white at gamma-corrected brightness level 'j':
    strip.fill(strip.Color(0, 0, 0, strip.gamma8(j)));
    strip.show();
    delay(wait);
  }

  for(int j=255; j>=0; j--) { // Ramp down from 255 to 0
    strip.fill(strip.Color(0, 0, 0, strip.gamma8(j)));
    strip.show();
    delay(wait);
  }
}

void rainbowFade2White(int wait, int rainbowLoops, int whiteLoops) {
  int fadeVal=0, fadeMax=100;

  // Hue of first pixel runs 'rainbowLoops' complete loops through the color
  // wheel. Color wheel has a range of 65536 but it's OK if we roll over, so
  // just count from 0 to rainbowLoops*65536, using steps of 256 so we
  // advance around the wheel at a decent clip.
  for(uint32_t firstPixelHue = 0; firstPixelHue < rainbowLoops*65536;
    firstPixelHue += 256) {

    for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...

      // Offset pixel hue by an amount to make one full revolution of the
      // color wheel (range of 65536) along the length of the strip
      // (strip.numPixels() steps):
      uint32_t pixelHue = firstPixelHue + (i * 65536L / strip.numPixels());

      // strip.ColorHSV() can take 1 or 3 arguments: a hue (0 to 65535) or
      // optionally add saturation and value (brightness) (each 0 to 255).
      // Here we're using just the three-argument variant, though the
      // second value (saturation) is a constant 255.
      strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(pixelHue, 255,
        255 * fadeVal / fadeMax)));
    }

    strip.show();
    delay(wait);

    if(firstPixelHue < 65536) {                              // First loop,
      if(fadeVal < fadeMax) fadeVal++;                       // fade in
    } else if(firstPixelHue >= ((rainbowLoops-1) * 65536)) { // Last loop,
      if(fadeVal > 0) fadeVal--;                             // fade out
    } else {
      fadeVal = fadeMax; // Interim loop, make sure fade is at max
    }
  }

  for(int k=0; k<whiteLoops; k++) {
    for(int j=0; j<256; j++) { // Ramp up 0 to 255
      // Fill entire strip with white at gamma-corrected brightness level 'j':
      strip.fill(strip.Color(0, 0, 0, strip.gamma8(j)));
      strip.show();
    }
    delay(1000); // Pause 1 second
    for(int j=255; j>=0; j--) { // Ramp down 255 to 0
      strip.fill(strip.Color(0, 0, 0, strip.gamma8(j)));
      strip.show();
    }
  }

  delay(500); // Pause 1/2 second
}

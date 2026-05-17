// #include <ESP8266WiFi.h>
// #include <WebSocketsServer.h> // Библиотека WebSockets
// #include <U8g2lib.h>

// const char* ssid = "HUAWEI-dbRX";
// const char* password = "485754437F456F9D";

// U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0, 12, 14, U8X8_PIN_NONE);
// WebSocketsServer webSocket = WebSocketsServer(81); // Порт для WebSocket

// // Обработчик событий WebSocket
// void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
//   switch(type) {
//     case WStype_TEXT:
//       // Получили команду из браузера -> отправляем в GRBL
//       Serial.println((char*)payload); 
//       break;
//     case WStype_CONNECTED:
//       u8g2.clearBuffer();
//       u8g2.drawStr(0, 10, "Browser Connected");
//       u8g2.sendBuffer();
//       break;
//   }
// }

// void setup() {
//   Serial.begin(115200);
//   u8g2.begin();
//   u8g2.setFont(u8g2_font_6x10_tf);

//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) { delay(500); }

//   webSocket.begin();
//   webSocket.onEvent(onWebSocketEvent);

//   u8g2.clearBuffer();
//   u8g2.setCursor(0, 12);
//   u8g2.print(WiFi.localIP());
//   u8g2.sendBuffer();
// }

// void loop() {
//   webSocket.loop();

//   // Если GRBL что-то ответил -> отправляем всем подключенным браузерам
//   if (Serial.available() > 0) {
//     String resp = Serial.readStringUntil('\n');
//     webSocket.broadcastTXT(resp);
//   }
// }






#include <ESP8266WiFi.h>
#include <WebSocketsServer.h>
#include <U8g2lib.h>

const char* ssid = "HUAWEI-dbRX";
const char* password = "485754437F456F9D";

U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0, 12, 14, U8X8_PIN_NONE);
WebSocketsServer webSocket = WebSocketsServer(81);

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    if (type == WStype_TEXT) {
        // Получаем G-код от клиента и отправляем в Serial
        Serial.println((char*)payload);
    }
}

void setup() {
    Serial.begin(115200);
    u8g2.begin();
    
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }

    webSocket.begin();
    webSocket.onEvent(webSocketEvent);
}

// void loop() {
//     webSocket.loop();

//     // Проверяем, есть ли данные в порту
//     size_t len = Serial.available();
//     if (len > 0) {
//         // Создаем временный буфер
//         uint8_t sbuf[len];
//         // Читаем ровно столько байт, сколько пришло
//         Serial.readBytes(sbuf, len);
//         // Отправляем клиенту как бинарные данные или текст
//         // broadcastTXT корректно работает с массивом байт и длиной
//         webSocket.broadcastTXT(sbuf, len);
//     }
// }

void loop() {
    webSocket.loop();

    static String inputBuffer = ""; 

    while (Serial.available() > 0) {
        char c = Serial.read();
        
        if (c == '\n') {
            // Если пришел конец строки, отправляем накопленное
            if (inputBuffer.length() > 0) {
                webSocket.broadcastTXT(inputBuffer);
                inputBuffer = "";
            }
        } else if (c != '\r') {
            // Накапливаем символы (игнорируя возврат каретки)
            inputBuffer += c;
        }
    }
}



// test4 + этот файл работает test3 еще лучше




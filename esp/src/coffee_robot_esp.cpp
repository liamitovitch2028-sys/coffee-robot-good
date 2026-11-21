#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiManager.h>
#include <ESP32Servo.h>

String bot_id = "000003";

unsigned long lastCheck = 0;

// Timer variables
unsigned long countdownEnd = 0;
bool timerRunning = false;

Servo myServo;

#define SERVO_PIN 27


void sendOnline(){

    if(WiFi.status() == WL_CONNECTED){

        WiFiClient client;
        HTTPClient http;

        Serial.println("Connecting to server...");

        http.begin("https://expressobot.up.railway.app//online");

        http.addHeader("Content-Type", "application/json");

        String data = "{\"id\":\"" + bot_id + "\"}";

        Serial.println(data);

        int response = http.POST(data);

        Serial.print("HTTP response: ");
        Serial.println(response);

        if(response > 0){
            Serial.println(http.getString());
        }
        else{
            Serial.println(http.errorToString(response));
        }

        http.end();
    }
}


void checkCommands(){

    if(WiFi.status() == WL_CONNECTED){

        HTTPClient http;

        http.begin(
            "https://expressobot.up.railway.app//request?id=" + bot_id
        );

        int response = http.GET();

        Serial.print("GET response: ");
        Serial.println(response);

        if(response > 0){

            String result = http.getString();

            result.trim();

            Serial.print("Server response: ");
            Serial.println(result);


            // =========================
            // PRESS IMMEDIATELY
            // =========================

            if(result == "press"){

                Serial.println("START COFFEE");

                // Abort any existing timer
                timerRunning = false;

                // Press motor
                int angle = myServo.read();

                while(angle < 100){

                    angle++;

                    myServo.write(angle);

                    delay(10);
                }

                delay(1000);

                myServo.write(40);

                Serial.println("COFFEE STARTED");
            }


            // =========================
            // CANCEL TIMER
            // =========================

            else if(result == "cancel_timer"){

                Serial.println("CANCELLING TIMER");

                timerRunning = false;

                Serial.println("TIMER CANCELLED");
            }


            // =========================
            // TIMER
            // =========================

            else {

                int timerSeconds = result.toInt();

                if(timerSeconds > 0){

                    Serial.print("Starting timer for ");
                    Serial.print(timerSeconds);
                    Serial.println(" seconds");

                    countdownEnd =
                        millis() +
                        ((unsigned long)timerSeconds * 1000);

                    timerRunning = true;
                }
            }
        }

        http.end();
    }
}


void checkTimer(){

    if(!timerRunning){
        return;
    }

    // Check if timer has finished
    if((long)(millis() - countdownEnd) >= 0){

        Serial.println("TIMER FINISHED");

        timerRunning = false;

        Serial.println("PRESSING MOTOR");

        int angle = myServo.read();

        while(angle < 100){

            angle++;

            myServo.write(angle);

            delay(10);
        }

        delay(1000);

        myServo.write(40);

        Serial.println("MOTOR FINISHED");
    }
}


void setup(){

    myServo.attach(SERVO_PIN);
    myServo.write(40);

    Serial.begin(115200);

    WiFiManager wifiManager;

    if(!wifiManager.autoConnect("CoffeeBot-Setup")){
        ESP.restart();
    }

    Serial.println("Connected!");

    delay(3000);

    sendOnline();
}


void loop(){

    // Check server every 3.5 seconds
    if(millis() - lastCheck > 3500){

        checkCommands();

        lastCheck = millis();
    }

    // Check the timer continuously
    checkTimer();
}

// 3FCD55319C3C
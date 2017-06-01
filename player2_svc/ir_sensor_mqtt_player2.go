package main

import (
  "gobot.io/x/gobot"
  "gobot.io/x/gobot/platforms/mqtt"
  "gobot.io/x/gobot/drivers/gpio"
  "gobot.io/x/gobot/platforms/firmata"
  "time"
  "strconv"
  //"fmt"
)

func main() {
        mqttAdaptor := mqtt.NewAdaptor("tcp://test.mosquitto.org:1883", "blinker")
        firmataAdaptor := firmata.NewTCPAdaptor("foosballyun2.local:5055")
        sensor := gpio.NewDirectPinDriver(firmataAdaptor, "4")
        led := gpio.NewLedDriver(firmataAdaptor, "13")
        sensorState := "LOW"
        lastState := "LOW"

        work := func() {
                mqttAdaptor.On("lights/on", func(msg mqtt.Message) {

                })
                gobot.Every(1*time.Millisecond, func() {
                        data, _ := sensor.DigitalRead()
                        if data == 1{
                          led.Off()
                          //sensor.DigitalWrite(1)
                          sensorState = "LOW"
                          //fmt.Println(data)
                        } else {
                          led.On()
                          sensorState = "HIGH"
                        }
                        if sensorState == "LOW" && lastState == "HIGH"{
                          mqttAdaptor.Publish("lights/on", []byte("{'Status': 'scored', 'Player': '2', 'Score': 0, 'Data':" + strconv.Itoa(data) + "}"))
                          //time.Sleep(1000*time.Millisecond)
                        }
                        if sensorState == "HIGH" && lastState == "HIGH"{
                          mqttAdaptor.Publish("lights/on", []byte("{'Status': 'scored', 'Player': '2', 'Score': 1, 'Data':" + strconv.Itoa(data) + "}"))
                          time.Sleep(1000*time.Millisecond)
                        }
                        lastState = sensorState
                })
        }

        robot := gobot.NewRobot("mqttBot",
                []gobot.Connection{mqttAdaptor, firmataAdaptor},
                []gobot.Device{sensor},
                work,
        )

        robot.Start()
}

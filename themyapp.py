from core import metrics, controls
from core.enums import DeviceType, MetricType
import time

#min_temperature = 12

kW_event_threshold = 2.0
fall_events = []

time0_hours = time.localtime()[3]
time0_mins = time.localtime()[4]
power_events = []

inactivity_alarm = 180 #minutes
inactivity_concern = 120 #minutes
inactivity_events = []

alarm_raised = False

#function is used to raise an alarm where red means danger or person has fallen
def raise_alarm(message):
    global alarm_raised
    alarm_raised = True

    controls.set_device_state(DeviceType.RED_LAMP, True)
    controls.set_device_state(DeviceType.BLUE_LAMP, False) 
    controls.set_device_state(DeviceType.GREEN_LAMP, False)
    
    print(message)
    return

def handle_all(metric):
    #print(metric)
    #sleep(10)
    pass

#def handle_temperature(temperature):
    #print(f"Temperature: {temperature.value}")
    #controls.set_device_state(DeviceType.BLUE_LAMP, temperature.value <= min_temperature)
    #pass

def handle_co2(co2):
    #print(f"CO2: {co2.value}")
    pass

#myeventhandlers
#vibration to tell when the person is in trouble
def handle_temperature(temperature):
    if temperature.value <18:
        controls.set_device_state(DeviceType.HEATER, True)
    elif temperature.value >21:
        controls.set_device_state(DeviceType.HEATER, False) 


def run():
    metrics.connect()

    print("Successfully connected to metric stream")
    print(f'Time set: {time0_hours} hrs {time0_mins} mins')

    metrics.handle_all(handle_all)
    metrics.handle(MetricType.IFM_TEMPERATURE, handle_temperature)
    #metrics.handle(MetricType.EPC_CO2, handle_co2)

    #mycode
    #metrics.handle(MetricType.IFM_VIBRATION, handle_vibration)
    #metrics.handle(MetricType.METER_KW, handle_meter)
    #metrics.handle(MetricType.METER_AMPS, handle_meter)


    # Wait for the program to exit
    while True:
        pass

if __name__ == '__main__':
    run()

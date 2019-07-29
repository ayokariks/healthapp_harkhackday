from core import metrics, controls
from core.enums import DeviceType, MetricType
import time

#min_temperature = 12

kW_event_threshold = 0.5 # 2.0 kilowatts
fall_events = []
power_events = []

inactivity_alarm = 3 # 180 minutes
inactivity_concern = 2 # 120 minutes
inactivity_events = []

immobility_alarm = 300 # 60 seconds
timer_mins = time.localtime()[4]
timer_secs = time.localtime()[5]

alarm_raised = False
concern_raised = False

def urgent_alarm(message):
    global alarm_raised
    alarm_raised = True

    controls.set_device_state(DeviceType.RED_LAMP, True)
    controls.set_device_state(DeviceType.BLUE_LAMP, False)
    controls.set_device_state(DeviceType.GREEN_LAMP, False)
    
    print(message)
    print('red lamp on, blue and green lamps off') #testing

    return

def countdown(instruction = 'count'):
    global timer_mins, timer_secs
    if instruction != 'count': # reset countdown timer
        timer_mins = time.localtime()[4]
        timer_secs = time.localtime()[5]
    else: # calculate time elapsed
        mins = time.localtime()[4] - timer_mins
        secs = time.localtime()[5] - timer_secs
        if mins < 0: # correct for minutes resetting on next hour
            mins += 60
        interval = mins*60 + secs
        if interval > immobility_alarm:
            urgent_alarm('No heartrate or respiration detected')
    return

def raise_alarm(message):
    global alarm_raised
    alarm_raised = True

    controls.set_device_state(DeviceType.RED_LAMP, True)
    controls.set_device_state(DeviceType.BLUE_LAMP, False)
    controls.set_device_state(DeviceType.GREEN_LAMP, False)
    
    print(message)
    print('red lamp on, blue and green lamps off') #testing
    return

def handle_all(metric):
    #print(metric)
    #sleep(10)
    pass

def handle_temperature(temperature):
    #print(f"Temperature: {temperature.value}")
    #controls.set_device_state(DeviceType.BLUE_LAMP, temperature.value <= min_temperature)
    pass

def handle_co2(co2):
    #print(f"CO2: {co2.value}")
    pass

#myeventhandlers
def handle_vibration(vibration):

    if vibration.value > 0:
        print(f"Vibration: {vibration.value}")
    
    if vibration.value == 0:
        #set countdown alarm for cardiorespiratory arrest
        pass
    elif vibration.value <= 5 and not alarm_raised:
        controls.set_device_state(DeviceType.GREEN_LAMP, True) 
        print('green lamp on')   # testing
    elif vibration.value > 10:
        fall_events.append(time.localtime()) #date & exact time
        raise_alarm('Fall detected, please call to check')

    return

def handle_meter(kilowatts):
    global concern_raised
    #print(kilowatts.value) #testing

    if not power_events: #set initial value
        print('tested True')
        power_events.append(((time.localtime()[3],
                                time.localtime()[4]),
                                kilowatts.value))
        print(power_events) # testing
    
    #retrieve last recorded significant change in power use
    last_time, last_power = power_events[-1] 

    if kilowatts.value > kW_event_threshold:
        if kilowatts.value > 2*last_power:
            #log significant increase in power consumption 
            power_events.append(((time.localtime()[3], #hours
                                        time.localtime()[4]), #mins
                                        kilowatts.value))
            print(power_events) #testing

    elif kilowatts.value < last_power/2:
        #log significant drop in power consumption
        power_events.append(((time.localtime()[3], #hours
                                time.localtime()[4]), #mins
                                kilowatts.value))
        print(power_events) #testing

    else:
        #calculate interval since last significant power change
        interval_hours = time.localtime()[3] - last_time[0]
        interval_minutes = time.localtime()[4] - last_time[1]
        #correct negative hours if passed midnight
        if interval_hours < 0:
            interval_hours += 24
        interval = interval_hours*60 + interval_minutes

        #respond to time interval since eg kettle last boiled
        if interval > inactivity_alarm and not alarm_raised:
            raise_alarm(f'No activity for over {inactivity_alarm} mins!'
                        f'\nPlease check urgently')
        elif interval > inactivity_concern and concern_raised == False:
            concern_raised = True
            controls.set_device_state(DeviceType.BLUE_LAMP, True)
            print('blue lamp on') #testing
        
    return
    

def run():
    metrics.connect()

    print("Successfully connected to metric stream")
    print(f'Started at {time.localtime()[3]}:{time.localtime()[4]}')

    controls.set_device_state(DeviceType.RED_LAMP, False)    
    controls.set_device_state(DeviceType.BLUE_LAMP, False)    
    controls.set_device_state(DeviceType.GREEN_LAMP, False)    


    metrics.handle_all(handle_all)
    metrics.handle(MetricType.IFM_TEMPERATURE, handle_temperature)
    metrics.handle(MetricType.EPC_CO2, handle_co2)

    #mycode
    metrics.handle(MetricType.IFM_VIBRATION, handle_vibration)
    metrics.handle(MetricType.METER_KW, handle_meter)
    #metrics.handle(MetricType.METER_AMPS, handle_meter)


    # Wait for the program to exit
    while True:
        pass

if __name__ == '__main__':
    run()

import time
import threading
import datetime

from TextToSpeech import TextToSpeech

class RemindersData(object):
    def __init__(self, pk, medication, note, start_date, everyday, interday, specificday, continuous, numday, remindertimes):
        self.pk = pk
        self.medication = medication
        self.note = note
        self.start_date = start_date
        self.everyday = everyday
        self.interday = interday
        self.specificday = specificday
        self.continuous = continuous
        self.numday = numday
        self.remindertimes = remindertimes


# Get data from database

class ReminderThread:
    def __init__(self):
        self.retrieve_file = self.retrieve_data_from_database()
        self.text_to_speech = TextToSpeech()
        self.alarms_list_done = []
        self.alarms_list_before_time = []
        self.alarms_list_in_time = []
        self.alarms_list_after_time = []
        self.quantity_intake = []
        self.quit_click = False

    def retrieve_data_from_database(self):
        file_retrieve = []
        text_file = open("/home/pi/Desktop/DP_final/ProjectDesign/database/Reminder.txt", 'r')
        new_data = []
        text_retrieve = text_file.readlines()
        for length_of_list in range(0,len(text_retrieve)):
            new_data = text_retrieve[length_of_list].split(',')
            file_retrieve.append(RemindersData(new_data[0], new_data[1], new_data[2], new_data[3], new_data[4], new_data[5], new_data[6], new_data[7], new_data[8], new_data[9]))
        text_file.close()
        return file_retrieve

    def process_start_date_process1(self, params):
        todays_reminders = []
        for data in range(len(params)):
            get_date = params[data].start_date
            pars_get_date = datetime.datetime.strptime(get_date, "%Y-%m-%d")
            subtracted_days = datetime.datetime.now() - pars_get_date
            if int(subtracted_days.days) >= 0:
                todays_reminders.append(params[data])
            else:
                pass
        return todays_reminders

    def process_days_process2(self, params):
        todays_reminders = []
        for data in range(len(params)):
            if int(params[data].everyday) == 1:
                todays_reminders.append(params[data])
            elif int(params[data].interday) != 0:
                date_start = params[data].start_date 
                calculate_day_pass = datetime.datetime.now()- datetime.datetime.strptime(date_start, "%Y-%m-%d") 
                subtracted_days = int(calculate_day_pass.days) % int(params[data].interday)
                if subtracted_days == 0:
                    todays_reminders.append(params[data])
            else:
                days_of_week_selected = params[data].specificday.split('-')
                get_days_of_week_today = self.get_day_of_week()
                for dates in range(len(days_of_week_selected)):
                    if days_of_week_selected[dates] == get_days_of_week_today:
                        todays_reminders.append(params[data])

        return todays_reminders


    def get_day_of_week(self):
        date = datetime.datetime.now().strftime("%A")
        date_return = ""
        if date == "Monday":
            date_return = "M"
        elif date == "Tuesday":
            date_return = "T"
        elif date == "Wednesday":
            date_return = "W"
        elif date == "Thursday":
            date_return = "TH"
        elif date == "Friday":
            date_return = "F"
        elif date == "Saturday":
            date_return = "Sat"
        elif date == "Sunday":
            date_return = "Sun"
        return date_return

    def process_duration_process3(self, params):
        todays_reminders = []
        for data in range(len(params)):
            get_date = params[data].start_date
            pars_get_date = datetime.datetime.strptime(get_date, "%Y-%m-%d")
            subtracted_days = datetime.datetime.now() - pars_get_date
            if int (params[data].continuous) == 1:
                todays_reminders.append(params[data])
            else:
                date_duration = params[data].numday
                if int(params[data].interday) != 0:
                    total_days_inter = int(params[data].interday) * int(date_duration)
                    if int(subtracted_days.days) <= total_days_inter:
                        todays_reminders.append(params[data])
                    else:
                        pass
                else:
                    pass
                days_of_week_selected = params[data].specificday.split('-')
                total_days_speci = date_duration * len(days_of_week_selected)
                if params[data].specificday != "disabled":
                    if int(subtracted_days.days) < int(total_days_speci):
                        todays_reminders.append(params[data])
                    else:
                        pass
                else:
                    pass
        return todays_reminders

    def process_time_process4(self, params):
        get_alarm_time =[]
        for alarm in range(len(params)):
            get_alarm_time = params[alarm].remindertimes.split('$')
            for time in range(len(get_alarm_time)):
                if get_alarm_time[time].find(".") == 1 or get_alarm_time[time] == 'Interval:' or get_alarm_time[time] == '' or get_alarm_time[time] == 'Frequency:':
                    pass
                else:
                    get_time_start = datetime.datetime.now() - datetime.timedelta(seconds = 1200)
                    get_time_middle = datetime.datetime.now()
                    get_time_end = datetime.datetime.now() + datetime.timedelta(seconds = 1200)
                    #convert_alarm_time = datetime.datetime.strptime(get_alarm_time[time], "%H:%M")
                    convert_alarm_time = get_alarm_time[time]
                    if convert_alarm_time == get_time_start.strftime("%H:%M"):
                        self.alarms_list_after_time.append(params[alarm])
                        self.quantity_intake.append(get_alarm_time[time+1])
                    elif convert_alarm_time == get_time_end.strftime("%H:%M"):
                        self.alarms_list_before_time.append(params[alarm])
                        self.quantity_intake.append(get_alarm_time[time+1])
                    elif convert_alarm_time == get_time_middle.strftime("%H:%M"):
                        self.alarms_list_in_time.append(params[alarm])
                        self.quantity_intake.append(get_alarm_time[time+1])

    def msg_medication_alarm_before_time(self, medication_name, quantity):
        msg = "Hey! I am your care companion for today. Please do not forget to take " + quantity + " " + medication_name + " 20 mins from now."
        return msg

    def msg_medication_alarm_in_time(self, medication_name, quantity):
        msg = "Hello Dear! It's time to take " + quantity + " of " + medication_name + ". Thank You!"
        return msg

    def msg_medication_alarm_after_time(self, medication_name, quantity):
        msg = "Darling! 20 minutes had past. Have you taken " + quantity + " of " + medication_name + " already? If not, Better to take it now. Thank you!"
        return msg

    def reminder_process(self):
        list_msg = []
        while not self.thread.stopped:
            self.retrieve_file = self.retrieve_data_from_database()
            print("Reading time for reminders")
            process1 = self.process_start_date_process1(self.retrieve_file)
            process2 = self.process_days_process2(process1)
            process3 = self.process_duration_process3(process2)
            self.process_time_process4(process3)
            list_msg = self.process_msg_alarm(self.alarms_list_before_time, self.alarms_list_in_time, self.alarms_list_after_time)
            self.text_to_speech.start_talk(list_msg)
            self.alarms_list_before_time = []
            self.alarms_list_after_time = []
            self.alarms_list_in_time = []
            self.quantity_intake = []
            list_msg = []
            sleep_cnt = 60
            while sleep_cnt > 0 and not self.quit_click:
                sleep_cnt = sleep_cnt - 1
                time.sleep(1)

    def process_msg_alarm(self, alarm1, alarm2, alarm3):
        msg_output = []
        cnt = 0
        if len(alarm1) != 0:
            for x in range(len(alarm1)):
                msg_output.append(self.msg_medication_alarm_before_time(alarm1[x].medication, self.quantity_intake[cnt]))
                cnt = cnt + 1
        elif len(alarm2) != 0:
            for y in range(len(alarm2)):
                msg_output.append(self.msg_medication_alarm_in_time(alarm2[y].medication, self.quantity_intake[cnt]))
                cnt = cnt + 1
        elif len(alarm3) != 0:
            for z in range(len(alarm3)):
                msg_output.append(self.msg_medication_alarm_after_time(alarm3[z].medication, self.quantity_intake[cnt]))
                cnt = cnt + 1
        return msg_output

    def start_reminder_thread(self):
        self.thread = threading.Thread(target=self.reminder_process)
        self.thread.stopped = False
        self.thread.start()
        return

    def stop_reminder_thread(self):
        self.thread.stopped = True
        return

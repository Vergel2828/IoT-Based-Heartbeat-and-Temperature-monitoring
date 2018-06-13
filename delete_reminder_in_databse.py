import time
import threading

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

class DeleteReminder:
    def __init__(self):
        self.reminder_to_delete = "/home/pi/Desktop/DP_final/ProjectDesign/database/Reminder.txt"

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

    def remove_the_selected(self, pk_to_delete, rt_file):
        new_data = []
        print(len(rt_file))
        for data_index in range(len(rt_file)):
            if rt_file[data_index].pk == pk_to_delete:
                pass
            else:
                new_data.append(rt_file[data_index])
        return new_data

    def save_new_data_to_data_base(self, params):
        data_to_save = ''
        for length_of_params in range(len(params)):
            data_to_save = data_to_save + '{},{},{},{},{},{},{},{},{},{},\n'.format(params[length_of_params].pk,
                params[length_of_params].medication,
                params[length_of_params].note,
                params[length_of_params].start_date,
                params[length_of_params].everyday,
                params[length_of_params].interday,
                params[length_of_params].specificday,
                params[length_of_params].continuous,
                params[length_of_params].numday,
                params[length_of_params].remindertimes
                )
        text_file = open("/home/pi/Desktop/DP_final/ProjectDesign/database/Reminder.txt", 'w')
        text_file.write(data_to_save)
        text_file.close()

    def delete_process(self, pk_to_delete):
        data_from_database = self.retrieve_data_from_database()
        new_data_to_save = self.remove_the_selected(pk_to_delete, data_from_database)
        self.save_new_data_to_data_base(new_data_to_save)

    def start_thread_delete(self, pk_to_delete):
        self.thread = threading.Thread(target=self.delete_process, args=(pk_to_delete,))
        self.thread.start()
        return

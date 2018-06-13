import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style

import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox

from PIL import Image

import time
import datetime
import threading
import urllib.request
import calendar_picker
import alsaaudio

from threadwrite import WriteThread
from temperature_thread import TempThread
from senddatabase import SendToDatabase
from count_down_thread import CounterThread
from save_to_temp_database import WriteReadingTemp
from save_to_heart_database import WriteReadingPulse
from TextToSpeech import TextToSpeech
from reminder_thread import ReminderThread
from delete_reminder_in_databse import DeleteReminder

LARGE_FONT = ("Century Gothic", 15)
rt = ReminderThread()

class Users(object):
    def __init__(self, lastname, firstname, middlename, emailadd, birthday, gender, number1, username, password):
        self.lastname = lastname
        self.firstname = firstname
        self.middlename = middlename
        self.emailadd = emailadd
        self.birthday = birthday
        self.gender = gender
        self.number1 = number1
        self.username = username
        self.password = password


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


class ProjectDesignApplication(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Monitoring System")
        #tk.Tk.geometry(self, "800x500")                       #Set Dimension
        tk.Tk.attributes(self,"-fullscreen", True)             #Set Gui to fullscreen     

        container = tk.Frame(self)
        container.pack(side = "top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        rt.start_reminder_thread()

        self.frames = {}

        for F in (StartPage, RegisterPage, LoginPage, ReminderPage, SettingPage, AddReminder, SetReminderTimes, MonitoringPage, RecordsPage):

            frame = F(container, self)
            self.frames[F] = frame

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid(row = 0, column = 0, sticky = "nsew")

    def hide_frame(self, cont):
        frame = self.frames[cont]
        frame.grid_forget()

    def updates_set_reminder(self, cont):
        frame = self.frames[cont]
        frame.display_reminder_times_details()

    def refresh_table(self, cont):
        frame = self.frames[cont]
        frame.insert_data_to_table()

    def clean_remidertimes_page(self, cont):
        frame = self.frames[cont]
        frame.clean_self()

    def start_plotting(self, cont):
        frame = self.frames[cont]
        frame.start_heart_plot()

    def thread_writer(self, cont):
        frame = self.frames[cont]
        frame.start_sensor_pulse_reading()

    def start_temperature(self, cont):
        frame = self.frames[cont]
        frame.refresh_display_temp()

    def start_pulse(self, cont):
        frame = self.frames[cont]
        frame.refresh_display_pulse()

    def start_pause_count(self, cont):
        frame = self.frames[cont]
        frame.start_counting()

    def instruction_talk(self, cont):
        frame = self.frames[cont]
        frame.tts_talk()

    def login_clear(self, cont):
        frame = self.frames[cont]
        frame.clear_inputs()
        

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.photo = tk.PhotoImage(file = "/home/pi/Desktop/DP_final/ProjectDesign/img/logomain.png")
        self.program_logo = tk.Label(self, image = self.photo)
        self.program_logo.photo = self.photo
        self.program_logo.grid(row = 0, column = 0, rowspan = 20, sticky = "nsew")

        self.register_button = tk.Button(self, text="Start New Account", font=LARGE_FONT, height = "2",command = self.register_function)
        self.register_button.grid(row = 8, column = 1, sticky = "ew")

        self.login_button = tk.Button(self, text="Login Existing Account", font=LARGE_FONT, height = "2", command = self.login_function)
        self.login_button.grid(row = 9, column = 1, sticky = "ew")

        self.reminder_button = tk.Button(self, text="Create Medicine Reminder", font=LARGE_FONT, height = "2", command = self.reminder_function)
        self.reminder_button.grid(row = 10, column = 1, sticky = "ew")

        self.setting_button = tk.Button(self, text="Settings", font=LARGE_FONT, height = "2", command = self.setting_function)
        self.setting_button.grid(row = 11, column = 1, sticky = "ew")

        self.exit_button = tk.Button(self, text="Exit", font=LARGE_FONT, height = "2", command = self.quit_function)
        self.exit_button.grid(row = 12, column = 1, sticky = "ew")

    def register_function(self):
        self.controller.hide_frame(StartPage)
        self.controller.show_frame(RegisterPage)

    def login_function(self):
        self.controller.hide_frame(StartPage)
        self.controller.show_frame(LoginPage)

    def reminder_function(self):
        self.controller.hide_frame(StartPage)
        self.controller.show_frame(ReminderPage)

    def setting_function(self):
        self.controller.hide_frame(StartPage)
        self.controller.show_frame(SettingPage)

    def quit_function(self):
        result = msgbox.askquestion("Logout", "Are you sure?", icon='warning')
        if result == 'yes':
            rt.stop_reminder_thread()
            rt.quit_click = True
            quit()
        else:
            return


class RegisterPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.var = tk.IntVar()
        self.var.set(0)
        self.date_value = tk.StringVar()
        self.date_value.set("")

        self.label = tk.Label(self, text="Account information", font=("century gothic", 20), height = 2)
        self.label.grid(row = 0, column = 0, columnspan = 5, sticky = "nsew")    

        self.label_lname = tk.Label(self, text="Last Name: ", font=LARGE_FONT)
        self.label_lname.grid(row = 1, column = 0, sticky = "w", padx = 2, pady = 3)
        self.input_lname = tk.Entry(self, width = 20, font=LARGE_FONT)
        self.input_lname.grid(row = 2, column = 0, sticky = "we", padx = 2, pady = 3)

        self.label_fname = tk.Label(self, text="First Name: ", font=LARGE_FONT)
        self.label_fname.grid(row = 1, column = 1, columnspan = 2, sticky = "w", padx = 2, pady = 3)
        self.input_fname = tk.Entry(self, width = 20, font=LARGE_FONT)
        self.input_fname.grid(row = 2, column = 1, columnspan = 2, sticky = "we", padx = 2, pady = 3)

        self.label_Mname = tk.Label(self, text="Middle Name: ", font=LARGE_FONT)
        self.label_Mname.grid(row = 1, column = 3, sticky = "w", padx = 2, pady = 3)
        self.input_Mname = tk.Entry(self, width = 19, font=LARGE_FONT)
        self.input_Mname.grid(row = 2, column = 3, columnspan = 2, sticky = "we", padx = 2, pady = 3)

        self.label_email = tk.Label(self, text="Email Address: ", font=LARGE_FONT)
        self.label_email.grid(row = 3, column = 0, sticky = "w", padx = 2, pady = 3)
        self.input_email = tk.Entry(self, width = 19, font=LARGE_FONT)
        self.input_email.grid(row = 4, column = 0, columnspan = 3, sticky = "we", padx = 2, pady = 3)

        self.pic_display = tk.Label(self,text = "", bg = "white")
        self.pic_display.grid(row = 3, column = 3, columnspan = 2, rowspan = 8, sticky = "nsew", padx = 4, pady = 4)

        self.label_birthday = tk.Label(self, text="Birthday: ", font=LARGE_FONT)
        self.label_birthday.grid(row = 5, column = 0, sticky = "w", padx = 2, pady = 3)
        calendar_picker.Datepicker(self, datevar = self.date_value).grid(row = 6, column = 0, sticky = "we", padx = 2, pady = 3)

        self.label_gender = tk.Label(self, text="Gender: ", font=LARGE_FONT)
        self.label_gender.grid(row = 5, column = 1, sticky = "w", padx = 2, pady = 3)
        self.select_female = tk.Radiobutton(self, text = "Female", variable = self.var, value = 1, font = LARGE_FONT)
        self.select_female.grid(row = 6, column = 1, sticky = "w" , pady = 3)        
        self.select_male = tk.Radiobutton(self, text = "Male", variable = self.var, value = 2, font = LARGE_FONT)
        self.select_male.grid(row = 6, column = 2, sticky = "w" , pady = 3)

        self.label_cp1 = tk.Label(self, text="Cellphone number: ", font=LARGE_FONT)
        self.label_cp1.grid(row = 7, column = 0, sticky = "w", padx = 2, pady = 1)
        self.input_cp1 = tk.Entry(self, width = 20, font=LARGE_FONT)
        self.input_cp1.grid(row = 8, column = 0, sticky = "we", padx = 2, pady = 1)

        self.user_name = tk.Label(self, text="Username:", font=LARGE_FONT)
        self.user_name.grid(row = 7, column = 1, columnspan = 2, sticky = "w", padx = 2, pady = 1)
        self.user_name = tk.Entry(self, width = 20, font=LARGE_FONT)
        self.user_name.grid(row = 8, column = 1, columnspan = 2, sticky = "we", padx = 2, pady = 1)

        self.label_password1 = tk.Label(self, text="Create Password: ", font=LARGE_FONT)
        self.label_password1.grid(row = 9, column = 0, sticky = "w", padx = 2, pady = 1)
        self.input_password1 = tk.Entry(self, width = 20, font=LARGE_FONT, show ="*")
        self.input_password1.grid(row = 10, column = 0, sticky = "we", padx = 2, pady = 1)

        self.label_password2 = tk.Label(self, text="Confirm Password: ", font=LARGE_FONT)
        self.label_password2.grid(row = 9, column = 1, columnspan = 2, sticky = "w", padx = 2, pady = 1)
        self.input_password2 = tk.Entry(self, width = 20, font=LARGE_FONT, show ="*")
        self.input_password2.grid(row = 10, column = 1, columnspan =2, sticky = "we", padx = 2, pady = 1)

        self.submit_button = tk.Button(self, text = "Submit", font = LARGE_FONT, command = self.save_profile)
        self.submit_button.grid(row = 11, column = 3, sticky = "e")

        self.cancel_button = tk.Button(self, text = "Cancel", font = LARGE_FONT,command = self.cancel_function)
        self.cancel_button.grid(row = 11, column = 4, sticky = "e", padx = 2)

    def gender_selected(self):
        if self.var.get() == 1:
            return ("female")
        elif self.var.get() == 2:
            return ("male")

    def is_input_not_space(self,user_input):
        if user_input.replace(" ","") is not "":
            return True
        else:
            return False

    def is_password_same(self,pass1,pass2):
        if pass1 == pass2:
            return True
        else:
            msgbox.showerror("Registration failed!","Password does not match.")
            return False

    def return_error_message(self):
        error_valid = 0
        if not self.is_input_not_space(self.input_lname.get()):
            error_valid = 1 
        elif not self.is_input_not_space(self.input_fname.get()):
            error_valid = 2           
        elif not self.is_input_not_space(self.input_Mname.get()):    
            error_valid = 3
        elif not self.is_input_not_space(self.input_email.get()):  
            error_valid = 4
        elif not self.is_input_not_space(self.input_cp1.get()):
            error_valid = 5
        elif not self.is_input_not_space(self.input_cp2.get()):    
            error_valid = 6
        elif not self.is_input_not_space(self.input_password1.get()):    
            error_valid = 7
        elif self.var.get() == 0:    
            error_valid = 8
        elif self.date_value.get() == "":   
            error_valid = 9
        else:
            error_valid = 0
        return error_valid

    def display_error(self,params):
        if params == 1:
            msgbox.showerror("Registration failed!","Please dont leave the last name blank.")
        elif params == 2:
            msgbox.showerror("Registration failed!","Please dont leave the first name blank.")
        elif params == 3:
            msgbox.showerror("Registration failed!","Please dont leave the middle name blank.")
        elif params == 4:
            msgbox.showerror("Registration failed!","Please dont leave the email address blank.")
        elif params == 5:
            msgbox.showerror("Registration failed!","Please dont leave the cellphone number blank.")
        elif params == 6:
            msgbox.showerror("Registration failed!","Please dont leave the username blank.")
        elif params == 7:
            msgbox.showerror("Registration failed!","Please dont leave the password blank.")
        elif params == 8:
            msgbox.showerror("Registration failed!","Please select gender")
        elif params == 9:
            msgbox.showerror("Registration failed!","Please dont leave the birthday blank")
        elif params == 0:
            print ("No Error")

    def clear_data(self):
        self.var.set(0)
        self.input_lname.delete(0,"end")
        self.input_fname.delete(0,"end")
        self.input_Mname.delete(0,"end")
        self.input_email.delete(0,"end")
        self.date_value.set("")
        self.input_cp1.delete(0,"end")
        self.user_name.delete(0,"end")
        self.input_password1.delete(0,"end")
        self.input_password2.delete(0,"end")

    def is_already_registered(self,database):
        is_registered = False
        for data in range(len(database)):
            if database[data].lastname == self.input_lname.get() and database[data].firstname == self.input_fname.get() and database[data].middlename == self.input_Mname.get():
                msgbox.showerror("Registration failed!","Account already exist.")
                is_registered = True
                return is_registered
                break
            else:
                is_registered = False
        return is_registered

    def append_profile(self):
        retrieve_database_profile_data.append(Users(self.input_lname.get(), self.input_fname.get(), self.input_Mname.get(), self.input_email.get(), self.date_value.get(), self.gender_selected(), self.input_cp1.get(), self.input_cp2.get(), self.input_password2.get()))

    def save_to_data_base(self):
        myurl = '192.168.254.109:8000/health/register/'
        data_to_save = self.input_lname.get()+'/'+self.input_fname.get()+'/'+self.input_Mname.get()+'/'+self.input_email.get()+'/'+self.date_value.get()+'/'+self.gender_selected()+'/'+self.input_cp1.get()+'/'+self.input_cp2.get()+'/'+self.input_password2.get()
        contents = urllib.request.urlopen(myurl+data_to_save)
        print(contents)

    def create_datatemp_for_every_user(self,database_name):
        text_file = open ("/home/pi/Desktop/DP_final/ProjectDesign/database/temperature/" + database_name, 'w+')
        text_file.close()

    def create_dataheart_for_every_usr(self,database_name):
        text_file = open ("/home/pi/Desktop/DP_final/ProjectDesign/database/heartbeat/" + database_name, 'w+')
        text_file.close()

    def save_to_text_file(self,params):
        data_to_save = ''
        for length_of_params in range(len(params)):
            data_to_save = data_to_save + '{},{},{},{},{},{},{},{},{},\n'.format(params[length_of_params].lastname,
                params[length_of_params].firstname,
                params[length_of_params].middlename,
                params[length_of_params].emailadd,
                params[length_of_params].birthday,
                params[length_of_params].gender,
                params[length_of_params].number1,
                params[length_of_params].username,
                params[length_of_params].password
                )
        text_file = open("/home/pi/Desktop/DP_final/ProjectDesign/database/Profile.txt", 'w')
        text_file.write(data_to_save)
        text_file.close()

    def save_profile(self):
        error_msg = self.return_error_message()
        if  error_msg == 0 and self.is_password_same(self.input_password1.get(), self.input_password2.get()) and not self.is_already_registered(retrieve_database_profile_data):
            self.append_profile()
            #self.save_to_data_base() Enable For data Transfer to web database
            self.save_to_text_file(retrieve_database_profile_data)
            self.create_datatemp_for_every_user(self.input_lname.get() + self.input_fname.get() + self.input_Mname.get()+".txt")
            self.create_dataheart_for_every_usr(self.input_lname.get() + self.input_fname.get() + self.input_Mname.get()+".txt")
            self.clear_data()
            print ("success")
            msgbox.showinfo("Success", "Account have been register")
            self.controller.show_frame(StartPage)
            self.controller.hide_frame(RegisterPage)
        else:
            self.display_error(error_msg)

    def cancel_function(self):
        self.clear_data()
        self.controller.show_frame(StartPage)
        self.controller.hide_frame(RegisterPage)



class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.photo = tk.PhotoImage(file = "/home/pi/Desktop/DP_final/ProjectDesign/img/logomain.png")
        self.program_logo = tk.Label(self, image = self.photo)
        self.program_logo.photo = self.photo
        self.program_logo.grid(row = 0, column = 0, rowspan = 20, sticky = "ns")

        self.label = tk.Label(self, text="Login Existing Account", font=LARGE_FONT, height = 2)
        self.label.grid(row = 7, column = 1, sticky = "nsw")

        self.label_login_fname = tk.Label(self, text="First Name: ", font=LARGE_FONT)
        self.label_login_fname.grid(row = 8, column = 1, sticky = "w", padx = 2)
        self.input_login_fname = tk.Entry(self, width = 25, font=LARGE_FONT)
        self.input_login_fname.grid(row = 9, column = 1, columnspan = 2,  sticky = "we", padx = 2)

        self.label_login_lname = tk.Label(self, text="Last Name: ", font=LARGE_FONT)
        self.label_login_lname.grid(row = 10, column = 1, sticky = "w", padx = 2)
        self.input_login_lname = tk.Entry(self, width = 25, font=LARGE_FONT)
        self.input_login_lname.grid(row = 11, column = 1, columnspan = 2,sticky = "we", padx = 2)

        self.label_password_login = tk.Label(self, text="Password: ", font=LARGE_FONT)
        self.label_password_login.grid(row = 12, column = 1, sticky = "w", padx = 2)
        self.input_password_login = tk.Entry(self, width = 25, font=LARGE_FONT, show ="*")
        self.input_password_login.grid(row = 13, column = 1, columnspan = 2, sticky = "we", padx = 2)

        self.login_button = tk.Button(self, text = "Login", font = LARGE_FONT, width = "6", command = lambda: self.login_verify(self.input_login_fname.get(),self.input_login_lname.get(),self.input_password_login.get(), retrieve_database_profile_data))
        self.login_button.grid(row = 14, column = 1, sticky = "e")

        self.login_cancel_button = tk.Button(self, text = "Cancel", font = LARGE_FONT, command = self.cancel_button_function)
        self.login_cancel_button.grid(row = 14, column = 2, sticky = "e", padx = 2)

    def clear_inputs(self):
        self.input_login_fname.delete(0,"end")
        self.input_login_lname.delete(0,"end")
        self.input_password_login.delete(0,"end")

    def login_verify(self,first_name, last_name, password_set,database):
        is_valid = False
        for data in range(len(database)):
            if database[data].lastname == last_name and database[data].firstname == first_name and database[data].password == password_set:
                is_valid = True
                user_profile_that_login.append(database[data].lastname)
                user_profile_that_login.append(database[data].firstname)
                user_profile_that_login.append(database[data].middlename)
                user_profile_that_login.append(database[data].birthday)
                user_profile_that_login.append(database[data].gender)
                user_profile_that_login.append(database[data].number1)
                user_profile_that_login.append(database[data].username)
                self.controller.show_frame(MonitoringPage)
                self.controller.hide_frame(LoginPage)
                self.controller.start_plotting(MonitoringPage)
                self.controller.thread_writer(MonitoringPage)
                self.controller.start_temperature(MonitoringPage)
                self.controller.start_pulse(MonitoringPage)
                self.controller.start_pause_count(MonitoringPage)
                self.controller.instruction_talk(MonitoringPage)
                break
            else:
                is_valid = False

        if not is_valid:
            msgbox.showerror("Login failed!","Please input correct first name, last name and password.")
            self.clear_inputs()

    def cancel_button_function(self):
        self.clear_inputs()
        self.controller.show_frame(StartPage)
        self.controller.hide_frame(LoginPage)


class MonitoringPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.writer = WriteThread()
        self.new_heart_rate_value = ''
        self.heatbeat_time_read = ''
        self.tt = TempThread()
        self.highest_temp_read = ""
        self.temp_time_read = ''
        self.stb = SendToDatabase()
        self.cdt = CounterThread()
        self.wrt = WriteReadingTemp()
        self.wrp = WriteReadingPulse()
        self.tts = TextToSpeech()
        self.job1 = None
        self.job2 = None

        style.use("ggplot")
        self.figs = plt.figure(figsize = (5,3), dpi = 110)
        self.plot_fig = self.figs.add_subplot(111)
        
        self.temp_val = tk.StringVar()
        self.temp_val.set("0 °C")

        self.label = tk.Label(self, text="Health Monitor", font=("century gothic", 20), height = 2)
        self.label.grid(row = 0, column = 0, columnspan = 4 ,sticky = "nsew")

        self.heart_rate_label = tk.Label(self, text="Heart Rate: ", font= LARGE_FONT)
        self.heart_rate_label.grid(row = 1, column = 0, sticky = "n", padx = 2, pady = 2)

        self.heart_rate_value = tk.Label(self, text="0 bpm", font = ("century gothic", 30), fg = "#9000ff")
        self.heart_rate_value.grid(row = 2, column = 0, sticky = "n", padx = 2, pady = 2)

        self.heart_rate_label2 = tk.Label(self, text="Waiting....", font = ("century gothic", 12), fg = "green")
        self.heart_rate_label2.grid(row = 3, column = 0, sticky = "n", padx = 2, pady = 2)

        self.heart_graph = tk.Frame(self, relief = "groove", borderwidth = 2)
        self.heart_graph.grid(row = 1, column = 1, sticky = "nsew", rowspan = 8, columnspan = 3, padx = 8, pady = 2)
         
        self.heart_rate_raw = FigureCanvasTkAgg(self.figs, self.heart_graph)
        self.heart_rate_raw.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = True)

        self.ani = animation.FuncAnimation(self.figs, self.animate_plot, interval = 200)
        self.heart_rate_raw.show()
        self.stop_heart_plot()

        self.temperature_label = tk.Label(self, text="Body Temperature: ", font = LARGE_FONT)
        self.temperature_label.grid(row = 4, column = 0, sticky = "n", padx = 2, pady = 2)

        self.temperature_value = tk.Label(self, text = "0 °C", font = ("century gothic", 30), fg = "#9000ff")
        self.temperature_value.grid(row = 5, column = 0, sticky = "n", padx = 2, pady = 2)

        self.temperature_label2 = tk.Label(self, text="Waiting....", font = ("century gothic", 12), fg="green")
        self.temperature_label2.grid(row = 6, column = 0, sticky = "n", padx = 2, pady = 2)

        #self.temperature_label3 = tk.Label(self, text="highest Reading: -- ", font = ("century gothic", 10))
        #self.temperature_label3.grid(row = 7, column = 0, sticky = "n", padx = 1, pady = 1)

        #self.temperature_label4 = tk.Label(self, text="0 °C", font = ("century gothic", 10))
        #self.temperature_label4.grid(row = 8, column = 0, sticky = "n", padx = 1, pady = 1)
        
        self.button_dummy = tk.Label(self, font = LARGE_FONT, width = 37)
        self.button_dummy.grid(row = 20, column = 0, sticky = "w", columnspan = 2)

        #self.Medicine_reminder_btn = tk.Button(self, text = "Records", font = LARGE_FONT, width = "8")
        #self.Medicine_reminder_btn.grid(row = 20, column = 2, sticky = "e", pady = 3)

        self.back_button = tk.Button(self, text = "Logout", font = LARGE_FONT, width = "8", command = self.logout_verify)
        self.back_button.grid(row = 20, column = 3, sticky = "e", padx = 7, pady = 3)
        
    def refresh_display_pulse(self):
        if self.cdt.is_done:
            self.heatbeat_time_read = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.send_data_to_data_base()
            if int(self.writer.Rate) >= 95 or int(self.writer.Rate) <= 48:
                self.heart_rate_value.configure(text = "0 bpm")
                self.new_heart_rate_value = "0"
                self.heart_rate_label2.configure(text = "no heart rate found", fg = "green")
            elif int(self.writer.Rate) >= 56 and int(self.writer.Rate) <=61:
                self.heart_rate_value.configure(text = str(self.writer.Rate) + " bpm")
                self.new_heart_rate_value = str(self.writer.Rate)
                self.heart_rate_label2.configure(text = "Excellent bpm", fg = "blue")
            elif int(self.writer.Rate) >= 62 and int(self.writer.Rate) <=65:
                self.heart_rate_value.configure(text = str(self.writer.Rate) + " bpm")
                self.new_heart_rate_value = str(self.writer.Rate)
                self.heart_rate_label2.configure(text = "Good bpm", fg = "#56a9ff")
            elif int(self.writer.Rate) >= 66 and int(self.writer.Rate) <=69:
                self.heart_rate_value.configure(text = str(self.writer.Rate) + " bpm")
                self.new_heart_rate_value = str(self.writer.Rate)
                self.heart_rate_label2.configure(text = "Above average bpm", fg = "#ff20ff")
            elif int(self.writer.Rate) >= 70 and int(self.writer.Rate) <=73:
                self.heart_rate_value.configure(text = str(self.writer.Rate) + " bpm")
                self.new_heart_rate_value = str(self.writer.Rate)
                self.heart_rate_label2.configure(text = "Average bpm", fg = "yellow")
            elif int(self.writer.Rate) >= 74 and int(self.writer.Rate) <=81:
                self.heart_rate_value.configure(text = str(self.writer.Rate) + " bpm")
                self.new_heart_rate_value = str(self.writer.Rate)
                self.heart_rate_label2.configure(text = "Below average bpm", fg = "orange")
            elif int(self.writer.Rate) >= 82 and int(self.writer.Rate) <=90:
                self.heart_rate_value.configure(text = str(self.writer.Rate) + " bpm")
                self.new_heart_rate_value = str(self.writer.Rate)
                self.heart_rate_label2.configure(text = "Poor bpm", fg = "red")
            self.wrp.save_thread(user_profile_that_login, self.new_heart_rate_value, self.heatbeat_time_read)
        else:
            pass
        self.job1 = self.after(2000, self.refresh_display_pulse)

    def send_data_to_data_base(self):
        print("sending")
        self.stb.send_thread(user_profile_that_login, self.new_heart_rate_value, self.heatbeat_time_read, self.tt.temperature_reading, self.temp_time_read)

    def start_sensor_pulse_reading(self):
        self.writer.start_thread_write()
        
    def stop_sensor_pulse_reading(self):
        self.writer.stop_thread_write()

    def start_heart_plot(self):
        self.ani.event_source.start()

    def stop_heart_plot(self):
        self.ani.event_source.stop()
            
    def start_reading_temperature(self):
        if self.cdt.is_done:
            self.tt.start_thread()
        else:
            pass
    def tts_talk(self):
        name = user_profile_that_login[1]
        msg = []
        msg_constract = "Hello! {}. How was your day?. hope it was great. Please you may now place the apparatus. kindly place the pulse heart sensor on the ring finger. also place the temperature sensor to the armpit. just relax and I will now start. thank you!".format(name)
        msg.append(msg_constract)
        self.tts.start_talk(msg)
    
    def start_counting(self):
        self.cdt.start_cnt_thread(60)

    def refresh_display_temp(self):
        if self.cdt.is_done:
            self.tt.read_temperature()
            self.temp_time_read = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.temperature_value.configure(text = self.tt.temperature_reading)
            if self.tt.temperature_int_reading <= 34.8 and self.tt.temperature_int_reading >= 25:
                self.temperature_value.configure(text = self.tt.temperature_reading)
                self.temperature_label2.configure(text = "hypothermia ", fg = "#8300ff")
            elif self.tt.temperature_int_reading >= 34.9 and self.tt.temperature_int_reading <= 37.5:
                self.temperature_value.configure(text = self.tt.temperature_reading)
                self.temperature_label2.configure(text = "Normal temperature ", fg = "blue")
            elif self.tt.temperature_int_reading >= 37.6 and self.tt.temperature_int_reading <= 40:
                self.temperature_value.configure(text = self.tt.temperature_reading)
                self.temperature_label2.configure(text = "fever/hyperphprmia", fg = "red")
            elif self.tt.temperature_int_reading >= 40.1:
                self.temperature_value.configure(text = self.tt.temperature_reading)
                self.temperature_label2.configure(text = "Hyperpyrexia", fg = "red")
            #self.temperature_label3.configure(text = "")
            #self.temperature_label4.configure(text = "")
            #print (user_profile_that_login)
            self.wrt.save_thread(user_profile_that_login, self.tt.temperature_reading, self.temp_time_read)
        else:
            pass
        self.job2 = self.after(5000, self.refresh_display_temp)
            
    def animate_plot(self, i):
        pulldata = open("/home/pi/Desktop/DP_final/ProjectDesign/database/rawheartbeat.txt", "r").read()
        datalist = pulldata.split('\n')
        xlist = []
        ylist = []
        for eachline in datalist:
            if len(eachline) > 1:
                x, y = eachline.split(',')
                xlist.append(int(x))
                ylist.append(int(y))

        self.plot_fig.clear()
        self.plot_fig.plot(xlist[-100:],ylist[-100:])
        self.plot_fig.set_ylim([-100, 1100])
        

    def logout_verify(self):
        result = msgbox.askquestion("Logout", "Are you sure?", icon='warning')
        if result == 'yes':
            self.stop_heart_plot()
            self.stop_sensor_pulse_reading()
            self.controller.login_clear(LoginPage)
            self.after_cancel(self.job1)
            self.after_cancel(self.job2)
            self.cdt.is_done = False
            self.controller.show_frame(StartPage)
            self.controller.hide_frame(MonitoringPage)
        else:
            return

    def create_data_page(self):
        pass

class RecordsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller


class ReminderPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.dremider = DeleteReminder()

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("century gothic", 15))

        self.label = tk.Label(self, text="Medicine Reminder", font=("century gothic", 20), height = 2)
        self.label.grid(row = 0, column = 0, columnspan = 6, sticky = "nsew")

        self.reminder_list = ttk.Treeview(self, columns = ('id','Medication','Note', 'Start Date', 'Days', 'Duration'), height = 17)
        self.reminder_list.heading('#1', text = 'id')
        self.reminder_list.heading('#2', text = 'Medication')
        self.reminder_list.heading('#3', text = 'Note')
        self.reminder_list.heading('#4', text = 'Start Date')
        self.reminder_list.heading('#5', text = 'Days')
        self.reminder_list.heading('#6', text = 'Duration')
        self.reminder_list.column('#1', stretch = tk.TRUE, width = 50)
        self.reminder_list.column('#2', stretch = tk.TRUE, width = 150)
        self.reminder_list.column('#3', stretch = tk.TRUE, width = 150)
        self.reminder_list.column('#4', stretch = tk.TRUE, width = 160)
        self.reminder_list.column('#5', stretch = tk.TRUE, width = 160)
        self.reminder_list.column('#6', stretch = tk.TRUE, width = 90)
        self.reminder_list['show'] = 'headings'
        self.reminder_list.grid(row = 1, column = 0, columnspan = 5, sticky = "nsew", padx = 5, pady = "2")

        self.dummy_label = tk.Label(self,  width = 28, borderwidth = 2)
        self.dummy_label.grid(row = 2 , column = 0, sticky = "w")

        self.vsb_list = tk.Scrollbar(self, orient="vertical",command = self.reminder_list.yview, width = 20)
        self.vsb_list.grid(row = 1, column = 5, sticky = "ns", padx = 1)

        self.add_button = tk.Button(self, text = "New", font = LARGE_FONT, width = "8", command = self.add_button_function)
        self.add_button.grid(row = 2, column = 1, sticky = "e", padx = 1)

        self.update_button = tk.Button(self, text = "Edit", font = LARGE_FONT, width = "8", command = self.update_button_function)
        self.update_button.grid(row = 2, column = 2, sticky = "e", padx = 1)

        self.remove_button = tk.Button(self, text = "Delete", font = LARGE_FONT, width = "8", command = self.delete_selected_item)
        self.remove_button.grid(row = 2, column = 3, sticky = "e", padx = 1)

        self.back_button = tk.Button(self, text = "Back", font = LARGE_FONT, width = "8", command = self.back_button_function)
        self.back_button.grid(row = 2, column = 4, sticky = "e", padx = 1)

        self.insert_data_to_table()

    def delete_selected_item(self):
        result = msgbox.askquestion("Delete", "Are you sure?", icon='warning')
        if result == 'yes':
            selected_item = self.reminder_list.selection()[0]
            get_item = self.reminder_list.focus()
            data_get = self.reminder_list.item(get_item, 'values')
            self.dremider.start_thread_delete(data_get[0])
            self.get_from_the_list()
            self.insert_data_to_table()
            msgbox.showinfo("Success", "Reminder have been deleted")
        else:
            return

    def get_from_the_list(self):
        global retrive_reminder_data_file
        retrive_reminder_data_file = retrive_reminder_data()

    def insert_data_to_table(self):
        ### variable  -- retrive_reminder_data_file
        for i in self.reminder_list.get_children():
            self.reminder_list.delete(i)
        
        for data in range(len(retrive_reminder_data_file)):
            days_value = ''
            duration = ''
            if retrive_reminder_data_file[data].everyday != '0':
                days_value = retrive_reminder_data_file[data].everyday
            elif retrive_reminder_data_file[data].interday != '0':
                days_value = retrive_reminder_data_file[data].interday
            elif retrive_reminder_data_file[data].specificday != 'disabled':
                days_value = retrive_reminder_data_file[data].specificday

            if retrive_reminder_data_file[data].continuous != '0':
                duration = 'continous'
            elif retrive_reminder_data_file[data].numday != '0':
                duration = retrive_reminder_data_file[data].numday

            self.reminder_list.insert('', 'end', values = (retrive_reminder_data_file[data].pk,retrive_reminder_data_file[data].medication,retrive_reminder_data_file[data].note, retrive_reminder_data_file[data].start_date, days_value, duration))


    def add_button_function(self):
        self.controller.show_frame(AddReminder)
        self.controller.hide_frame(ReminderPage)

    def update_button_function(self):
        selected_item = self.reminder_list.selection()[0]
        get_item = self.reminder_list.focus()
        data_get = self.reminder_list.item(get_item, 'values')
        print (selected_item)
        print (data_get[0])
        self.controller.show_frame(AddReminder)
        self.controller.hide_frame(ReminderPage)

    def back_button_function(self):
        self.controller.show_frame(StartPage)
        self.controller.hide_frame(ReminderPage)



class AddReminder(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        self.controller = controller

        self.var = tk.IntVar()
        self.var.set(1)

        self.days_select = tk.IntVar()
        self.days_select.set(1)

        self.date_var = tk.StringVar()
        self.date_var.set("")

        self.label = tk.Label(self, text="New Remider", font=("century gothic", 18), height = 2)
        self.label.grid(row = 0, column = 0, columnspan = 6, sticky = "nsew" , padx = 2)

        self.medname_label = tk.Label(self, text = "Medication: ", font = LARGE_FONT)
        self.medname_label.grid(row = 1, column = 0, sticky = "w", padx = 2)
        self.rmdfor_entry = tk.Entry(self, font = LARGE_FONT, width = 18)
        self.rmdfor_entry.grid(row = 1, column = 1, sticky = "w", padx = 2)

        self.note_label = tk.Label(self, text = "Note:     ", font = LARGE_FONT)
        self.note_label.grid(row = 1, column = 2, sticky = "w", padx = 2)
        self.note_entry = tk.Entry(self, font = LARGE_FONT,  width = 18)
        self.note_entry.grid(row = 1, column = 3, sticky = "w",columnspan =3, padx = 2)

        self.sched_label = tk.Label(self, text = "Schedule ", font = ("century gothic", 18), height = 1)
        self.sched_label.grid(row = 2, column = 0, columnspan = 6, sticky = "nsew", padx = 2)

        self.start_label = tk.Label(self, text = "Start Date: ", font = LARGE_FONT)
        self.start_label.grid(row = 3, column = 0, sticky = "w", padx = 2)

        calendar_picker.Datepicker(self, entrywidth = 18, datevar = self.date_var).grid(row = 3, column = 1, sticky = "w", padx = 2)

        self.sched_label = tk.Label(self, text = "Reminder Times: ", font = LARGE_FONT)
        self.sched_label.grid(row = 3, column = 2, sticky = "w", columnspan= 2, padx = 2, pady = 1)

        self.sched_set_button = tk.Button(self, text = "Set", font = LARGE_FONT, command = self.show_set_reminder_times)
        self.sched_set_button.grid(row = 3, column = 4, sticky = "w", padx = 1, pady =1)
    
        self.number_of_day = tk.Spinbox(self, from_ = 1, to = 10000, font = LARGE_FONT, width = 4, state = "readonly")

        self.duration_label = tk.Label(self, text = "Duration: ", font = LARGE_FONT)
        self.duration_label.grid(row = 4, column = 1, sticky = "w", pady = 1)

        self.select_continuous = tk.Radiobutton(self, text = "continuous", variable = self.var, value = 1, font = LARGE_FONT, command = self.disable_spinner)
        self.select_continuous.grid(row = 5, column = 1, sticky = "w" , padx = 1, pady = 1)

        self.select_numday = tk.Radiobutton(self, text = "number of days", variable = self.var, value = 2, font = LARGE_FONT, command = self.enable_spinner)
        self.select_numday.grid(row = 6, column = 1, sticky = "w", padx = 1, pady = 1)

        self.days_label = tk.Label(self, text = "Days: ", font = LARGE_FONT)
        self.days_label.grid(row = 4, column = 0, sticky = "w", padx = 2, pady = 2)

        self.select_everyday = tk.Radiobutton(self, text = "Every day", variable = self.days_select, value = 1, font = LARGE_FONT, command = self.select_cont)
        self.select_everyday.grid(row = 5, column = 0, sticky = "w" , padx = 1, pady = 1)

        self.select_interval = tk.Radiobutton(self, text = "Days interval", variable = self.days_select, value = 2, font = LARGE_FONT, command = self.create_days_interval_spinner)
        self.select_interval.grid(row = 6, column = 0, sticky = "w" , padx = 1, pady = 1)

        self.days_interval = tk.Spinbox(self, from_ = 1, to = 365, font = LARGE_FONT, width = 5, state = "readonly")

        self.select_week = tk.Radiobutton(self, text = "Specific days", variable = self.days_select, value = 3, font = LARGE_FONT, command = self.show_days_of_week)
        self.select_week.grid(row = 7, column = 0, sticky = "w" , padx = 1, pady = 1)

        self.chck_monday = tk.IntVar()
        self.chck_tuesday = tk.IntVar()
        self.chck_wednesday = tk.IntVar()
        self.chck_thursday = tk.IntVar()
        self.chck_friday = tk.IntVar()
        self.chck_saturday = tk.IntVar()
        self.chck_sunday = tk.IntVar()

        self.c1 = tk.Checkbutton(self, text = "Monday", variable = self.chck_monday, onvalue = 1, offvalue = 0, font = LARGE_FONT)
        self.c2 = tk.Checkbutton(self, text = "Tuesday", variable = self.chck_tuesday, onvalue = 1, offvalue = 0, font = LARGE_FONT)
        self.c3 = tk.Checkbutton(self, text = "Wednesday", variable = self.chck_wednesday, onvalue = 1, offvalue = 0, font = LARGE_FONT)
        self.c4 = tk.Checkbutton(self, text = "Thursday", variable = self.chck_thursday, onvalue = 1, offvalue = 0, font = LARGE_FONT)
        self.c5 = tk.Checkbutton(self, text = "Friday", variable = self.chck_friday, onvalue = 1, offvalue = 0, font = LARGE_FONT)
        self.c6 = tk.Checkbutton(self, text = "Saturday", variable = self.chck_saturday, onvalue = 1, offvalue = 0, font = LARGE_FONT)
        self.c7 = tk.Checkbutton(self, text = "Sunday", variable = self.chck_sunday, onvalue = 1, offvalue = 0, font = LARGE_FONT)

        self.dummy_label = tk.Label(self, height = 9)
        self.dummy_label.grid(row = 8 , column = 0, rowspan = 5,columnspan = 2, padx = 1, pady = 1)

        self.sched_details = tk.Text(self, font = ("century gothic", 12), borderwidth = 2, relief = "groove", height = 11, width = 5, state = "disabled", spacing1 = 3)
        self.sched_details.grid(row = 4, column =2, sticky = "ew", rowspan = 8, columnspan = 4, padx = 2, pady = 2)

        self.save_button = tk.Button(self, text = "Save", font = LARGE_FONT, width = "5", command = self.save_button_function)
        self.save_button.grid(row = 20, column = 4, sticky = "e")

        self.cancel_button = tk.Button(self, text = "Cancel", font = LARGE_FONT, width = "5", command = self.cancel_button_function)
        self.cancel_button.grid(row = 20, column = 5, sticky = "e")

    def display_reminder_times_details(self):
        global reminder_times_data_save

        if reminder_times_data_save != {}:
            self.sched_details.configure(state = "normal")
            self.sched_details.delete("1.0", "end")
            self.sched_details.insert( "1.0", '\t             ' + reminder_times_data_save[0] + ' \n')
            if len(reminder_times_data_save) < 8:
                self.sched_details.insert( "2.0", ' Time: \t Take: \n')
            else:
                self.sched_details.insert( "2.0", ' Time: \t Take:        \t Time: \t Take: \n')

            hrs = []
            mins = []
            loop = 0

            for data in range(len(reminder_times_data_save) - 1):
                h , m = reminder_times_data_save[data + 1].split('$')
                hrs.append(h)
                mins.append(m)

            if len(hrs) < 7:
                loop = len(hrs)
            else:
                loop = 6
            
            cnt = len(hrs)

            for save in range(loop):
                
                if cnt > 6:
                    self.sched_details.insert("end", ' ' + hrs[save] + ' \t ' + mins[save] + '           \t ' + hrs[save+6] + ' \t ' + mins[save+6] +'\n')       
                    cnt = cnt - 1
                else:
                    self.sched_details.insert("end", ' ' + hrs[save] + ' \t ' + mins[save] +'\n')
                    

            
            self.sched_details.configure(state = "disabled")
        else:
            return

    def enable_spinner(self):
        self.number_of_day.grid(row = 7, column = 1  , sticky = "n", padx = 1, pady = 1)

    def disable_spinner(self):
        self.number_of_day.configure(state = "normal")
        self.number_of_day.delete(0,"end")
        self.number_of_day.insert(0,1)
        self.number_of_day.configure(state = "readonly")
        self.number_of_day.grid_forget()

    def show_set_reminder_times(self):
        self.controller.show_frame(SetReminderTimes)
        self.controller.hide_frame(AddReminder)

    def create_days_interval_spinner(self):
        self.days_interval.configure(state = "normal")
        self.days_interval.delete(0,"end")
        self.days_interval.insert(0,1)
        self.days_interval.grid(row = 7, column = 0, sticky = "n", pady = 1,)
        self.days_interval.configure(state = "readonly")
        self.select_week.grid_forget()
        self.select_week.grid(row = 8, column = 0, sticky = "w" , padx = 1, pady = 1)
        self.hide_days_of_week()

    def hide_days_interval_spinner(self):
        self.days_interval.delete(0,"end")
        self.days_interval.insert(0,1)
        self.days_interval.grid_forget()
        self.select_week.grid_forget()
        self.select_week.grid(row = 7, column = 0, sticky = "w" , padx = 1, pady = 1)

    def show_days_of_week(self):
        self.c1.grid(row = 8, column = 0, sticky = "w", padx = 1, pady = 1)
        self.c2.grid(row = 9, column = 0, sticky = "w", padx = 1, pady = 1)
        self.c3.grid(row = 10, column = 0, sticky = "w", padx = 1, pady = 1)
        self.c4.grid(row = 11, column = 0, sticky = "w", padx = 1, pady = 1)
        self.c5.grid(row = 8, column = 1, sticky = "w", padx = 1, pady = 1)
        self.c6.grid(row = 9, column = 1, sticky = "w", padx = 1, pady = 1)
        self.c7.grid(row = 10, column = 1, sticky = "w", padx = 1, pady = 1)
        self.hide_days_interval_spinner()
        self.dummy_label.grid_forget()

    def hide_days_of_week(self):
        self.c1.grid_forget()
        self.c2.grid_forget()
        self.c3.grid_forget()
        self.c4.grid_forget()
        self.c5.grid_forget()
        self.c6.grid_forget()
        self.c7.grid_forget()
        self.chck_monday.set(0)
        self.chck_tuesday.set(0)
        self.chck_wednesday.set(0)
        self.chck_thursday.set(0)
        self.chck_friday.set(0)
        self.chck_saturday.set(0)
        self.chck_sunday.set(0)
        self.dummy_label.grid(row = 8 , column = 0, rowspan = 4,columnspan = 2, padx = 1, pady = 1)

    def select_cont(self):
        self.hide_days_of_week()
        self.hide_days_interval_spinner()

    def is_specific_have_day_error(self, params):
        if params == 3:
            if self.chck_monday.get() == 0 and self.chck_tuesday.get() == 0 and self.chck_wednesday.get() == 0 and self.chck_thursday.get() == 0 and self.chck_friday.get() == 0 and self.chck_saturday.get() == 0 and self.chck_sunday.get() == 0:
                msgbox.showerror("Registration failed!","Please select specific days.")
                return False
            else:
                return True
        else:
            return True

    def is_input_not_space(self, user_input):
        if user_input.replace(" ","") is not "":
            return True
        else:
            return False

    def return_error_message(self):
        error_valid = 0
        if not self.is_input_not_space(self.rmdfor_entry.get()):
            error_valid = 1 
        elif not self.is_input_not_space(self.note_entry.get()):
            error_valid = 2           
        elif not self.is_input_not_space(self.date_var.get()):    
            error_valid = 3
        elif not self.is_input_not_space(self.sched_details.get("1.0", "end-1c")):    
            error_valid = 4
        else:
            error_valid = 0
        return error_valid

    def error_msg(self, params):
        if params == 1:
            msgbox.showerror("Registration failed!","Please dont leave the medication blank.")
        elif params == 2:
            msgbox.showerror("Registration failed!","Please dont leave the note blank.")
        elif params == 3:
            msgbox.showerror("Registration failed!","Please dont leave the date blank.")
        elif params == 4:
            msgbox.showerror("Registration failed!","Please set the reminder times")
        elif params == 0:
            print ("No Error")

    def define_days_select(self, params):
        if params == 1:
            return '1'
        else: 
            return '0'
    def interval_days_select(self, params):
        if params == 2:
            return self.days_interval.get()
        else:
            return '0'
    def define_specific_day(self, params):
        days_select = ''
        if params == 3:
            if self.chck_monday.get() == 1:
                days_select = 'M-'
            if self.chck_tuesday.get() == 1:
                days_select = days_select + 'T-'
            if self.chck_wednesday.get() == 1:
                days_select = days_select + 'W-'
            if self.chck_thursday.get() == 1:
                days_select = days_select + 'TH-'
            if self.chck_friday.get() == 1:
                days_select = days_select + 'F-'
            if self.chck_saturday.get() == 1:
                days_select = days_select + 'Sat-'
            if self.chck_sunday.get() == 1:
                days_select = days_select + 'Sun'
            return days_select
        else:
            return 'disabled'

    def define_continous(self, params):
        if params == 1:
            return '1'
        else:
            return '0'

    def define_numday(self, params):
        if params == 2:
            return self.number_of_day.get()
        else:
            return '0'

    def define_reminder_times_data_save(self):
        str_data = ''
        for data in range(len(reminder_times_data_save)):
            str_data = str_data + reminder_times_data_save[data] + '$'
        return str_data

    def clean_self(self):
        self.rmdfor_entry.delete(0,"end")
        self.note_entry.delete(0, "end")
        self.date_var.set("")
        self.var.set(1)
        self.days_select.set(1)
        self.sched_details.configure(state = "normal")
        self.sched_details.delete("1.0", "end")
        self.sched_details.configure(state = "disabled")
        self.chck_monday.set(0)
        self.chck_tuesday.set(0)
        self.chck_wednesday.set(0)
        self.chck_thursday.set(0)
        self.chck_friday.set(0)
        self.chck_saturday.set(0)
        self.chck_sunday.set(0)
        self.disable_spinner()
        self.hide_days_interval_spinner()
        self.hide_days_of_week()

    def append_to_reminder_data(self):
        retrive_reminder_data_file.append(RemindersData(len(retrive_reminder_data_file)+1, self.rmdfor_entry.get(), self.note_entry.get(), self.date_var.get(), self.define_days_select(self.days_select.get()), self.interval_days_select(self.days_select.get()), self.define_specific_day(self.days_select.get()), self.define_continous(self.var.get()), self.define_numday(self.var.get()), self.define_reminder_times_data_save()))

    def save_to_text_database(self, params):
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


    def save_button_function(self):
        error_msg = self.return_error_message()
        if error_msg == 0 and self.is_specific_have_day_error(self.days_select):
            self.append_to_reminder_data()
            self.save_to_text_database(retrive_reminder_data_file)
            msgbox.showinfo("Success", "Reminder have been Save")
            self.clean_self()
            self.controller.refresh_table(ReminderPage)
            self.controller.clean_remidertimes_page(SetReminderTimes)
            self.controller.show_frame(ReminderPage)
            self.controller.hide_frame(AddReminder)
        else:
            self.error_msg(error_msg)
        

    def cancel_button_function(self):
        self.controller.show_frame(ReminderPage)
        self.controller.hide_frame(AddReminder)


class SetReminderTimes(tk.Frame):
    """kapoy"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.reminder_times_label = tk.Label(self, text = "Reminder Times",font=("century gothic", 18), height = 2)
        self.reminder_times_label.grid(row = 0, column = 0, sticky = "nsew", pady = 1, columnspan = 6)

        self.var = tk.IntVar()
        self.var.set(0)

        self.take_time_values_hours = {}
        self.take_time_values_mins = {}
        self.take_dosage_times = {}

        self.take_interval_values_hours = {}
        self.take_interval_values_mins = {}
        self.take_dosage_interval = {}

        self.hours_picker = ("00","01","02","03","04","05","06","07","08","09","10","11","12","12","13","14","15","16","17","18","19","20",
            "21","22","23")
        self.minutes_picker = ("00","01","02","03","04","05","06","07","08","09","10","11","12","12","13","14","15","16","17","18","19","20",
            "21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45",
            "46","47","48","49","50","51","52","53","54","55","56", "57","58","59")
        self.dosage_piker = ("1.00","1.25","1.50","1.75","2.00","2.25","2.50","2.75","3.00","3.25","3.50","3.75","4.00","4.25","4.50","4.75","5.00")

        self.freq = tk.StringVar()
        self.freq.set("Once a day")
        self.inter = tk.StringVar()
        self.inter.set("Every 12 hours")


        self.frequency_select = tk.Radiobutton(self, text = "Frequency", variable = self.var, value = 1, font = LARGE_FONT, width = 10, command = self.show_freq_menu)
        self.frequency_select.grid(row = 1, column = 0, sticky = "w", padx = 3, pady = 2, columnspan = 2)

        self.interval_select = tk.Radiobutton(self, text = "Intervals", variable = self.var, value = 2, font = LARGE_FONT , width = 10, command = self.show_inter_menu)
        self.interval_select.grid(row = 1, column = 3, sticky = "w", padx = 3, pady = 2, columnspan = 2)

        self.frequency_items = ["Once a day", "Twice a day", "3 times a day", "4 times a day", "5 times a day", "6 times a day", "7 times a day", "8 times a day", "9 times a day", "10 times a day", "11 times a day", "12 times a day"]
        self.freq_menu = tk.OptionMenu(self, self.freq, *(self.frequency_items), command = self.create_spin)        
        self.freq_menu.configure(font = ("century gothic", 11), width = 16)

        self.freq_dummy_label = tk.Label(self, font = ("century gothic", 16), width = 15, relief = "groove", borderwidth = 4)
        self.freq_dummy_label.grid(row = 1, column = 2, sticky = "w", padx = 1, pady = 1)

        self.interval_items = ["Every 12 hours", "Every 8 hours", "Every 6 hours", "Every 4 hours", "Every 3 hours", "Every 2 hours"]
        self.inter_menu = tk.OptionMenu(self, self.inter, *(self.interval_items), command = self.create_spin_interval)
        self.inter_menu.configure(font = ("century gothic", 11), width = 16)

        self.inter_dummy_label = tk.Label(self, font = ("century gothic", 16), width = 15, relief = "groove", borderwidth = 4)
        self.inter_dummy_label.grid(row = 1, column = 5, sticky = "w", padx = 1, pady = 1)

        self.time_quan_label = tk.Label(self, text = "Set Time and Quantity", font = LARGE_FONT)
        self.time_quan_label.grid(row = 3, column = 0, sticky = "n", padx = 2, columnspan = 6, pady = 2)

        self.time_set_label = tk.Label(self, text = "Time: ", font = LARGE_FONT)

        self.time_take_label = tk.Label(self, text = "Set Take: ", font = LARGE_FONT)

        self.time_set_label1 = tk.Label(self, text = "Time: ", font = LARGE_FONT)

        self.time_take_label1 = tk.Label(self, text = "Set Take: ", font = LARGE_FONT)

        self.save_button = tk.Button(self, text = "Save", font = LARGE_FONT, width = "5", command = self.save_function)
        self.save_button.grid(row = 20, column = 5, sticky = "w")

        self.cancel_button = tk.Button(self, text = "Cancel", font = LARGE_FONT,command = self.cancel_button_function)
        self.cancel_button.grid(row = 20, column = 5, sticky = "e", padx = 2)

    def show_freq_menu(self):
        self.freq_menu.grid(row = 1, column = 2, sticky = "n", padx = 1, pady = 1)
        self.inter_menu.grid_forget()
        self.freq_dummy_label.grid_forget()
        self.inter_dummy_label.grid(row = 1, column = 5, sticky = "w", padx = 1, pady = 1)
        self.remove_create_interval()
        self.show_set_time_and_quan(1)
        self.freq.set("Once a day")

    def show_inter_menu(self):
        self.inter_menu.grid(row = 1, column = 5, sticky = "n", padx = 1, pady = 1)
        self.freq_menu.grid_forget()
        self.inter_dummy_label.grid_forget()
        self.freq_dummy_label.grid(row = 1, column = 2, sticky = "w", padx = 1, pady = 1)
        self.remove_create_time_and_quan()
        self.show_set_interval(2)
        self.inter.set("Every 12 hours")

    def remove_freq_inter_menu(self):
        self.inter_menu.grid_forget()
        self.freq_dummy_label.grid_forget()
        self.freq_menu.grid_forget()
        self.inter_dummy_label.grid_forget()
        self.inter_dummy_label.grid(row = 1, column = 5, sticky = "w", padx = 1, pady = 1)
        self.freq_dummy_label.grid(row = 1, column = 2, sticky = "w", padx = 1, pady = 1)  

    def show_set_time_and_quan(self,times_set):
        self.remove_create_time_and_quan()
        cnt = 0
        time_interval_every_spinner = 24 / times_set
        time_init = 6
        for create_times in range(times_set):
            if create_times <= 5:

                spin_hours = tk.Spinbox(self, values = self.hours_picker, wrap = True, state = "normal", font = LARGE_FONT, width = 3)
                spin_hours.grid(row = (5+create_times), column = 0, sticky = "e", padx = 1, pady = 6)
                if time_init < 10:
                    spin_hours.delete(0, "end")
                    spin_hours.insert(0, "0" + str(time_init))
                else:
                    spin_hours.delete(0, "end")
                    spin_hours.insert(0, str(time_init))
                self.take_time_values_hours[create_times] = spin_hours

                spin_mins = tk.Spinbox(self, values = self.minutes_picker, wrap = True, state = "readonly", font = LARGE_FONT, width = 3)
                spin_mins.grid(row = (5+create_times), column = 1, sticky = "w", padx = 1, pady = 6)
                self.take_time_values_mins[create_times] = spin_mins

                take_dosage = tk.Spinbox(self, values = self.dosage_piker, wrap = True, state = "readonly", font = LARGE_FONT, width = 4)
                take_dosage.grid(row = (5+create_times), column = 2, sticky = "n", padx = 1, pady = 6)
                spin_hours.configure(state = "readonly")
                self.take_dosage_times[create_times] = take_dosage
            else:
                spin_hours = tk.Spinbox(self, values = self.hours_picker, wrap = True, state = "normal", font = LARGE_FONT, width = 3)
                spin_hours.grid(row = (create_times-1), column = 3, sticky = "e", padx = 1, pady = 6)
                if time_init < 10:
                    spin_hours.delete(0, "end")
                    spin_hours.insert(0, "0" + str(time_init))
                else:
                    spin_hours.delete(0, "end")
                    spin_hours.insert(0, str(time_init))
                self.take_time_values_hours[create_times] = spin_hours

                spin_mins = tk.Spinbox(self, values = self.minutes_picker, wrap = True, state = "readonly", font = LARGE_FONT, width = 3)
                spin_mins.grid(row = (create_times-1), column = 4, sticky = "w", padx = 1, pady = 6)
                self.take_time_values_mins[create_times] = spin_mins

                take_dosage = tk.Spinbox(self, values = self.dosage_piker, wrap = True, state = "readonly", font = LARGE_FONT, width = 4)
                take_dosage.grid(row = (create_times-1), column = 5, sticky = "n", padx = 1, pady = 6)
                spin_hours.configure(state = "readonly")
                self.take_dosage_times[create_times] = take_dosage
            ccnt = cnt + 1
            next_time = time_init + int(time_interval_every_spinner)
            if next_time >= 24:
                time_init = next_time - 24
            else:
                time_init = time_init + int(time_interval_every_spinner)


        if cnt <= 5:
            self.time_set_label.grid(row = 4, column = 0, sticky = "w", padx = 2, pady = 2)
            self.time_take_label.grid(row = 4, column = 2, sticky = "w", padx = 2, pady = 2)
        else:
            self.time_set_label.grid(row = 4, column = 0, sticky = "w", padx = 2, pady = 2)
            self.time_take_label.grid(row = 4, column = 2, sticky = "w", padx = 2, pady = 2)
            self.time_set_label1.grid(row = 4, column = 3, sticky = "w", padx = 2, pady = 2)
            self.time_take_label1.grid(row = 4, column = 5, sticky = "w", padx = 2, pady = 2)

    def remove_create_time_and_quan(self):
        for_remove = self.take_time_values_hours
        for_remove1 = self.take_time_values_mins
        for_remove2 = self.take_dosage_times
        for remove_create in for_remove:
            for_remove[remove_create].grid_forget()
            for_remove1[remove_create].grid_forget()
            for_remove2[remove_create].grid_forget()
            self.time_set_label.grid_forget()
            self.time_take_label.grid_forget()
        self.take_time_values_hours = {}
        self.take_time_values_mins = {}
        self.take_dosage_times = {}

    def show_set_interval(self, times_set):
        self.remove_create_interval()
        cnt = 0
        time_interval_every_spinner = 24 / times_set
        time_init = 6
        for create_interval in range(times_set):
            if create_interval <= 5:
                spin_hours = tk.Spinbox(self, values = self.hours_picker, wrap = True, state = "normal", font = LARGE_FONT, width = 3)
                spin_hours.grid(row = (5+create_interval), column = 0, sticky = "e", padx = 1, pady = 6)
                if time_init < 10:
                    spin_hours.delete(0, "end")
                    spin_hours.insert(0, "0" + str(time_init))
                else:
                    spin_hours.delete(0, "end")
                    spin_hours.insert(0, str(time_init))
                self.take_interval_values_hours[create_interval] = spin_hours

                spin_mins = tk.Spinbox(self, values = self.minutes_picker, wrap = True, state = "readonly", font = LARGE_FONT, width = 3)
                spin_mins.grid(row = (5+create_interval), column = 1, sticky = "w", padx = 1, pady = 6)
                self.take_interval_values_mins[create_interval] = spin_mins

                take_dosage = tk.Spinbox(self, values = self.dosage_piker, wrap = True, state = "readonly", font = LARGE_FONT, width = 4)
                take_dosage.grid(row = (5+create_interval), column = 2, sticky = "n", padx = 1, pady = 6)
                self.take_dosage_interval[create_interval] = take_dosage

                spin_hours.configure(state = "readonly")

            else:
                spin_hours = tk.Spinbox(self, values = self.hours_picker, wrap = True, state = "normal", font = LARGE_FONT, width = 3)
                spin_hours.grid(row = (create_interval-1), column = 3, sticky = "e", padx = 1, pady = 6)
                if time_init < 10:
                    spin_hours.delete(0, "end")
                    spin_hours.insert(0, "0" + str(time_init))
                else:
                    spin_hours.delete(0, "end")
                    spin_hours.insert(0, str(time_init))
                self.take_interval_values_hours[create_interval] = spin_hours

                spin_mins = tk.Spinbox(self, values = self.minutes_picker, wrap = True, state = "readonly", font = LARGE_FONT, width = 3)
                spin_mins.grid(row = (create_interval-1), column = 4, sticky = "w", padx = 1, pady = 6)
                self.take_interval_values_mins[create_interval] = spin_mins

                take_dosage = tk.Spinbox(self, values = self.dosage_piker, wrap = True, state = "readonly", font = LARGE_FONT, width = 4)
                take_dosage.grid(row = (create_interval-1), column = 5, sticky = "n", padx = 1, pady = 6)
                self.take_dosage_interval[create_interval] = take_dosage
 
                spin_hours.configure(state = "readonly")
            
            cnt = cnt + 1
            next_time = time_init + int(time_interval_every_spinner)
            if next_time >= 24:
                time_init = next_time - 24
            else:
                time_init = time_init + int(time_interval_every_spinner)

        if cnt <= 5:
            self.time_set_label.grid(row = 4, column = 0, sticky = "w", padx = 2, pady = 2)
            self.time_take_label.grid(row = 4, column = 2, sticky = "w", padx = 2, pady = 2)
        else:
            self.time_set_label.grid(row = 4, column = 0, sticky = "w", padx = 2, pady = 2)
            self.time_take_label.grid(row = 4, column = 2, sticky = "w", padx = 2, pady = 2)
            self.time_set_label1.grid(row = 4, column = 3, sticky = "w", padx = 2, pady = 2)
            self.time_take_label1.grid(row = 4, column = 5, sticky = "w", padx = 2, pady = 2)

    def remove_create_interval(self):
        for_remove = self.take_interval_values_hours
        for_remove1 = self.take_interval_values_mins
        for_remove2 = self.take_dosage_interval
        for remove_interval in for_remove:
            for_remove[remove_interval].grid_forget()
            for_remove1[remove_interval].grid_forget()
            for_remove2[remove_interval].grid_forget()
            self.time_set_label1.grid_forget()
            self.time_take_label1.grid_forget()
        self.take_interval_values_hours = {}
        self.take_interval_values_mins = {}
        self.take_dosage_interval = {}

    def clean_self(self):
        self.remove_create_time_and_quan()
        self.remove_create_interval()
        self.time_set_label.grid_forget()
        self.time_take_label.grid_forget()
        self.time_set_label1.grid_forget()
        self.time_take_label1.grid_forget()
        self.var.set(0)
        self.freq_menu.grid_forget()
        self.freq_dummy_label.grid_forget()
        self.freq_dummy_label.grid(row = 1, column = 2, sticky = "w", padx = 1, pady = 1)
        self.inter_menu.grid_forget()
        self.inter_dummy_label.grid_forget()
        self.inter_dummy_label.grid(row = 1, column = 5, sticky = "w", padx = 1, pady = 1)

    def create_spin(self, event):
        if self.freq.get() == "Once a day":
            self.show_set_time_and_quan(1)
        elif self.freq.get() == "Twice a day":
            self.show_set_time_and_quan(2)
        elif self.freq.get() == "3 times a day":
            self.show_set_time_and_quan(3)
        elif self.freq.get() == "4 times a day":
            self.show_set_time_and_quan(4)
        elif self.freq.get() == "5 times a day":
            self.show_set_time_and_quan(5)
        elif self.freq.get() == "6 times a day":
            self.show_set_time_and_quan(6)
        elif self.freq.get() == "7 times a day":
            self.show_set_time_and_quan(7)
        elif self.freq.get() == "8 times a day":
            self.show_set_time_and_quan(8)
        elif self.freq.get() == "9 times a day":
            self.show_set_time_and_quan(9)
        elif self.freq.get() == "10 times a day":
            self.show_set_time_and_quan(10)
        elif self.freq.get() == "11 times a day":
            self.show_set_time_and_quan(11)
        elif self.freq.get() == "12 times a day":
            self.show_set_time_and_quan(12)                      

    def create_spin_interval(self, event):
        if self.inter.get() == "Every 12 hours":
            self.show_set_interval(2)
        elif self.inter.get() == "Every 8 hours":
            self.show_set_interval(3)
        elif self.inter.get() == "Every 6 hours":
            self.show_set_interval(4)
        elif self.inter.get() == "Every 4 hours":
            self.show_set_interval(6)
        elif self.inter.get() == "Every 3 hours":
            self.show_set_interval(8)
        elif self.inter.get() == "Every 2 hours":
            self.show_set_interval(12)

    def append_reminder_data_to_global(self, time_hours, time_mins, dosage_take, freq_inter):
        global reminder_times_data_save
        reminder_times_data_save = []
        if freq_inter.get() == 1:
            reminder_times_data_save.append('Frequency:')
        elif freq_inter.get() == 2:
            reminder_times_data_save.append('Interval:')
        for data in range(len(time_hours)):
            reminder_times_data_save.append(time_hours[data].get()+ ":" + time_mins[data].get() + '$' + dosage_take[data].get())

    def save_function(self):
        if self.take_time_values_hours != {}:
            self.append_reminder_data_to_global(self.take_time_values_hours, self.take_time_values_mins, self.take_dosage_times, self.var)
        elif self.take_interval_values_hours != {}:
            self.append_reminder_data_to_global(self.take_interval_values_hours, self.take_interval_values_mins ,self.take_dosage_interval, self.var)
        self.controller.show_frame(AddReminder)
        self.controller.updates_set_reminder(AddReminder)
        self.controller.hide_frame(SetReminderTimes)

    def cancel_button_function(self):
        self.controller.show_frame(AddReminder)
        self.controller.hide_frame(SetReminderTimes)


class SettingPage(tk.Frame):
    def __init__(self, parent, controller):
        #sudo pip3 install pyalsaaudio
        #apt-get install libasound2-dev

        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.m = alsaaudio.Mixer('PCM')
        self.var = tk.StringVar()
        self.var.set(1)
        global volume_selected
        volume_selected = 100

        self.setting_label = tk.Label(self, text = "Settings",font=("century gothic", 18), height = 2)
        self.setting_label.grid(row = 0, column = 0, columnspan = 3, sticky = 'nsew')

        #self.wifi_connect_label = tk.Label(self, text = "Wifi Networks", font = LARGE_FONT)
        #self.wifi_connect_label.grid(row = 1, column = 0, sticky = 'n', padx = 2, pady =2)

        #self.scan_wifi = tk.Button(self, text = "Scan", font = LARGE_FONT, command = self.scan_net)
        #self.scan_wifi.grid(row = 3, column = 0, sticky = 'e', padx = 2, pady = 2)

        #self.net_list = tk.Listbox(self, width = 50, height = 5)
        #self.net_list.grid(row = 2, column = 0, sticky = 'n', padx = 1, pady = 1)

        self.dummy_label = tk.Label(self, font = LARGE_FONT, width = 10)
        self.dummy_label.grid(row = 4, column = 0, sticky = 'nsew',padx = 1, pady = 1)

        self.volume_slider = tk.Scale(self, length = 500, label = 'Volume: ', orient = 'horizontal', fg = 'black', font = LARGE_FONT, command = self.volume_range)
        self.volume_slider.grid(row = 4, column = 1, sticky = 'n', padx = 4, pady = 2)
        self.volume_slider.set(volume_selected)

        self.dummy_label = tk.Label(self, font = LARGE_FONT, width = 10)
        self.dummy_label.grid(row = 4, column = 2, sticky = 'nsew',padx = 1, pady = 1)

        self.language_select = tk.Label(self, text = "Languange:", font = LARGE_FONT, )
        self.language_select.grid(row = 5, column = 1, sticky = 'n', padx = 2, pady = 5)

        self.l1 = tk.Radiobutton(self, text = "English (United States)", variable = self.var, value = 1, font = LARGE_FONT, command = self.select_lang)
        self.l1.grid(row = 6, column = 1, sticky = "w", padx = 2, pady = 2)

        self.l2 = tk.Radiobutton(self, text = "English (United Kingdom)", variable = self.var, value = 2, font = LARGE_FONT, command = self.select_lang)
        self.l2.grid(row = 7, column = 1, sticky = "w", padx = 2, pady = 2)

        self.l3 = tk.Radiobutton(self, text = "English (Australia)", variable = self.var, value = 3, font = LARGE_FONT, command = self.select_lang)
        self.l3.grid(row = 8, column = 1, sticky = "w", padx = 2, pady = 2)

        self.l3 = tk.Radiobutton(self, text = "Tagalog", variable = self.var, value = 3, font = LARGE_FONT, command = self.select_lang)
        self.l3.grid(row = 9, column = 1, sticky = "w", padx = 2, pady = 2)

        self.l3 = tk.Radiobutton(self, text = "Cebuano", variable = self.var, value = 3, font = LARGE_FONT, command = self.select_lang)
        self.l3.grid(row = 10, column = 1, sticky = "w", padx = 2, pady = 2)

        self.save_button = tk.Button(self, text = "Apply", font = LARGE_FONT, command = self.save_function)
        self.save_button.grid(row = 20, column = 1, sticky = "e", padx = 2, pady = 2)
        self.button = tk.Button(self, text = "Cancel", font = LARGE_FONT, command = self.cancel_function)
        self.button.grid(row = 20, column = 2, sticky = "w", padx = 2, pady = 2)

    def scan_net(self):
        output=subprocess.check_output('iwlist wlan0 scan | grep -E "Channel:|ESSID:"', shell=True)
        netze = output.split()
        for i in range(0,(len(netze)/2)-1): 
              string = netze[2*i]+" "+netze[2*i+1]    
              self.net_list.insert(END, string)

    def volume_range(self, v):
        self.m.setvolume(int(v))

    def select_lang(self):
        msgbox.showinfo("Sorry!", "Version not supported!")
        self.var.set(1)

    def save_function(self):
        global volume_selected
        self.controller.show_frame(StartPage)
        self.controller.hide_frame(SettingPage)
        volume_selected = self.volume_slider.get()

    def cancel_function(self):
        self.controller.show_frame(StartPage)
        self.controller.hide_frame(SettingPage)
        self.volume_slider.set(volume_selected)
        

def retrive_profile_data():
    file_retrieve = []
    text_file = open("/home/pi/Desktop/DP_final/ProjectDesign/database/Profile.txt", 'r')
    new_data = []
    text_retrieve = text_file.readlines()
    for length_of_list in range(0,len(text_retrieve)):
        new_data = text_retrieve[length_of_list].split(',')
        file_retrieve.append(Users(new_data[0], new_data[1], new_data[2], new_data[3], new_data[4], new_data[5], new_data[6], new_data[7], new_data[8]))
    text_file.close()
    return file_retrieve

def retrive_reminder_data():
    file_retrieve = []
    text_file = open("/home/pi/Desktop/DP_final/ProjectDesign/database/Reminder.txt", 'r')
    new_data = []
    text_retrieve = text_file.readlines()
    for length_of_list in range(0,len(text_retrieve)):
        new_data = text_retrieve[length_of_list].split(',')
        file_retrieve.append(RemindersData(new_data[0], new_data[1], new_data[2], new_data[3], new_data[4], new_data[5], new_data[6], new_data[7], new_data[8], new_data[9]))
    text_file.close()
    return file_retrieve


#---------------------------------------------------------PROGRAM START ---------------------------------------------#
# Global Variabless init
retrieve_database_profile_data = retrive_profile_data()
retrive_reminder_data_file = retrive_reminder_data()
user_profile_that_login = []
reminder_times_data_save = []
reminder_data_save = []
volume_selected = 0

#start Program
app = ProjectDesignApplication()
app.mainloop()

#---------------------------------------------------------PROGRAM START ---------------------------------------------#




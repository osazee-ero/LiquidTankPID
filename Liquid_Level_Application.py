import tkinter as tk
import PID
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import BSpline, make_interp_spline #  Switched to BSpline
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue

class GUI:
    def __init__(self, master, height, width):
        self.master = master
        self.height=height 
        self.width=width 
        self.mode = False
        self.control_output = 0.0
        self.tolerance=0.95
        self.PGain = 1.2
        self.IGain =1.0
        self.DGain = 0.001 
        self.Pumpstate = False
        self.Tapstate = False
        self.piditerations = 100
        self.PumpPressure = 0
        self.OutletPressure = 0
        self.DesiredHeight=250.0
        self.ActualHeight = 100.0
        self.Area_of_tank = 90000.0
        self.change_in_height = 0.0
        self.density_liquid = 997.0
        self.acceleration_due_to_gravity = 9.8
        self.tank_height = 300.0
        self.height_factor = 1000
        self.transportdelay = 2
        self.timelist = []
        self.actualheightlist = []
        self.desiredheightlist =[]
        self.timeCount = 0;
        self.queue = queue.Queue()
        self.left_Frame = tk.Frame(self.master, height = self.height, width = self.width, bg="red")
        self.topFrameL=tk.Frame(self.left_Frame)
        self.bottomFrameL=tk.Frame(self.left_Frame)
        self.right_Frame = tk.Frame(self.master, height = self.height, width = self.width, bg="blue")
        self.topFrameR=tk.Frame(self.right_Frame)
        self.bottomFrameR = tk.Frame(self.right_Frame)
        self.fig1 =plt.Figure(figsize=(8,5))
        self.interval = 1000
        self.canvas1=FigureCanvasTkAgg(self.fig1, self.topFrameR)
        self.canvas1.get_tk_widget().grid(row=0, column = 0)
        self.ax1 = self.fig1.add_subplot(111)

        
        #plt.ylim((1-0.5, 1+0.5))
        
        self.fig2 =plt.Figure(figsize=(8,4))
        self.canvas2=FigureCanvasTkAgg(self.fig2, self.bottomFrameR)
        self.canvas2.get_tk_widget().grid(row=0, column = 0)
        self.ax2 = self.fig2.add_subplot(111)
        self.PID_Parameters = self.PIDController()
        #self.TimeResponsePlot()
        
        self.drawWidgets()
        self.on_main_thread()
       
       
        
    def changePressure(self,e):
        self.PumpPressure = float(e)
        return self.PumpPressure
        
    def changeHeight(self,e):
        self.DesiredHeight = float(e)
        #if(self.mode == True):
            #self.PID_Parameters = self.PIDController()

        
    def changeOutletPressure(self,e):
        self.OutletPressure = float(e)
        return self.OutletPressure
      
    
    def HeightChanges(self):
        if(self.mode == False):
            if(self.Pumpstate == True):
                self.OutletPressure = 0
                self.PumpPressure = float(self.slider.get())
                self.c.coords(self.water, 400, 450,700,450-self.ActualHeight-self.SimulateHeight())
                self.ActualHeight = self.ActualHeight + self.SimulateHeight()
                self.master.update()
                time.sleep(0.1)
                if(self.ActualHeight > 0 and self.ActualHeight < 300):
                    self.c.itemconfig(self.warningtext, text="")
                if(self.ActualHeight >= 300):
                    self.ActualHeight = 300
                    self.c.itemconfig(self.warningtext, text="Tank filled up", font=('', 14), fill="red")
                elif(self.ActualHeight <= 0):
                    self.ActualHeight = 0
                    self.c.itemconfig(self.warningtext,text="Tank Empty", font=('', 14), fill="red")  
                    self.c.itemconfig(self.Outletpipe, fill="lightblue")
            elif(self.ActualHeight > 0 and self.ActualHeight < 300):
                self.c.itemconfig(self.warningtext, text="")
                
            if(self.Tapstate == True):
                self.PumpPressure = 0
                self.OutletPressure = float(self.slider2.get())
                self.c.coords(self.water, 400, 450,700,450-self.ActualHeight-self.SimulateHeight())
                self.ActualHeight = self.ActualHeight + self.SimulateHeight()
                self.master.update()
                time.sleep(0.1)
                if(self.ActualHeight > 0 and self.ActualHeight < 300):
                    self.c.itemconfig(self.warningtext, text="")
                if(self.ActualHeight >= 300):
                    self.ActualHeight = 300
                    self.c.itemconfig(self.warningtext, text="Tank filled up", font=('', 14), fill="red")
                elif(self.ActualHeight <= 0):
                    self.ActualHeight = 0
                    self.c.itemconfig(self.warningtext,text="Tank Empty", font=('', 14), fill="red")  
                    self.c.itemconfig(self.Outletpipe, fill="lightblue")
            elif(self.ActualHeight > 0 and self.ActualHeight < 300):
                self.c.itemconfig(self.warningtext, text="")
                
        elif(self.mode == True):
            self.DesiredHeight = float(self.slider3.get())
            if(self.ActualHeight >= self.tolerance * self.DesiredHeight and self.ActualHeight <= self.DesiredHeight):
                self.ActualHeight = self.ActualHeight
                self.OFFTapButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
                self.ONTapButton.configure(state="normal", bg="lightblue")
                self.OFFPumpButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
                self.ONPumpButton.configure(state="normal", bg="lightblue")
                self.c.itemconfig(self.Outletpipe, fill="lightblue")
                self.c.itemconfig(self.pumptext, fill="black")
                self.c.itemconfig(self.inletpipe, fill="lightblue")
                self.c.itemconfig(self.inletpipe2, fill="lightblue")
                self.c.itemconfig(self.pump, fill="lightblue")
            elif((self.ActualHeight <  self.DesiredHeight)):
                self.PumpPressure = 500
                self.OFFPumpButton.configure(state="normal", bg="lightblue")
                self.ONPumpButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
                self.c.itemconfig(self.pump, fill="darkblue")
                self.c.itemconfig(self.pumptext, fill="white")
                self.c.itemconfig(self.inletpipe, fill="darkblue")
                self.c.itemconfig(self.inletpipe2, fill="darkblue")
                self.OFFTapButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
                self.ONTapButton.configure(state="normal", bg="lightblue")
                self.c.itemconfig(self.Outletpipe, fill="lightblue")
                
                self.c.coords(self.water, 400, 450,700,450-self.ActualHeight- (0.05 * self.outputlist[-1]))
                self.ActualHeight = self.ActualHeight + (0.05 * self.outputlist[-1])
                self.master.update()
                time.sleep(0.1)
                if(self.ActualHeight > 0 and self.ActualHeight < 300):
                    self.c.itemconfig(self.warningtext, text="")
                if(self.ActualHeight >= 300):
                    self.ActualHeight = 300
                    self.c.itemconfig(self.warningtext, text="Tank filled up", font=('', 14), fill="red")
                elif(self.ActualHeight <= 0):
                    self.ActualHeight = 0
                    self.c.itemconfig(self.warningtext,text="Tank Empty", font=('', 14), fill="red")  
                    self.c.itemconfig(self.Outletpipe, fill="lightblue")
                
            elif((self.ActualHeight > self.DesiredHeight)):
                self.OutletPressure = 500
                self.OFFTapButton.configure(state="normal", bg="lightblue")
                self.ONTapButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
                self.OFFPumpButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
                self.ONPumpButton.configure(state="normal", bg="lightblue")
                self.c.itemconfig(self.Outletpipe, fill="darkblue")
                self.c.itemconfig(self.pumptext, fill="black")
                self.c.itemconfig(self.inletpipe, fill="lightblue")
                self.c.itemconfig(self.inletpipe2, fill="lightblue")
                self.c.itemconfig(self.Outletpipe, fill="darkblue")
                self.c.coords(self.water, 400, 450,700,450-self.ActualHeight- (0.05 * self.outputlist[-1]))
                self.ActualHeight = self.ActualHeight - (0.05 * self.outputlist[-1])
                self.master.update()
                time.sleep(0.1)
                if(self.ActualHeight > 0 and self.ActualHeight < 300):
                    self.c.itemconfig(self.warningtext, text="")
                if(self.ActualHeight >= 300):
                    self.ActualHeight = 300
                    self.c.itemconfig(self.warningtext, text="Tank filled up", font=('', 14), fill="red")
                elif(self.ActualHeight <= 0):
                    self.ActualHeight = 0
                    self.c.itemconfig(self.warningtext,text="Tank Empty", font=('', 14), fill="red")  
                    self.c.itemconfig(self.Outletpipe, fill="lightblue")
                    
            elif(self.ActualHeight > 0 and self.ActualHeight < 300):
                self.c.itemconfig(self.warningtext, text="")
            
                    
                    
            
        self.master.after(500, self.HeightChanges)
                
#    def Outletheightdecrease(self):
#        if(self.Tapstate == True):
#            self.c.coords(self.water, 400, 450,700,450-self.ActualHeight+self.SimulateHeightOutlet())
#            self.ActualHeight = self.ActualHeight - self.SimulateHeightOutlet()
#            self.master.update()
#            time.sleep(0.1)
#            if(self.ActualHeight <= 0):
#                self.ActualHeight = 0
#                self.warningtext = self.c.create_text(400, 50, text="Tank Empty", font=('', 14), fill="red")   
#                self.c.itemconfig(self.Outletpipe, fill="lightblue")
#        self.master.after(500, self.Outletheightdecrease)
        
    def OnPump(self):
        
        self.Pumpstate = True
        self.PumpPressure = float(self.slider.get())
        self.OFFPumpButton.configure(state="normal", bg="lightblue")
        self.ONPumpButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
        self.c.itemconfig(self.pump, fill="darkblue")
        self.c.itemconfig(self.pumptext, fill="white")
        self.c.itemconfig(self.inletpipe, fill="darkblue")
        self.c.itemconfig(self.inletpipe2, fill="darkblue")
        
       
        
    
        
    def OffPump(self):
        self.OFFPumpButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
        self.ONPumpButton.configure(state="normal", bg="lightblue")
        self.c.itemconfig(self.pump, fill="lightblue")
        self.c.itemconfig(self.pumptext, fill="black")
        self.c.itemconfig(self.inletpipe, fill="lightblue")
        self.c.itemconfig(self.inletpipe2, fill="lightblue")
        self.Pumpstate = False
        self.PumpPressure = 0
        self.ActualHeight = self.ActualHeight - 0
        self.c.itemconfig(self.warningtext, text="")
        
    
        
    def OnTap(self):
        self.Tapstate = True
        self.OutletPressure = float(self.slider2.get())
        self.OFFTapButton.configure(state="normal", bg="lightblue")
        self.ONTapButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
        self.c.itemconfig(self.Outletpipe, fill="darkblue")
       
        
  
        
    def OffTap(self):
        self.OFFTapButton.configure(state="active", activebackground="lightgreen", bg="lightgreen")
        self.ONTapButton.configure(state="normal", bg="lightblue")
        self.c.itemconfig(self.Outletpipe, fill="lightblue")
        self.Tapstate = False
        self.OutletPressure = 0
        self.ActualHeight = self.ActualHeight - 0
        self.c.itemconfig(self.warningtext, text="")
        
#    def GetPValue(self):
#        if(self.Pvalue.get() != ''):
#            self.PGain = float(self.Pvalue.get())
#            self.PID_Parameters = self.PIDController()
        
    def GetIValue(self):
        if(self.Ivalue.get() != '' and self.Pvalue.get() != '' and self.Dvalue.get() != ''):
            self.PGain = float(self.Pvalue.get())
            self.IGain = float(self.Ivalue.get())
            self.DGain = float(self.Dvalue.get())
            self.PID_Parameters = self.PIDController()
            
         
    def SimulateHeight(self):
        #self.tankParameters = (self.acceleration_due_to_gravity * self.density_liquid * self.tank_height)/10000
        #self.change_in_height = ((self.PumpPressure - self.tankParameters)/self.Area_of_tank)*self.height_factor
        self.change_in_height = (( self.PumpPressure - self.OutletPressure)/self.Area_of_tank) *self.height_factor
        print(self.change_in_height)
        return self.change_in_height
       
    
#    def SimulateHeightOutlet(self):
#        self.change_in_height2 = (( self.PumpPressure - self.OutletPressure)/self.Area_of_tank) *self.height_factor
#        print(self.change_in_height2)
#        return self.change_in_height2
        
#    def GetDValue(self):
#        if(self.Dvalue.get() != ''):
#            self.DGain = float(self.Dvalue.get())
#            self.PID_Parameters = self.PIDController()
#        
    def PIDController(self):
        pid = PID.PID(self.PGain, self.IGain, self.DGain)  
        pid.SetPoint = 0
        pid.setSampleTime(0.01)  
        feedback = self.ActualHeight
        feedback_list = []
        time_list = [] 
        setpoint_list = [] 
        self.outputlist = []
        for i in range(1, self.piditerations):
            pid.update(feedback)
            self.control_output = pid.output
            if pid.SetPoint > 0:
                feedback += (self.control_output - (1/i))
                self.outputlist.append(feedback)
            if i>self.transportdelay:
                pid.SetPoint = self.DesiredHeight 
            time.sleep(0.01)
        
            feedback_list.append(feedback)
            setpoint_list.append(pid.SetPoint)
            time_list.append(i)
        time_sm = np.array(time_list)
        time_smooth = np.linspace(time_sm.min(), time_sm.max(), 300)
         # Using make_interp_spline to create BSpline
        helper_x3 = make_interp_spline(time_list, feedback_list)
        feedback_smooth = helper_x3(time_smooth)
        return self.control_output, time_smooth, feedback_smooth, time_list, setpoint_list, feedback_list, self.outputlist 

    
    def TimeResponsePlot(self,i):
       
        self.ax1.cla()
        self.ax1.grid(True)
        self.ax1.set_xlabel('time (s)')
        self.ax1.set_ylabel('PID (PV)')
        self.ax1.set_title('PID Time Response')
        line1, = self.ax1.plot(self.PID_Parameters[1], self.PID_Parameters[2], label="Actual Response")
        line1, = self.ax1.plot(self.PID_Parameters[3], self.PID_Parameters[4], label = "Desired Response")
        self.ax1.set_xlim((0, self.piditerations))
        self.ax1.set_ylim((min(self.PID_Parameters[5])-5, max(self.PID_Parameters[5])+5))
        self.ax1.legend()
        
    def HeightPlotOvertime(self,i):
        self.ax2.cla()
        self.ax2.set_xlabel('time (s)')
        self.ax2.set_ylabel('Liquid Height')
        self.ax2.set_title('Height Response')
        self.ax2.grid(True)
        self.actualheightlist.append(float(self.ActualHeight))
        self.desiredheightlist.append(float(self.DesiredHeight))
        self.timelist.append(float(self.timeCount))
        self.ax2.set_ylim((0, 400.0))
        self.ax2.plot(self.timelist, self.actualheightlist,label = "Actual Height")
        self.ax2.plot(self.timelist, self.desiredheightlist, label = "desired Height")
        self.ax2.legend()
        self.timeCount = self.timeCount + 1
        time.sleep(0.01)
        
    def on_main_thread(self):
        self.queue.put(FuncAnimation(self.fig2, self.HeightPlotOvertime, self.interval))
        self.queue.put(FuncAnimation(self.fig1, self.TimeResponsePlot, self.interval))
        
    def check_queue(self):
        while True:
            try:
                task = self.queue.get(block=False)
            except queue.Empty:
                break
            else:
                pass
                #self.master.after_idle(task)
        self.master.after(100, self.check_queue)
            
    def restart(self):
        print("restart")
        
    def ManualMode(self):
        self.mode = False
        self.c.itemconfigure(self.ModeText, text="MANUAL MODE")
        
    def AutomaticMode(self):
        self.mode = True
        self.c.itemconfigure(self.ModeText, text="AUTOMATIC MODE")
     
        
    def drawWidgets(self):
        self.c = tk.Canvas(self.topFrameL, width=self.width*1.4, height=self.height, bg="white")
        self.c.grid(row=0, column=0, sticky="nesw")
        self.c.grid_columnconfigure(0, weight=1)
        self.c.grid_rowconfigure(0, weight=1)
        self.topFrameL.pack(expand = True, fill="both")
        
        self.tank = self.c.create_rectangle(400, 150, 700, 450, fill="lightblue")
        self.water = self.c.create_rectangle(400, 450, 700, 450-self.ActualHeight, fill="darkblue")
        self.warningtext = self.c.create_text(400, 50, text="", font=('', 14), fill="red")
        
        self.ModeText = self.c.create_text(800, 50, text="MANUAL MODE", font=('', 20), fill="black")
        
        self.dimensionsV = self.c.create_line(390, 450, 390, 150)
        self.dimensionsH1 = self.c.create_line(385, 150, 395, 150)
        self.H1text = self.c.create_text(358, 150, text="300mm", font=('', 10), fill="black")
        self.dimensionsH2 = self.c.create_line(385, 150, 395, 150)
        self.c.move(self.dimensionsH2, 0,50)
        self.H2text = self.c.create_text(358, 200, text="250mm", font=('', 10), fill="black")
        self.dimensionsH3 = self.c.create_line(385, 150, 395, 150)
        self.c.move(self.dimensionsH3, 0,100)
        self.H3text = self.c.create_text(358, 250, text="200mm", font=('', 10), fill="black")
        self.dimensionsH4 = self.c.create_line(385, 150, 395, 150)
        self.c.move(self.dimensionsH4, 0,150)
        self.H4text = self.c.create_text(358, 300, text="150mm", font=('', 10), fill="black")
        self.dimensionsH5 = self.c.create_line(385, 150, 395, 150)
        self.c.move(self.dimensionsH5, 0,200)
        self.H5text = self.c.create_text(358, 350, text="100mm", font=('', 10), fill="black")
        self.dimensionsH6 = self.c.create_line(385, 150, 395, 150)
        self.c.move(self.dimensionsH6, 0,250)
        self.H6text = self.c.create_text(358, 400, text="50mm", font=('', 10), fill="black")
        self.dimensionsH7 = self.c.create_line(385, 150, 395, 150)
        self.c.move(self.dimensionsH7, 0,300)
        self.H7text = self.c.create_text(358, 450, text="0mm", font=('', 10), fill="black")
        
        

        
        self.inletpipe = self.c.create_rectangle(300, 120, 550, 80, fill = "lightblue")
        self.inletpipe2 = self.c.create_rectangle(500, 140, 550, 80, fill = "lightblue")
        
        self.Outletpipe = self.c.create_rectangle(700, 450, 800, 420, fill = "lightblue")
        #self.OutletpipeWater = self.c.create_rectangle(700, 450, 800, 420, fill = "lightblue")
        self.outletpumptext = self.c.create_text(800, 400, text="Outlet tap", font=('', 14), fill="black")
        
        self.ONPumpButton = tk.Button(self.topFrameL, text = "ON PUMP", command = self.OnPump, anchor = "w", bg="lightblue")
        self.ONPumpButton.configure(width = 10, relief = "flat", justify ="center",font=('', 12))
        self.buttonwindow = self.c.create_window(60, 200, anchor="nw", window=self.ONPumpButton)
        
        self.OFFPumpButton = tk.Button(self.topFrameL, text = "OFF PUMP", command = self.OffPump, anchor = "w")
        self.OFFPumpButton.configure(width = 10, relief = "flat", justify ="center",font=('', 12), state="active", activebackground="lightgreen")
        self.offbuttonwindow = self.c.create_window(180, 200, anchor="nw", window=self.OFFPumpButton)
        
        self.ONTapButton = tk.Button(self.topFrameL, text = "ON TAP", command = self.OnTap, anchor = "w", bg="lightblue")
        self.ONTapButton.configure(width = 10, relief = "flat", justify ="center",font=('', 12))
        self.ontapbuttonwindow = self.c.create_window(750, 200, anchor="nw", window=self.ONTapButton)
        
        self.OFFTapButton = tk.Button(self.topFrameL, text = "OFF TAP", command = self.OffTap, anchor = "w")
        self.OFFTapButton.configure(width = 10, relief = "flat", justify ="center",font=('', 12),state="active", activebackground="lightgreen")
        self.offtapbuttonwindow = self.c.create_window(900, 200, anchor="nw", window=self.OFFTapButton)
        
        self.pump = self.c.create_oval(0,0,100,100,fill = "lightblue")
        self.c.move(self.pump, 250, 60)
        self.pumptext = self.c.create_text(300, 110, text="Pump", font=('', 14), fill="black")
        
        tk.Label(self.bottomFrameL, text='PID PARAMETERS', font=('', 16), padx=5).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.bottomFrameL, text='SYSTEM SETUP', font=('', 16), padx=5).grid(row=1, column=4, columnspan = 3, padx=5, pady=5 )
        self.slider =tk.Scale(self.bottomFrameL, label = "PumpPressure",font=('', 14), from_=0, to =500, command=self.changePressure,orient='horizontal', width=40)
        self.slider.set(self.PumpPressure)
        self.slider.grid(row = 2, column=4, columnspan =4, ipadx=70, padx=30)
        
        self.slider2 =tk.Scale(self.bottomFrameL, label = "OutletPressure",font=('', 14), from_=0, to =500, command=self.changeOutletPressure,orient='horizontal', width=40)
        self.slider2.set(self.OutletPressure)
        self.slider2.grid(row = 3, column=4, columnspan =4, ipadx=70, padx=30)
        
        self.slider3 =tk.Scale(self.bottomFrameL, label = "DesiredHeight",font=('', 14), from_=50, to =300, command=self.changeHeight,orient='horizontal', width=40)
        self.slider3.set(self.DesiredHeight)
        self.slider3.grid(row = 4, column=4,columnspan =4, ipadx=70, padx = 30)
        
        
        
        tk.Label(self.bottomFrameL, text='P Value', font=('', 16)).grid(row=2, column=0, sticky="W", padx=7, pady=7, ipadx=7, ipady=7)
        self.Pvalue = tk.Entry(self.bottomFrameL, text='', font=('', 16), width=23, justify="center")
        self.Pvalue.insert(0, str(self.PGain))
        self.Pvalue.grid(row=2, column=1, sticky="W", padx =7, pady=12, ipadx=7, ipady=12)
        #self.liveplotB = tk.Button(self.bottomFrameL, text='LivePlot', font=('', 16), bg="green",activebackground = "#33B5E5",relief = "flat", command=self.GetPValue)
                            
        #self.Pbutton.configure(activebackground = "#33B5E5", relief = "flat")
                               
        tk.Label(self.bottomFrameL, text='I Value', font=('', 16)).grid(row=3, column=0, sticky="W", padx=7, pady=7, ipadx=7, ipady=7)
        self.Ivalue= tk.Entry(self.bottomFrameL, text='', font=('', 16), width=23, justify="center")
        self.Ivalue.insert(0, str(self.IGain))
        self.Ivalue.grid(row=3, column=1, sticky="W", padx =7, pady=12, ipadx=7, ipady=12)
        tk.Button(self.bottomFrameL, text='Enter Values', font=('', 16), bg="green",activebackground = "#33B5E5",relief = "flat", command=self.GetIValue).grid(row=3, column=2, sticky="W", padx=5, pady=7, ipadx=15, ipady=5)
        
        tk.Label(self.bottomFrameL, text='D Value', font=('', 16)).grid(row=4, column=0, sticky="W", padx=7, pady=7, ipadx=7, ipady=7)
        self.Dvalue = tk.Entry(self.bottomFrameL, text='', font=('', 16), width=23, justify="center")
        self.Dvalue.insert(0,str(self.DGain))
        self.Dvalue.grid(row=4, column=1, sticky="W", padx =7, pady=12, ipadx=7, ipady=12)
        #tk.Button(self.bottomFrameL, text='Enter', font=('', 16), bg="green",activebackground = "#33B5E5",relief = "flat", command=self.GetDValue).grid(row=4, column=2, sticky="W", padx=5, pady=7, ipadx=15, ipady=5)
        
        self.bottomFrameL.pack(fill="both",expand=True)
        
        
        self.topFrameR.pack(expand = True, fill="both")
        self.bottomFrameR.pack(expand = True, fill="both")
        
        self.left_Frame.pack(fill="both",expand=True, side="left")
        
        
        self.right_Frame.pack(fill="both",expand=True, side="right")  
        #self.on_main_thread()
        
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)
        filemenu=tk.Menu(menu)
        menu.add_cascade(label='File..', menu=filemenu)
        filemenu.add_command(label='Restart', command = self.restart)
        filemenu.add_command(label='Exit', command=self.master.destroy)
        colormenu=tk.Menu(menu)
        menu.add_cascade(label='Controller Mode', menu=colormenu)
        colormenu.add_command(label='Manual', command=self.ManualMode)
        colormenu.add_command(label='Automatic', command=self.AutomaticMode)
     

root = tk.Tk()
gui = GUI(root,500,800)
root.title('LiquidLevelControl Application')
#root.resizable(900,900)
   #ani1 = FuncAnimation(gui.fig1, gui.TimeResponsePlot, gui.interval)
   #ani2 = FuncAnimation(gui.fig2, gui.animate_thread, gui.interval)
root.after(100, gui.check_queue)
root.after(100, gui.HeightChanges)
root.mainloop()


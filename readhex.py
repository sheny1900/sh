import threading, time, serial
import string

class SerThread:
    def __init__(self, Port=0):
        self.my_serial = serial.Serial()
        self.my_serial.port=Port
        self.my_serial.baudrate = 921600
        self.my_serial.timeout = 1        
        self.alive = False
        self.waitEnd = None
        fname=time.strftime("%Y%m%d_%H%M%S.pcm")
        self.rfname='r'+fname
        self.sfname='s'+fname
        self.thread_read= None
        self.thread_send=None      
             
 
    def waiting(self):
        if not self.waitEnd is None:
            self.waitEnd.wait()
 
    def start(self):
        self.rfile=open(self.rfname,'wb')
        self.my_serial.open()
             
        if self.my_serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            
            self.thread_read = threading.Thread(target=self.Reader)
            self.thread_read.setDaemon(True)
            
            self.thread_send=threading.Thread(target=self.Sender)
            self.thread_send.setDaemon(True)
            
            self.thread_read.start()
            self.thread_send.start()
            return True
        else:
            return False
 
   
    def Reader(self):
        while self.alive:
            try:
                n=self.my_serial.inWaiting()
                data=''
                if n:
                    data= self.my_serial.read(n)
                    print ('recv data:'+ str(n))
                    self.rfile.write(data)
            except Exception as ex:
                print (ex)
               
 
        self.waitEnd.set()
        self.alive = False
    
    def Sender(self):
        while self.alive:
            try:
                snddata=input("input data:\n")
                if snddata == 'q':
                    self.stop()

            except Exception as ex:
                print (ex)
        
        self.waitEnd.set()
        self.alive = False                   
                
        
 
    def stop(self):
        self.alive = False
        #self.thread_read.join()
        #self.thread_send.join()
        if self.my_serial.isOpen():
            self.my_serial.close()
        self.rfile.close()

 
if __name__ == '__main__':    
    
    ser = SerThread('com3')
    try:
        if ser.start():
            ser.waiting()
            ser.stop()
        else:
            pass;            
    except Exception as ex:
        print (ex)
 
    if ser.alive:
        ser.stop()
 
    print ('End OK .');
    del ser; 

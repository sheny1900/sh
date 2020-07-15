import threading, time, serial
import string
import os
import sys
import time
import math

class SerThread:
    def __init__(self, Port=0):
        self.my_serial = serial.Serial()
        self.my_serial.port=Port
        self.my_serial.baudrate = 115200
        self.my_serial.timeout = None
        self.my_serial.stopbits = 1
        self.my_serial.parity = 'N'
        self.my_serial.bytesize = 8
        self.my_serial.timeout = 0.02
        #self.my_serial.set_buffer_size(409600, 409600)
        self.alive = False
        self.waitEnd = None
        self.settingFileName="2_bootloader_setting.hex"
        self.imageFileName="nrf52810_xxaa.bin"
        self.imageFileReceiveName= "image.rev.bin"
        self.thread_read= None
        self.thread_send=None
 
    def waiting(self):
        if not self.waitEnd is None:
            self.waitEnd.wait()
 
    def start(self):
        self.imageFileSize=os.path.getsize(self.imageFileName)
        print('Image File Size:'+ str(self.imageFileSize)+'\r\n')
        self.imageFile=open(self.imageFileName,'rb')
        self.my_serial.open()
        self.imageFileReceive = open(self.imageFileReceiveName, 'wb')
             
        if self.my_serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            
            #self.thread_read = threading.Thread(target=self.Reader)
            #self.thread_read.setDaemon(True)
            
            self.thread_send=threading.Thread(target=self.Sender)
            self.thread_send.setDaemon(True)

            #self.thread_commander = threading.Thread(target=self.Commander)
            #self.thread_commander.setDaemon(True)
            
            #self.thread_read.start()
            self.thread_send.start()
            #self.thread_commander.start()
            return True
        else:
            return False

    def WaitingSerialResponse(self):
        self.my_serial.flush()
        read_data = b''
        while read_data == b'':
            read_data = self.my_serial.read()
            if( read_data == b'\xEE' ):
                print("ERROR")
                self.stop()
        #print("Response:" + read_data.__str__())

    def SendPKGCMD(self, pkgCMD):
        print("Send command: " + int(pkgCMD).to_bytes(2, "little").__str__())
        self.my_serial.write(int(pkgCMD).to_bytes(2, "little"))
        self.WaitingSerialResponse()
        print("Got command: " + int(pkgCMD).to_bytes(2, "little").__str__() + " response.")

    def GetCheckSum(self, datas):
        checksum = 0;
        for d in datas:
            checksum += d;
        print("Checksum = "+str(checksum))
        return checksum

    def Sender(self):
        while self.alive:
            try:
                #print(self.imageFileSize.to_bytes(4, "big"))
                print("Sending the pkg addr...")
                self.SendPKGCMD(2) #0x0002
                pkgAddr = 143360 #0x23000
                self.my_serial.write(pkgAddr.to_bytes(4, "little"))
                self.WaitingSerialResponse()

                print("Sending the size...")
                self.SendPKGCMD(3) #0x0003
                self.my_serial.write(self.imageFileSize.to_bytes(4, "little"))
                pkgErasePage = 7
                self.my_serial.write(pkgErasePage.to_bytes(4, "little"))
                self.WaitingSerialResponse()

                print("Erasing the flash...")
                self.SendPKGCMD(4) #0x0004
                erase_confirm = 56797
                self.my_serial.write(erase_confirm.to_bytes(4, "little"))
                self.WaitingSerialResponse() #Waiting for success

                print("Sending the data...")
                slip_size = 128
                pkgDatas = self.imageFile.read()
                for index in range(0, (self.imageFileSize//slip_size)):
                    self.SendPKGCMD(5) #0x0005
                    pkgItem = pkgDatas[index*slip_size:(index+1)*slip_size]
                    self.my_serial.write(self.GetCheckSum(pkgItem).to_bytes(4, "little"))
                    self.my_serial.write(slip_size.to_bytes(4, "little"))
                    self.my_serial.write(pkgItem)
                    self.WaitingSerialResponse()

                if self.imageFileSize%slip_size > 0:
                    self.SendPKGCMD(5)  # 0x0005
                    pkgItem = pkgDatas[self.imageFileSize-(self.imageFileSize%slip_size):]
                    self.my_serial.write(self.GetCheckSum(pkgItem).to_bytes(4, "little"))
                    self.my_serial.write((self.imageFileSize%slip_size).to_bytes(4, "little"))
                    self.my_serial.write(pkgItem)
                    self.WaitingSerialResponse()

                print("Write finished.")
                self.SendPKGCMD(6) #0x0006
                flash_confirm = 52428
                self.my_serial.write(flash_confirm.to_bytes(4, "little"))
                self.WaitingSerialResponse()
                print("Flash finished.")
                #time.sleep(240)
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
        self.imageFile.close()
        self.imageFileReceive.close()
 
if __name__ == '__main__':    
    
    ser = SerThread('com6')
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

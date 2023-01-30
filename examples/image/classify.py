#!/usr/bin/env python

import device_patches       # Device specific patches for Jetson Nano (needs to be before importing cv2)

import cv2
import os
import sys, getopt
import signal
import time
sys.path.append("/opt/linux-sdk-python/edge_impulse_linux")
#from edge_impulse_linux.image import ImageImpulseRunner
from image import ImageImpulseRunner
###
from threading import Timer
import time
import json
import csv
outputPath = './'
n = 0
sec_list = [0]
###
runner = None
# if you don't want to see a camera preview, set this to False
show_camera = True
if (sys.platform == 'linux' and not os.environ.get('DISPLAY')):
    show_camera = False
###
#def imwrite():
#    i =  1
                            
#    img_pad = "./1/" + str(time.strftime('%H:%M:%S',time.localtime()))+".jpg"
#    cv2.imwrite(img_pad, img)


###
def now():
    return round(time.time() * 1000)

def get_webcams():
    port_ids = []
    for port in range(5):
        print("Looking for a camera in port %s:" %port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName =camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s " %(backendName,h,w, port))
                port_ids.append(port)
            camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            if len(args)>= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if len(port_ids) == 0:
                    raise Exception('Cannot find any webcams')
                if len(args)<= 1 and len(port_ids)> 1:
                    raise Exception("Multiple cameras found. Add the camera port ID as a second argument to use to this script")
                videoCaptureDeviceId = int(port_ids[0])

            camera = cv2.VideoCapture(videoCaptureDeviceId)
            #ret = camera.read()[0]
            ###
            
            ret,original_image = camera.read()#[0]
            #ret1,frame = cv2.VideoCapture.read()
            
            print ('frame11_2',original_image.shape)
            ###
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print('w',w)
                print("Camera %s (%s x %s) in port %s selected." %(backendName,h,w, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            next_frame = 0 # limit to ~10 fps here
            i = 0
            #camera1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            #camera1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            #camera1 = camera
            #print ('img.shape2', img.shape)            
            for res, img in runner.classifier(videoCaptureDeviceId):
               ####
                #ret2, frame11_2 = camera.read()

                #print (runner.classifier.())
                #seconds = time.localtime(time.time())#轉換整秒數
                seconds = time.mktime(time.gmtime())#轉換整秒數
                print ("seconds",seconds)
                seconds_threshold = seconds#.tm_sec

                #sec_list.append(seconds.tm_sec)
                


                #if (seconds.tm_sec % 5) == 0: #被5整除就拍
                    #i = i + 1
                    #img_pad = "./1/" + str(i)+".jpg"
                    #cv2.imwrite(img_pad, img)
                #else:
                 #   print
                ####
                if (next_frame > now()):
                    time.sleep((next_frame - now()) / 1000)

                # print('classification runner response', res)
                data_list = []
                #n = 1
                print ("test")
                        #seconds = time.localtime(time.time())#轉換整秒數
 
                #print ("nnnn",n)

                sec_list1 = int(max(sec_list))
                print ("seconds.tm_sec",seconds)#.tm_sec)
                print ("sec_list1",sec_list1)








                #
                if "classification" in res["result"].keys():
                    print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
                    for label in labels:
                        score = res['result']['classification'][label]
                        #print('%s: %.2f\t' % (label, score), end='')#
                        score1 = str(score)
                        #print('%s: %.2f\t' % ('"'+label+'"', score), end='')
                        #data =  ('%s: %.2f' % (label, score))
                        score2 =int (float('%.2f' % (score))*100)
                        #score2 =(int('%.f' % (score))*100)
                        #data_json = [ {label:score2} ]
                        #data_json = json.dumps(data,indent=2, sort_keys=True)
                        #print (label)no
                        data_list.append((label,score2))
                        #print (score2)
                                                                    
                    print('', flush=True)
                    #print(data_list)
                    data_list_1 = sorted(data_list,key=lambda x: x[1], reverse=True)
                    print(data_list_1)
                    data_list_2 = data_list_1[0]
                    data_str = ' '.join(map(str,data_list_2))
                elif "bounding_boxes" in res["result"].keys():
                    print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                    for bb in res["result"]["bounding_boxes"]:
                        print('\t%s (%.2f): x1=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                        print('%s: %.2f\t' % ('"'+label+'"', score), end='')
                        img = cv2.rectangle(img, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (0, 255, 0), 1)                
    
                #if (seconds.tm_sec % 5) == 0 and (seconds.tm_sec > sec_list1) : #被5整除就拍
                if (seconds % 5) == 0 and (seconds > sec_list1) : #被5整除就拍
                            #seconds.tm_sec = seconds.tm_sec + 1
                            #if n == 1:
                    ###
                    local_time = time.localtime()
                    timeString = time.strftime("%Y_%m_%d_%H_%M_", local_time)
                    ###
                    i = i + 1

                    print ('img.shape2', original_image.shape)
                    #original_img_pad = "./Original_image/" + str(timeString) + str(i)+".jpg"
                    #cv2.imwrite(original_img_pad, original_image)
                            
                    img_pad = "/opt/linux-sdk-python/examples/image/Inference_results/" + str(timeString) + str(i)+".jpg"
                    cv2.imwrite(img_pad, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                    timestamp = str(timeString) + str(i)
                    data_list_1.insert(0, timestamp)

                    with open('/opt/linux-sdk-python/examples/image/Inference_results/Inference_results.csv', 'a') as file:
                        #writer = csv.writer(file,delimiter=';')
                        writer = csv.writer(file)
                        #for item in str(data_list_1):
                         #   writer.writerows(item)
                        writer.writerow((data_list_1))


                    seconds_1 = int(seconds_threshold) + 1
                    sec_list.append(seconds_1)


                    #n =  1
                    #print ("ififififn",n)
                #else:
                #    print 



                print (data_str)
                cv2.putText(img, (data_str+'%'), (5, 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 255), 1)##
                if (show_camera):
                    cv2.imshow('edgeimpulse', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                    if cv2.waitKey(1) == ord('q'):
                        break

                next_frame = now() + 100
        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
   main(sys.argv[1:])

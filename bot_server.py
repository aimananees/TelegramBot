import telepot
from pprint import pprint
import time
import requests
import json
from firebase import firebase

bot = telepot.Bot('TOKEN')

needs_dict = {}
haves_dict = {}
need_subject_dict={}
provide_subject_dict={}

def handle(msg):
    #chat_id is an unique identifier for the bot user
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':

        pprint(msg)
        inp = msg['text']
        #Eg inp => I need 2 eggs
        #Eg inp => I have 3 eggs
        #Eg inp => I want to study maths
        #Eg inp => I can teach 10 maths
        #Eg inp => Hello
        #Eg inp => Hi
        #Getting the name:
        first_name=str(msg['from']['first_name'])
        last_name=str(msg['from']['last_name'])
        name = first_name+" "+last_name
        print name
        inp = inp.split()
        if len(inp) == 4:
            request_type = inp[1]
            item = inp[3]
            qty = int(inp[2])

            #Storing needs and haves in dictionaries
            ############################This is used for 'needs'###############################
            if request_type == 'need':
                if item not in needs_dict:
                    needs_dict[item] = {}
                needs_dict[item][chat_id] = needs_dict[item].get(chat_id, 0) + qty
                needs_dict[item]['name'] = name

                #Getting the coordinates
                send_url = 'http://freegeoip.net/json'
                r = requests.get(send_url)
                j = json.loads(r.text)
                lat = j['latitude']
                lon = j['longitude']

                needs_dict[item]['latitude'] = lat
                needs_dict[item]['longitude'] = lon

                msg_time=time.time()
                needs_dict[item]['time']=msg_time
                needs_dict[item]['need']='true'

                
                print msg_time
                print lat,"-----",lon
                print str(chat_id) + " Needs " + str(item) + " registered"

                firebase1 = firebase.FirebaseApplication('https://cmu-hackathon-python.firebaseio.com/')
                result=firebase1.post('/need_record',{
                    "chat_id":chat_id,
                    "name":name,
                    "latitude":lat,
                    "longitude":lon,
                    "time":msg_time,
                    "qty":needs_dict[item][chat_id],
                    "item":item,
                    "need":"true"
                    })

                if item in haves_dict:
                    receivers = haves_dict[item].keys()
                    receivers.sort()
                    receivers1=receivers[0]
                    receivers2=receivers[3]
                    name=haves_dict[item][receivers2]
                    if(haves_dict[item][receivers1] >= needs_dict[item][chat_id]):
                        count=(haves_dict[item][receivers1] - int(needs_dict[item][chat_id]))
                        if(count>0):
                            haves_dict[item][receivers1]=count
                            bot.sendMessage(chat_id,"Hey, "+str(name)+" has "+item)
                            del needs_dict[item]
                        else:
                            receivers = haves_dict[item].keys()
                            bot.sendMessage(chat_id,"Hey, "+str(name)+" has "+item)
                            del haves_dict[item]
                            del needs_dict[item]
                else:
                    bot.sendMessage(chat_id,"You will be notified once someone volunteers for providing "+str(item))
                print "################################"
                print "Needs Dict: ",needs_dict
                print "Haves Dict: ",haves_dict
                

            ######################This is used for 'have'####################################
            if request_type == 'have':
                haves_dict[item] = {}
                haves_dict[item][chat_id] = haves_dict[item].get(chat_id, 0) + qty
                haves_dict[item]['name'] =name

                #Getting the coordinates
                send_url = 'http://freegeoip.net/json'
                r = requests.get(send_url)
                j = json.loads(r.text)
                lat = j['latitude']
                lon = j['longitude']

                haves_dict[item]['latitude'] =lat
                haves_dict[item]['longitude'] =lon

                msg_time=time.time()
                haves_dict[item]['time'] = msg_time
                haves_dict[item]['need'] = 'false'
                print msg_time

                if item in needs_dict:
                    receivers=needs_dict[item].keys()
                    receivers.sort()
                    receivers1=receivers[0]
                    receivers2=receivers[3]
                    name=needs_dict[item][receivers2]
                    if(needs_dict[item][receivers1] <= int(haves_dict[item][chat_id])):
                        count=int(haves_dict[item][chat_id])-needs_dict[item][receivers1]
                        if(count>0):
                            haves_dict[item][chat_id]=count
                            bot.sendMessage(receivers1,"Hey, "+str(haves_dict[item]['name'])+" has "+item)
                            del needs_dict[item]
                        else:
                            bot.sendMessage(receivers1,"Hey, "+str(haves_dict[item]['name'])+" has "+item)
                            del needs_dict[item]
                            del haves_dict[item]
            
        #bot.sendMessage(chat_id, msg['text'])
        print "################################"
        print "Needs Dict: ",needs_dict
        print "Haves Dict: ",haves_dict

        ################################################################################################################
        #Eg inp => I want to study maths
        #Eg inp => I can teach 10 maths
        if(len(inp) == 5):
            request_type=inp[1]
            subject=inp[4]
            qty=inp[3]
            #######################This is for 'want' to study###########################################
            if request_type == 'want':
                need_subject_dict[subject] = {}
                need_subject_dict[subject][chat_id]=need_subject_dict[subject].get(chat_id,0)+ 1
                need_subject_dict[subject]['name'] = name
                #Getting the coordinates
                send_url = 'http://freegeoip.net/json'
                r = requests.get(send_url)
                j = json.loads(r.text)
                lat = j['latitude']
                lon = j['longitude']

                need_subject_dict[subject]['latitude'] = lat
                need_subject_dict[subject]['longitude'] = lon

                msg_time=time.time()
                need_subject_dict[subject]['time'] = msg_time
                need_subject_dict[subject]['need'] = 'true'
                print msg_time
                print lat,"-----",lon
                print str(chat_id) + " Needs " + str(subject) + " registered"

                firebase1 = firebase.FirebaseApplication('https://cmu-hackathon-python.firebaseio.com/')
                result=firebase1.post('/want_record',{
                    "chat_id":chat_id,
                    "name":name,
                    "latitude":lat,
                    "longitude":lon,
                    "time":msg_time,
                    "subject":subject,
                    "need":"true"
                    })
                
                if subject in provide_subject_dict:
                    receivers=provide_subject_dict[subject].keys()
                    receivers.sort()
                    receivers1=receivers[0]
                    receivers2=receivers[3]
                    name=provide_subject_dict[subject][receivers2]
                    if(int(provide_subject_dict[subject][receivers1]) > 0):
                        count = int(provide_subject_dict[subject][receivers1]) - 1
                        if count > 0:
                            provide_subject_dict[subject][receivers1] = count
                            bot.sendMessage(chat_id,"Hey, "+str(name)+" can teach "+str(subject))
                            del need_subject_dict[subject]
                        else:
                            bot.sendMessage(chat_id,"Hey, "+str(name)+" can teach "+str(subject))
                            del need_subject_dict[subject]
                            del provide_subject_dict[subject]
                elif subject not in provide_subject_dict:
                    bot.sendMessage(chat_id,"You will be notified once someone volunteers for providing tuitions for "+str(subject))
        
             
            if request_type == 'can':
                provide_subject_dict[subject]={}
                provide_subject_dict[subject][chat_id] = provide_subject_dict[subject].get(chat_id,0) + int(qty)
                provide_subject_dict[subject]['name'] = name

                #Getting the coordinates
                send_url = 'http://freegeoip.net/json'
                r = requests.get(send_url)
                j = json.loads(r.text)
                lat = j['latitude']
                lon = j['longitude']

                provide_subject_dict[subject]['latitude'] = lat
                provide_subject_dict[subject]['longitude'] = lon

                msg_time=time.time()
                provide_subject_dict[subject]['time'] = msg_time
                provide_subject_dict[subject]['need'] = 'false'
                print msg_time

                if subject in need_subject_dict:
                    receivers=need_subject_dict[subject].keys()
                    receivers.sort()
                    receivers1=receivers[0]
                    receivers2=receivers[3]
                    if(int(provide_subject_dict[subject][chat_id]) >= 0):
                        count=int(provide_subject_dict[subject][chat_id]) - (1)
                        if(count > 0):
                            provide_subject_dict[subject][chat_id]=count
                            bot.sendMessage(receivers1,"Hey, "+provide_subject_dict[subject]['name']+" can teach "+str(subject))
                            del need_subject_dict[subject]
                        else:
                            bot.sendMessage(receivers1,"Hey, "+provide_subject_dict[subject]['name']+" can teach "+str(subject))
                            del provide_subject_dict[subject]
                            del need_subject_dict[subject]
           
                
            print "################################"
            print "Needs Dict: ",need_subject_dict
            print "Haves Dict: ",provide_subject_dict

        if(len(inp) == 1):
            request_type = inp[0].lower()
            if(request_type == "hi" or request_type == "hello"):
                bot.sendMessage(chat_id,"Hello "+str(name)+"! How can I help you today?\nPlease enter a number from 1-4 from the following options:\n1. Need something\n2. Provide something\n3. Want to study\n4. Provide tuitions")
            elif(request_type == "thanks"):
                bot.sendMessage(chat_id,"Glad I could help!")
            elif(request_type == "1"):
                bot.sendMessage(chat_id,"Try something like: 'I need 2 shirts'")
            elif(request_type == "2"):
                bot.sendMessage(chat_id,"Try something like: 'I have 2 blankets'")
            elif(request_type == "3"):
                bot.sendMessage(chat_id,"Type something like: 'I want to study maths'")
            elif(request_type == "4"):
                bot.sendMessage(chat_id,"Type something like: 'I can teach 10 physics")
            elif(msg['text'] == "/start"):
                bot.sendMessage(chat_id,"Process beginning")
            elif(request_type > 4):
                bot.sendMessage(chat_id,"Oops, I didn't get that.")
        
bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)

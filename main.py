import paho.mqtt.client as mqtt
import queue
import json
import hashlib

# Paramètres de connexion au broker MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45

# Nom d'utilisateur et mot de passe pour la connexion au broker MQTT 
MQTT_USERNAME = "admin"
MQTT_PWD = "admin"

# Liste des canaux de discussion disponibles
channels = []

# Queue des messages reçu non traités
message_enqueued = queue.Queue()

# Fonction appelée lorsqu'un client se connecte au broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT.")
        client.subscribe("global")
        client.subscribe("login")
    else:
        print("Impossible de se connecter au broker MQTT. Code de retour : " + str(rc))

# Fonction appelée lorsqu'un client se connecte au broker MQTT   
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Déconnexion du broker. Code de retour : ", rc)

# Fonction appelée lorsqu'un message est reçu sur un canal de discussion
def on_message(client, userdata, msg):
    msg_dict = json.loads(msg.payload.decode('utf-8'))
    #msg_dict["topic"] = msg.topic
    if msg_dict["type"] != "channel" or msg_dict["topic"] in channels :
        message_enqueued.put(msg_dict)

# Fonction appelée lorsqu'un utilisateur rejoint un canal
def on_join(client, userdata, message):
    channel_name = message.payload.decode('utf-8') # nom du canal
    print(f"{userdata['username']} a rejoint le canal {channel_name}")
    userdata['channel'] = channel_name # stocker le nom du canal dans les données utilisateur
    client.subscribe(channel_name) # s'abonner au canal
    message = f"{userdata['username']} a rejoint le canal {channel_name}"
    client.publish(channel_name, message) # publier un message pour informer les autres utilisateurs du canal

# Fonction appelée pour afficher les message dans la queue
def print_messages(client):
    print("\n>>>>>")
    temp_queue = queue.Queue()
    while not message_enqueued.empty():
        try:
            msg = message_enqueued.get_nowait()
            if msg["type"]=="public":
                print("[] @{} : \"{}\"".format(msg["user"], msg["message"]))
            elif msg["type"]=="channel" and msg["topic"] in channels :
                print("[#{}] @{} : \"{}\"".format(msg["topic"], msg["user"], msg["message"]))
            elif msg["type"]=="prive" :
                print("[{}/{}] @{} : \"{}\"".format(MQTT_USERNAME, msg["topic"], msg["user"], msg["message"]))
            elif msg["type"]=="invitation" :
                print("[INVITATION] @{} vous invite à rejoindre le canal {}".format(msg["user"], msg["message"]))
                ret = input("Entrer 0 pour refuser ou 1 pour accepter ")
                if ret == "1":
                    ret = client.subscribe(canonical_channel_name("global/",msg["message"]))
                    if ret[0] == mqtt.MQTT_ERR_SUCCESS  :
                        channels.append(msg["message"])
                        print ("Vous avez bien rejoint le canal.\n")
                    else :
                        print("Impossible de rejoindre le canal. Code de retour : " + str(ret.rc))
            else :
                print("/!\ Type de message non supporté ")
        except queue.Empty:
            break
    print("Plus de message à afficher !\n<<<<<\n")

# Fonction appelée pour envoyer un message
def send_message(client, topic, canal, type):
    msg = input("Entrer votre message à envoyer : ")
    msg_dict = {"topic": canal, "user" : MQTT_USERNAME, "message" : msg, "type" : type}
    ret = client.publish(topic, json.dumps(msg_dict).encode('utf-8') )
    if ret.rc == mqtt.MQTT_ERR_SUCCESS  :
        print ("Votre message a bien été envoyé !")
    else :
        print("Impossible d'envoyer le message. Code de retour : " + str(ret.rc))

# Fonction qui retourne le nom en hexadecimal et haché des topic pour éviter les erreurs
def canonical_channel_name(type, topic):
    return type+hashlib.sha256(topic.encode('utf-8')).hexdigest()



def main():
    
    # Connexion au broker
    client = mqtt.Client(userdata={'username': MQTT_USERNAME, 'channel': 'global'}) # créer un client MQTT avec les données utilisateur

    # Ajout des fonctions de rappel pour les événements MQTT
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    client.message_callback_add("join", on_join) # ajouter la fonction on_join comme callback pour le topic "join"
    
    client.username_pw_set(MQTT_USERNAME, MQTT_PWD) # identification

    # Connexion au broker MQTT
    print("Connexion au broker MQTT...")
    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL) # se connecter au broker MQTT

    # Boucle principale MQTT pour rester connecté au broker
    client.loop_start()
    
    # Se préparer à recevoir des messages privés
    ret = client.subscribe(canonical_channel_name("prive/",MQTT_USERNAME))
    if ret[0] != mqtt.MQTT_ERR_SUCCESS  :
        print("Impossible de recevoir des messages privés. Code de retour : " + str(ret.rc))
    
    
    
    # Se préparer à recevoir des invitations
    ret = client.subscribe(canonical_channel_name("invitation/",MQTT_USERNAME))
    if ret[0] != mqtt.MQTT_ERR_SUCCESS  :
        print("Impossible de recevoir des invitations. Code de retour : " + str(ret.rc))
    
    # Boucle principale pour la saisie des commandes utilisateur
    while True:
        
        print("==============================")
        print("Bienvenue dans le forum MQTT !")
        print("==============================")
        print("1. Envoyer un message au chat général")
        print("2. Afficher les messages en attente")
        print("3. Créer un canal")
        print("4. Rejoindre un canal")
        print("5. Publier dans un canal")
        print("6. Quitter un canal")
        print("7. Envoyer un message privé")
        print("8. Envoyer une invitation")
        print("0. Quitter")
        
        # Lecture de la commande utilisateur
        cmd = input("Entrer votre choix : ")

        # Envoyer un message au chat général
        if cmd == "1":
            send_message(client, "global", "global", "public")
        
        # Afficher les messages en attente
        if cmd == "2":
            print_messages(client)
            
        # Créer un canal
        if cmd == "3":
            canal = input("Entrer le nom du canal à ajouter : ")
            if canal in channels:
                print("\n/!\ Erreur, le canal existe déjà !\n")
            else :
                print("Canal ajouté.")
                channels.append(canal)
            ret = input("Voulez vous rejoindre ce canal tout de suite ? 0 = NON 1 = OUI ")
            if ret == "1":
                ret = client.subscribe(canonical_channel_name("global/",canal))
                if ret[0] == mqtt.MQTT_ERR_SUCCESS  :
                    print ("Vous avez bien rejoint le canal.\n")
                else :
                    print("Impossible de rejoindre le canal. Code de retour : " + str(ret.rc))
        
        # Rejoindre un canal
        if cmd == "4":
            canal = input("Entrer le nom du canal à rejoindre : ")
            if canal in channels :
                ret = client.subscribe(canonical_channel_name("global/",canal))
                if ret[0] == mqtt.MQTT_ERR_SUCCESS  :
                    print ("Vous avez bien rejoint le canal.\n")
                else :
                    print("Impossible de rejoindre le canal. Code de retour : " + str(ret.rc))
            else :
                print("\n/!\ Erreur, le canal n'existe pas !\n")
                
            
        # Publier dans un canal
        if cmd == "5":
            canal = input("Entrer le nom du canal dans lequel publier : ")
            if canal in channels:
                send_message(client, canonical_channel_name("global/",canal), canal, "channel")
            else :
                print("\n/!\ Erreur, le canal n'existe pas !\n")
            
        # Quitter un canal
        if cmd == "6":
            canal = input("Entrer le nom du canal à quitter : ")
            if canal in channels:
                ret = client.unsubscribe(canonical_channel_name("global/",canal))
                if ret[0] == mqtt.MQTT_ERR_SUCCESS  :
                    channels.remove(canal)
                    print ("Vous avez bien quitté le canal.")
                else :
                    print("Impossible de quitter le canal. Code de retour : " + str(ret.rc))
                
            else :
                print("\n/!\ Erreur, le canal n'existe pas !\n")
            
        # Envoyer un message privé
        if cmd == "7": 
            send_to = input("Avec qui voulez vous discutter ? ")
            send_message(client, canonical_channel_name("prive/",send_to), send_to, "prive")
            
        # Envoyer une invitation
        if cmd == "8":
            send_to = input("Avec qui voulez vous envoyer l'invitation ? ")
            canal = input("Dans quel canal voulez-vous l'inviter ? ")
            msg_dict = {"topic": "", "user" : MQTT_USERNAME, "message" : canal, "type" : "invitation"}
            ret = client.publish(canonical_channel_name("invitation/",send_to), json.dumps(msg_dict).encode('utf-8') )
            if ret.rc == mqtt.MQTT_ERR_SUCCESS  :
                print ("Votre invitation a bien été envoyé !")
            else :
                print("Impossible d'envoyer l'invitation. Code de retour : " + str(ret.rc))
        
        # Quitter
        if cmd == "0":
            print("Fermeture du broker MQTT...")
            client.loop_stop()
            client.disconnect()
            break  # Sortir de la boucle while True

    print("Fin du programme")


if __name__ == '__main__':
    main()


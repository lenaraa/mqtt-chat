# Chat MQTT

## Présentation

Il s'agit d'un projet dans le cadre de mes études à Efficom dont le but est d'implémenter un forum de discussion en temps réel avec MQTT

## Fonctionnement global

Le code python utilise Paho-MQTT, une bibliothèque client MQTT open source pour Python qui fournit une interface de programmation pour communiquer avec des brokers MQTT tels que Mosquitto. Mosquitto est un broker MQTT open source qui implémente le protocole MQTT et permet la communication entre les clients MQTT. Vous trouverez le fonctionnement de la bibliothèque paho-MQTT à l'adresse https://pypi.org/project/paho-mqtt/
L'application fonctionne entièrement dans le terminal.

## Prérequis

Il faut installer :
- Python (https://www.python.org/)
- Broker Mosquitto (https://mosquitto.org/)
- Paho-Mqtt (https://pypi.org/project/paho-mqtt/)

Pour installer paho-mqtt, vous pouvez lancer la commande `pip install paho-mqtt`  


## Configuration du broker MQTT

1. Récupérez le fichier mosquitto.conf du github
2. Remplacez le fichier mosquitto.conf de votre installation par celui là (dans le dossier `C:\Program Files\mosquitto` par défaut sous Windows et `/etc/mosquitto/mosquitto.conf` sous Ubuntu)
3. Ouvrez un terminal dans le même dossier
4. Pour créer le fichier des utilisateurs lancez la requête `mosquitto_passwd -c mosquitto_pwd_file admin`
5. Comme mot de passe, entrez `admin`
6. (Facultatif) Pour ajouter d'autres utilisateurs, lancer la requête `mosquitto_passwd -b mosquitto_pwd_file [username] [password]`

Par défaut le client se connecte sur `localhost:1883` et vérifie que la connexion est toujours active et que les deux parties sont toujours en communication toutes les 45s.

Vous pouvez modifiez ces paramètres dans le code python en modifiant les variables MQTT_BROKER, MQTT_PORT et MQTT_KEEPALIVE_INTERVAL.


## Lancement 

1. Dans un terminal, lancer mosquitto avec `mosquitto -c mosquitto.conf` 
2. Lancez votre code python
3. Pour discuttez avec d'autres utilisateurs, vous pouvez lancer plusieurs instances de python. Vous pouvez également modifiez les paramètres MQTT_USERNAME et MQTT_PWD pour utiliser des utilsateurs différents après les avoir déclarés dans la partie 6 de la configuration.
4. Suivre les instructions dans le terminal


## Fonctionnement des messages

Par défaut au lancement de l'application, on ne reçoit que les messages globaux.

Les messages sont des dictionnaires avec le topic dans lequel on l'a reçu (en clair), l'utilisateur qui l'a envoyé, le contenu du message et son type.

Les messages reçus arrive dans une Queue et sont retirés de la queue à la lecture du message.


## Fonctionnement des topics

En dehors du channel global, le nom des channel est hashé puis converti en hexadécimal pour éviter les erreurs mosquitto dues aux wildcards. Les topics sont divisés par type :

1. Public
Tous les messages envoyés dans le global sont envoyés et reçus.

2. Channel
Quand on crée un channel, on l'ajoute à la liste des channel dont on accepte les messages. Si on rejoint ce channel, on va y subscribe afin d'également recevoir les messages. Si on le quitte, on l'enlève de la liste des messages et on l'unsubcribe.

3. Prive
Chaque utilisateur est subscribe à son propre channel privé. Pour envoyer des messages à un utilisateur, il faut donc envoyer des messages à son canal prive/[username] en indiquant son nom dans le champ topic.

4. Invitation
De manière similaire, chaque utilisateur est subscribe à son propre channel invitation. Pour inviter un utilisateur, il faut donc envoyer un message à son canal invitation/[username] en indiquant son nom dans le champ topic et le nom du canal dans le corp du message.

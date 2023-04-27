mosquitto_pub -h localhost -t login -m "mon_username"


# Chat MQTT

## Présentation

Il s'agit d'un projet dans le cadre de mes études à Efficom dont le but est d'implémenter un forum de discussion en temps réel avec MQTT

## Fonctionnement global


## Prérequis
- Python (https://www.python.org/)
- Broker Mosquitto (https://mosquitto.org/)
- Paho-Mqtt (https://pypi.org/project/paho-mqtt/)

Pour installer paho-mqtt, vous pouvez lancer la commande `pip install paho-mqtt`  


## Configuration 

Par défaut le client se connecte sur `localhost:1883` et vérifie que la connexion est toujours active et que les deux parties sont toujours en communication toutes les 45s.

Vous pouvez modifiez ces paramètres dans le code python en modifiant les variables MQTT_BROKER, MQTT_PORT et MQTT_KEEPALIVE_INTERVAL.


## Lancement 

1. Lancez votre code python
2. Ouvrez d'autres terminaux pour envoyer des messages ou s'inscrire au forum

# Utilisations de Forum MQTT

## Connexion et inscription

TODO

## Inscription à un channel

TODO

## Discussion personnelle entre 2 utilisateurs

TODO

## Gestion des topics personnels

Vous pouvez créer / rejoindre / quitter / inviter dans un topic ! **seul le topic général n'est pas modifiable**

### Créer un topic

1. Il suffit de cliquer en bas à gauche dans le menu des canaux `Créer un topic`
2. Entrez le nom de votre topic dans la pop-up et validez !

Vous pourrez voir et accéder à votre topic qui se situe sur la gauche.

### Invitez dans un topic
1. Cliquez sur l'icône en forme d'enveloppe à coté du nom du topic à sélectionner.
2. Cochez dans la pop-up les gens à inviter.
3. Et c'est tout ! De leurs côté  ils devront cliquer sur l'invitation, et à vous les discussions de groupe privé !

**NOTE : Seul le propriétaire du topic peut gérer les invitations (un choix du développeur)**

![invit](assets/react_invit_topic.gif)

### Quittez dans un topic

1. Cliquez tout simplement sur la petite croix rouge à côté du nom du topic, fini !
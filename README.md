
# Projet AI Quarto

Pour notre travaille de fin de 2ème Bac en ingénieur industriel a l'Ecam orientation Génie Electrique, notre professeur d'informatique nous a mis au défis de créer une intelligence artificiel jouant au jeux Quarto.
Pour ce faire il nous a mis a disposition une librairie ainsi qu'un code pour la structure du jeux.

## Fonctionnement 

Pour créer mon intelligence artificiel j'ai décidée d'utiliser la librairie EasyAI [http://zulko.github.io/easyAI/index.html](http://zulko.github.io/easyAI/index.html) grace a cette librairie j'ai pu utiliser différent algorithme du type Alpha-Beta pruning, dans mon cas j'utilise plus précisément l'algorithme Negamax [https://en.wikipedia.org/wiki/Negamax](https://en.wikipedia.org/wiki/Negamax) ainsi que la méthode Solving qui va résoudre la partie en utilisant Negamax avec différente profondeur de recherche.

Pour générer le coups qui sera jouer différente intelligence sont disponible ( voir [Intelligence](#intelligence) ). 
L'intelligence principale, l'intelligence *client*, utilise la fonction id_solve de la class Solving qui va me retourner plusieurs information dont la mouvement le plus interessant pour arriver a la victoire le plus rapidement.

#### Utilisation

Pour jouer au jeux vous devez lancer 3 terminale depuis le dossier ou est enregistrer le jeux.
 1. [Fenêtre 1] : server du jeux
 2. [Fenêtre 2] : client 1 du jeux
 3. [Fenêtre 3] : client 2 du jeux
*vous pouvez lancer 2 fois le même client*

#### Intelligence
 1. client : utilisation de id_solve *(recommander)*
 2. clientB : utilisation de Negamax avec transposition table
 3. user : pour jouer contre l'IA
 4. rdm : AI qui agis 100% aléatoirement
 5. prof : AI d'origine

#### Lancer une partie 
##### Server :
    ./quarto.py server --verbose

##### Client :
    ./quarto.py *Intelligence* *Nom* --verbose

Vous avez aussi la possibilité de lancer les clients et server sur différente machine, il vous faudra donc préciser l'IP du host ainsi que le port de communication (*Pars défaut le host = localhost et le port = 5000*) :
    
##### Server disant :
    ./quarto.py server --verbose --host= *IP* --port= *Port*

##### Client distant :
    ./quarto.py *Intelligence* *Nom* --verbose --host= *IP* --port= *Port*
    
#### Test AI
    ./quarto.py ai --verbose --algo= *algo* --depth= *depth* --tt

 1. algo : choisissez entre Negamax, SSS, solve. Default = Negamax
 2. depth : profondeur de la recherche de l'AI . Default = 3
 3. tt : active la transposition table. Default = False

*C'est 3 arguments ne sont pas obligatoire*

Le test AI n'a pas besoin du serveur il peut être lancer dans une seul fenêtre de terminal.

<!--stackedit_data:
eyJoaXN0b3J5IjpbLTQ1MTkyNTAxMSwtMTQ2MDQ3MjQyMSwtMT
Q2MDQ3MjQyMSw5MjI2NDc2NywtMTQ1NjM5MzIzMSwxMTY4NTgw
ODg4LC0yMDY3NjE5Mjg2LDIwMjY0NzkzOTEsODcyNTM0NzMzLC
02NTUyNzI4MTUsLTE0OTEzNDQzNTAsLTIwMzc1MzgzMTUsODkx
Mzg4NzAxLC0yMDQwMjYyNjE0LC0yMDIzODI3NDE0LDg2NDY2OT
QwOCwxMDM3NjQ5OTI2LDEwMzc2NDk5MjYsLTI5Nzc5NjI5LC0x
NzMzODQyMDY2XX0=
-->
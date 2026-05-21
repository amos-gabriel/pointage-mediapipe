# Script de Démo Vidéo — 5 minutes

## Matériel Requis
- [ ] Webcam fonctionnelle
- [ ] 2-3 personnes enrôlées dans le système
- [ ] OBS Studio ou logiciel d'enregistrement écran
- [ ] Résolution : 1920x1080, 30 FPS
- [ ] Micro optionnel (commentaires voix off)

---

## Déroulé Chronométré

### 0:00 – 0:25 | Introduction & Lancement
**Action** : Ouvrir un terminal, montrer la commande de lancement
```bash
source venv/bin/activate
python run.py
```
**Montrer** : Le terminal affiche "Chargement des visages connus... 3 visages chargés"  
**Ouvrir** : `http://localhost:5000` dans le navigateur  
**Montrer** : Page d'accueil avec les 2 boutons d'interface  
**Dire / sous-titres** : *"Système de pointage automatique — Master 2 — Interface principale"*

---

### 0:25 – 0:50 | Interface Pointage — Vue Générale
**Action** : Cliquer sur "Interface Pointage"  
**Montrer** :
- Le flux vidéo en direct
- La liste vide "Présences du jour : 0"
- Les overlays (aucun visage dans le champ pour l'instant)

---

### 0:50 – 1:40 | Scénario 1 — Personne Connue + Main Levée ✅
**Action** : 
1. Personne A entre dans le champ de la caméra
2. Attendre que le rectangle vert s'affiche avec son nom
3. Lever la main
4. Attendre 2 secondes → confirmation visuelle (icône ✅ ou bordure clignotante)

**Montrer** :
- Rectangle **orange** : "Détecté — Alice Dupont (confiance: 87%)"
- Main levée → rectangle passe **vert** + barre de progression 2s
- Confirmation → rectangle **vert foncé** + "✅ Pointé : 09:34:12"
- Dans la liste à droite : "Alice Dupont — 09:34:12 — ✅ Présente"

**Zoomer** sur la liste des présences pour montrer l'enregistrement.

---

### 1:40 – 2:10 | Scénario 2 — Personne Connue SANS Main Levée ❌
**Action** :
1. Personne B entre dans le champ
2. Reste immobile, ne lève PAS la main
3. Attendre 10-15 secondes

**Montrer** :
- Rectangle **orange** : "Bob Martin — Non pointé"
- La liste des présences NE change PAS
- Dire/sous-titres : *"Le geste de main levée est obligatoire — présence non enregistrée"*

---

### 2:10 – 2:30 | Scénario 3 — Personne Inconnue 👤
**Action** : Montrer une personne non enrôlée  
**Montrer** :
- Rectangle **rouge** : "Inconnu"
- Aucun enregistrement, aucune action

---

### 2:30 – 3:30 | Interface Comptage 🔢
**Action** : Ouvrir un nouvel onglet → `http://localhost:5000/counting`  
**Montrer** :
1. **1 personne** dans le champ → compteur affiche "1"
2. **2e personne** entre → compteur passe à "2"
3. **3e personne** entre → "3"
4. Une personne sort → "2"
5. Montrer le graphique temps réel qui s'actualise

**Zoomer** sur le compteur numérique grand format.  
**Dire** : *"Cette interface ne fait que compter — pas d'identification — utile pour la gestion de capacité de salle"*

---

### 3:30 – 4:15 | Base de Données & Historique
**Action** : Ouvrir `http://localhost:5000/admin`  
**Montrer** :
- Liste des utilisateurs enrôlés (nom, matricule, date d'enrôlement)
- Page `/admin/history` : tableau des pointages avec filtre par date
- Les entrées créées lors de la démo apparaissent bien

**Optionnel** : ouvrir le fichier SQLite avec DB Browser for SQLite et montrer la table `attendance`

---

### 4:15 – 4:45 | Export & Synthèse
**Action** : Cliquer sur "Exporter CSV du jour"  
**Montrer** : Le fichier CSV téléchargé avec les colonnes nom, prenom, matricule, timestamp, statut

---

### 4:45 – 5:00 | Conclusion
**Montrer** : Retour sur l'interface principale  
**Dire / Sous-titres** :
*"Système fonctionnel : reconnaissance faciale + geste de pointage + comptage temps réel — Stack : Python, Flask, OpenCV, MediaPipe, face_recognition — Projet Master 2"*

---

## Conseils d'Enregistrement

1. **Éclairage** : éviter le contre-jour, bien éclairer les visages de face
2. **Distance caméra** : 1 à 2 mètres pour que les visages soient bien visibles
3. **Résolution** : enregistrer en 1080p minimum
4. **Fond** : fond uni (mur blanc/gris) pour meilleure détection
5. **Post-production** : ajouter des sous-titres avec les étapes, couper les silences
6. **Logiciels** : OBS Studio (gratuit) pour la capture, DaVinci Resolve pour le montage

## Problèmes Courants Avant la Démo

| Problème | Solution |
|---|---|
| Caméra non détectée | Changer `CAMERA_INDEX=1` dans `.env` |
| Visage non reconnu | Re-enrôler avec `python scripts/register_face.py` en bonne lumière |
| Main levée pas détectée | Lever la main plus haut, paume face caméra |
| FPS trop bas | Réduire résolution : changer en `(320, 240)` dans `camera.py` |

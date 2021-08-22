# OSIRIS

English below.

Les fichiers synthèse contenant les données du jeu de données OSIRIS ont été produits
par le Centre d'Expertise de Données de l'ASC en utilisant python. Pour plus de détails sur le script qui a
généré ces fichiers ou si vous avez un problème, veuillez créer un "issue" Github, ou contacter nous par email à asc.donnees-data.csa@canada.ca.

Ces fichiers synthèses ont été créés en tenant compte des conventions de données climatiques et prévisionnelles (fournies par earthdata.nasa.gov). OSIRIS est un instrument de mesure installé sur le satellite suédois Odin. Avant d'utiliser les fichiers sommaires, assurez vous de vous renseigner sur les objectifs de cet instrument sur le [site web pour OSIRIS](https://research-groups.usask.ca/osiris/). Pour faciliter l'usage des données, assurez vous d'avoir aussi lu [le guide d'utilisateur](ftp://data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/OSIRIS/Supporting%20Documents/OSIRIS-Level2-Daily-Data-Products-Users-Guide). Vous pouver aussi visiter la page d'OSIRIS sur [le portail de données ouvertes de l'ASC](https://data.asc-csa.gc.ca/dataset/6c3f7e9c-7b43-4a6b-a924-a1bef1a9cf74).

Les fichiers synthèses ont été produits à l'aide du script osiris.py, qui contient de la documentation parmis le code.
La validité des fichiers synthèses a été testée à l'aide du script verification.py. Le but de ce script était d'assurer
que les fichiers synthèses contiennent les données qui sont exactement les mêmes que les données stockées sur le portail de données de l'ASC. Chaque fichier avait un
taux d'exactitude de 99,7 % ou plus, les 0,3 % étant causés par de rares artefacts dans les données stockées sur le portail de données (c'est-à-dire des fichiers existants
qui sont simplement vides). En savoir plus sur le processus de vérification avec la documentation dans le code.

Un example d'utilisation des fichiers sommaires est la création facile de graphique comme celui-ci:
![Aerosol_time](https://user-images.githubusercontent.com/56747050/130344095-64316a43-e68c-452e-bf06-ba9e2f934ebf.png)

(Gardez en tête que ce graphique contient plusieurs millions de points.)

Vous pouvez consulter tous les graphiques dans le dossier "Plots".

==================================================================================

The summary files containing the data from the OSIRIS dataset were produced by the CSA Data Centre of Expertise using python. If you encounter any problems with the script that generated these files, please create a Github "issue", or contact us by email at asc.donnees-data.csa@canada.ca.

These summary files were created taking into account the climate and forecast data conventions (provided by earthdata.nasa.gov). OSIRIS is a measuring instrument installed on the Swedish satellite Odin. Before using the summary files, be sure to read out about the purposes of this instrument on the website for OSIRIS. In order to properly use this data, be sure to read the user guide as well. You can also visit the OSIRIS page on the CSA open data portal.

The summary files were produced using the osiris.py script, which contains documentation within the code. The validity of the summary files was tested using the verification.py script. The purpose of this script was to ensure that the summary files contain data which is exactly the same as the data stored on the ASC data portal. Each file had an accuracy rate of 99.7% or better, with the 0.3% being caused by rare artifacts in the data stored on the data portal (i.e. existing files that are simply empty). Learn more about the verification process with the documentation in the code.

An example of the use of summary files is the easy creation of graphs like this:
![Aerosol_time](https://user-images.githubusercontent.com/56747050/130344095-64316a43-e68c-452e-bf06-ba9e2f934ebf.png)

(Keep in mind that this graph contains several million points.)

You can view all the graphics in the "Plots" folder.




# WINDII

English below.

Les fichiers synthèses contenant les données du jeu de données WINDII ont été produits
par le Centre d'Expertise de Données de l'ASC en utilisant python. Pour plus de détails sur le script qui a
généré ces fichiers, ou pour signaler un problème, veuillez créer un "issue" Github, ou contacter asc.donnees-data.csa@canada.ca.

Ces fichiers synthèses ont été créés en tenant compte des conventions de données climatiques et prévisionnelles (fournies par earthdata.nasa.gov).
L'Interferomètre d'Imagerie du Vent (WINDII, en anglais) est une initiative de l'ASC lancé sur le Satellite de Recherche en Haute Atmosphère de la NASA
le 12 septembre 1991. Les données crées sont une propriété de l'ASC et vous pouvez trouver ces données sur [le portail de données ouvertes de l'ASC](https://data.asc-csa.gc.ca/fr/dataset/4501efc8-9fe0-4a52-9a60-f2657a969c0b).
Avant l'utilisation des données crées par ce script, il est important d'avoir un apercu sur la documentation existant sur le portail. Plus spécifiquement, [le
guide de l'utilisateur](https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/WINDII-data-archive/Supporting-Documents/Digitized-Documents/WINDII-SDPPS-USERs-GUIDE-PDFA.pdf).

Les fichiers sommaires ont été produits à l'aide du script windii.py, qui contient la documentation parmis le code.
La validité des fichiers synthèses a été testée et une description plus en détail du processus de validation peut être trouvée
dans le fichier validation.txt. En bref, le test de validité consiste à choisir un "point" aléatoire parmis les données originales et ensuite on vérifie
que ce point existe dans le fichier sommaire et qu'il est exactement le même. Ce test est executé plusieurs millier de fois pour guarantir un haut taux de validité.
Les fichiers sommaires ont tous passés ces tests avec un taux de succès de 100%.

Pour exécuter un script x.py, vous devez vous assurez qu'il y a **un dossier nommé "temp" directement dans le même dossier que x.py** et puis exécuter la ligne

`python x.py`

Dans le terminal.

Un example de l'utilité de ces fichiers sommaire est la création simple de graphiques comme celui-ci:
![O1D_FD_Volume Emission Rate_altitude ](https://user-images.githubusercontent.com/56747050/130168857-6e294c07-1f18-4e49-8137-cfc2a49c275d.png)

(Gardez en tête que ce graphique démontre plusieurs milliers de points).

Vous retrouverez le reste des graphiques dans le fichier "Plots".

========================================================================

The summary files containing the data from the WINDII dataset were produced by the CSA Data Centre of Expertise using python. For more details on the script that generated these files, or to report a problem, please create a Github issue, or contact asc.donnees-data.csa@canada.ca.

These summary files were created with the climate and forecast data conventions (provided by earthdata.nasa.gov) in mind. The Wind Imaging Interferometer (WINDII) is a CSA initiative launched on the NASA Upper Atmosphere Research Satellite on September 12, 1991. The data created is property of the CSA and can be found on the [CSA open data portal](https://data.asc-csa.gc.ca/fr/dataset/4501efc8-9fe0-4a52-9a60-f2657a969c0b). Before using the data created by these scripts, it is important to have an overview of the documentation existing on the portal. More specifically, the [user's guide](https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/WINDII-data-archive/Supporting-Documents/Digitized-Documents/WINDII-SDPPS-USERs-GUIDE-PDFA.pdf).

The summary files were produced using the windii.py script, which contains documentation within the code. The validity of the summary files has been tested and a more detailed description of the validation process can be found in the validation.txt file. In short, the validity test consists in choosing a random "point" among the original data and then we verify that this point exists in the summary file and that it is exactly the same. This test is performed several thousand times to ensure a high rate of validity.
Summary files all passed these tests with a 100% success rate.

To run the script x.py you need to make sure there is **a folder named "temp" directly in the same folder as x.py** and then run the line

`python x.py`

In the terminal.

For data validation the **ExamplePlots.pdf** was made containing various plots using the WINDII dataset. Check it out here [ExamplePlots.pdf](ExamplePlots.pdf)

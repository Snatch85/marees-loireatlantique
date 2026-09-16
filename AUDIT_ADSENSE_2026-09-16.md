# Audit AdSense — 16 septembre 2026

## Conclusion

Le site contient déjà beaucoup de contenu et plusieurs pages sont indexées par Google. Le problème n'est donc pas simplement un manque de nombre d'articles. Les principaux risques observés sont techniques et qualitatifs : liens cassés, copies techniques publiées, emplacements publicitaires invalides et CMP maison non certifiée.

## Corrections effectuées dans le dossier local

- 52 références internes cassées corrigées (0 restante au contrôle local).
- Redirections 301 ajoutées pour consolider les copies `/www/` et `/android/app/src/main/assets/public/` vers les URL canoniques.
- En-tête `X-Robots-Tag: noindex, nofollow` ajouté aux dossiers techniques `/www/` et `/android/`.
- Balise de propriété AdSense ajoutée à la page d'accueil : `ca-pub-1465276904717454`.
- Image Open Graph inexistante remplacée par une image réellement présente.
- 34 emplacements manuels factices retirés (`data-ad-slot=""` ou `data-ad-slot="AUTO"`).
- Injection JavaScript de deux autres emplacements factices par page supprimée.
- Ligne AdSense correcte confirmée dans `ads.txt` : `google.com, pub-1465276904717454, DIRECT, f08c47fec0942fa0`.
- Prévisualisation locale validée sur l'accueil, le blog et un guide important.

## Actions manuelles indispensables

1. Dans AdSense, ouvrir **Confidentialité et messages > Réglementations européennes** et activer la CMP Google avec trois choix : Accepter, Refuser, Gérer les options.
2. Après activation et déploiement, supprimer le bandeau de consentement maison pour éviter deux CMP concurrentes.
3. Laisser les annonces automatiques désactivées jusqu'à l'approbation. Le script officiel reste en place pour la vérification du site.
4. Dans Search Console, contrôler : Indexation > Pages, Sitemaps, Core Web Vitals, Actions manuelles et Problèmes de sécurité.
5. Vérifier que toutes les anecdotes, l'interview de « Marc », les affirmations d'expérience et les données réglementaires sont authentiques et sourcées. Retirer ou réécrire tout passage inventé ou générique avant une nouvelle demande d'examen.
6. Déployer les corrections, attendre que Google réexplore le site, puis demander un nouvel examen AdSense. Ne pas multiplier les demandes avant indexation des changements.

## Point à clarifier

Le fichier `ads.txt` contient une longue liste The Moneytizer. Elle est cohérente seulement si le compte The Moneytizer `130812` appartient bien à l'éditeur et reste actif. Sinon, remplacer ce fichier par la seule ligne Google ci-dessus. La politique de confidentialité doit également citer exactement les régies réellement utilisées.

## Données Search Console utiles pour la suite

- Capture du rapport **Indexation > Pages** avec les motifs d'exclusion et leurs nombres.
- Capture du rapport **Sitemaps**.
- Capture de **Core Web Vitals** mobile et ordinateur.
- Capture de **Actions manuelles** et **Problèmes de sécurité**.
- Capture de l'e-mail ou du motif exact du refus AdSense.


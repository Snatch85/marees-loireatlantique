#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_adsense_complet.py
Corrections pour obtenir l'approbation Google AdSense :
1. Supprime les fausses pubs "ad-slot" (violation de politique)
2. Ajoute le script AdSense auto-ads dans le <head>
3. Supprime le <ins> avec data-ad-slot="AUTO" invalide
4. Ajoute du contenu éditorial riche et unique à chaque page ville
"""

import os, re

BASE = r"C:\Users\33629\Desktop\Maree loire atlantique"

# ─── SCRIPT ADSENSE AUTO-ADS À INSÉRER DANS LE <HEAD> ───────────────────────
ADSENSE_SCRIPT = '''<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1465276904717454" crossorigin="anonymous"></script>'''

# ─── CONTENU ÉDITORIAL UNIQUE PAR PORT ──────────────────────────────────────
EDITORIAL = {

"marees-saint-nazaire": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à Saint-Nazaire — tout ce qu'il faut savoir</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le port de référence du département 44</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Saint-Nazaire est le <strong>port de référence pour les marées de Loire-Atlantique</strong>. Toutes les stations locales (Le Croisic, Pornic, La Turballe…) sont calculées par rapport aux constantes harmoniques de Saint-Nazaire. Avec un <strong>marnage de 5,2 m en vive-eau</strong> et jusqu'à 6 m lors des grandes vives-eaux (coefficient 110+), l'estuaire de la Loire génère des courants parmi les plus puissants du littoral atlantique français.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Chenal et navigation commerciale</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le chenal dragué à <strong>16 mètres</strong> accueille ferrys, porte-conteneurs, méthaniers et paquebots des Chantiers de l'Atlantique. Les plaisanciers doivent contacter <strong>Port Trafic sur le canal VHF 14</strong> avant toute traversée. En vive-eau, le courant peut atteindre <strong>4 nœuds dans l'axe du chenal</strong>. En crue hivernale de la Loire, le débit fluvial s'ajoute au jusant et peut dépasser 5 nœuds.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Pêche à pied : Villès-Martin et Grande Plage</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>Plage de Villès-Martin</strong> est le spot de pêche à pied le plus accessible depuis Saint-Nazaire centre (bus ligne 10). Dès que le coefficient dépasse 80, les rochers côté droit à marée basse découvrent des zones à <strong>bigorneaux, coques et moules de roche</strong>. Partez <strong>1h30 avant la basse mer</strong> et réglez une alarme 45 minutes après — la remontée est rapide par coefficient élevé. La <strong>Grande Plage</strong>, plus sableuse, offre de bonnes conditions de pêche aux coques dès coefficient 75. Consultez le classement sanitaire DDTM 44 la veille de toute sortie.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La base sous-marine et les épaves</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Saint-Nazaire abrite une des plus grandes <strong>bases sous-marines de la Seconde Guerre mondiale</strong>, classée monument historique. Les plongeurs trouvent dans les eaux de l'estuaire plusieurs épaves accessibles par coefficients faibles (mortes-eaux), quand les courants sont réduits. La <strong>visibilité dans l'estuaire est réduite par les apports sédimentaires de la Loire</strong> — préférez les sorties par coefficient 30-50 et conditions météo anticycloniques.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Caractéristiques des marées à Saint-Nazaire</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le régime est <strong>semi-diurne à inégalité diurne</strong> : deux pleines mers et deux basses mers par jour, avec une légère différence de hauteur entre les deux cycles. L'<strong>étale</strong> (courant nul) ne dure que 15 à 30 minutes selon le coefficient — une donnée critique pour les manœuvres portuaires. La montée (flot) est plus rapide que la descente (jusant) en vive-eau.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 95 : grandes découvertes — idéal pour la pêche à pied et l'exploration côtière</li>
        <li>Coefficient ≤ 45 : morte-eau — marnage réduit, peu de courant, conditions calmes pour la plaisance</li>
        <li>Traversée du chenal en plaisance : toujours contacter VHF 14 (Port Trafic)</li>
        <li>En navigation : vérifiez votre carte marine SHOM — les bouées de l'estuaire sont déplacées régulièrement</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong> (gratuit, 24h/24)</li>
      </ul>
""",

"marees-le-croisic": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées au Croisic — Côte Sauvage et presqu'île guérandaise</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le port de pêche authentique de la presqu'île</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le Croisic est l'un des derniers <strong>ports de pêche artisanale actifs de Loire-Atlantique</strong>. La criée SICA de la presqu'île guérandaise y débarque chaque matin turbots, soles, homards et langoustines. Le marnage de vive-eau atteint environ <strong>5 m</strong>, découvrant à basse mer des zones rocheuses d'une richesse exceptionnelle. Le port intérieur, protégé par la digue, accueille chalutiers et plaisanciers dans un décor de maisons de granit.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La Côte Sauvage : meilleur spot de pêche à pied du 44</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Entre la Pointe du Croisic et la Pointe du Bec, la <strong>Côte Sauvage</strong> expose à grande marée des dalles rocheuses couvertes d'<strong>huîtres sauvages, bigorneaux et étrilles</strong> d'une qualité rare. Coefficient minimum conseillé : <strong>85</strong>. Partez avant 7h du matin — la lumière rasante sur l'estran vaut le réveil. Les flaques entre les rochers abritent aussi des anémones et étoiles de mer. Attention : les rochers sont glissants, les chaussures à crampons sont indispensables.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Marais salants et éco-tourisme</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La presqu'île guérandaise est classée <strong>zone Natura 2000</strong>. Les marais salants qui bordent Le Croisic côté intérieur produisent la <strong>fleur de sel de Guérande</strong>, récoltée à la main par les paludiers de mai à septembre. Les marées influencent directement le niveau des chenaux d'alimentation des marais — un ecosystème fragile où la biodiversité est remarquable (avocettes, hérons, chevaliers). Respectez les zones protégées indiquées par les panneaux.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Plaisance et mouillages</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le port du Croisic offre environ <strong>600 anneaux</strong> dont une centaine de places visiteurs. L'accès se fait par passe sud balisée — chenaux étroits à emprunter avec précaution par fort coefficient. Les bateaux à fort tirant d'eau (> 1,8 m) doivent vérifier les horaires de marée : le port peut être inaccessible aux 2 heures de part et d'autre de la basse mer en mortes-eaux.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 85 : Côte Sauvage accessible — huîtres sauvages et étrilles</li>
        <li>Coefficient ≥ 70 : bonne pêche à pied sur les rochers du bourg</li>
        <li>Classement sanitaire : consultez la DDTM 44 ou Géolittoral.fr la veille de chaque sortie</li>
        <li>Stationnement : gratuit hors saison côté ocean, payant en juillet-août</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-la-baule": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à La Baule — La grande plage de l'Atlantique</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La plus belle baie de l'Atlantique</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>Baule-Escoublac</strong> est connue pour ses <strong>8 kilomètres de plage de sable fin</strong> en arc de cercle, classée parmi les plus belles plages d'Europe. La station balnéaire, née à la Belle Époque, alterne villas 1900 et immeubles modernes. Le marnage de vive-eau atteint environ <strong>4,8 m</strong>. À basse mer par fort coefficient, la plage découvre jusqu'à 400 mètres de sable, transformant le paysage de manière spectaculaire.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Pêche à pied et activités de plage</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La plage de La Baule est principalement <strong>sableuse</strong> — idéale pour la récolte de <strong>coques et palourdes</strong> à basse mer. Les meilleurs spots se situent aux deux extrémités de la baie : vers Le Pouliguen côté ouest (zone plus rocheuse) et vers La Baule-les-Pins côté est. Coefficient minimum conseillé : <strong>75</strong>. La zone de Pornichet, en continuité de la plage, offre également de bonnes conditions par coefficients élevés.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Sports nautiques et kite-surf</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La baie de La Baule est un <strong>spot réputé de kite-surf et de windsurf</strong>, notamment par vent d'ouest à sud-ouest. Plusieurs écoles de voile et de surf y sont installées. Les conditions optimales combinent coefficient faible à moyen (courant limité) et vent de secteur ouest. La plage est également parfaite pour le char à voile et le longe-côte par marée descendante.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le port de La Baule (Pornichet)</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le port de plaisance de Pornichet, à l'extrémité est de la baie, compte plus de <strong>1 100 anneaux</strong> — l'un des plus grands ports de plaisance de Loire-Atlantique. Accès depuis le chenal balisé par tribord, accessible à tout état de marée pour les bateaux de tirant d'eau inférieur à 2 m. VHF canal 9 pour les capitaineries de La Baule et Pornichet.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 75 : bonne récolte de coques — zone sableuse aux deux extrémités de la baie</li>
        <li>Vent d'ouest + coefficient moyen : conditions idéales pour kite et windsurf</li>
        <li>Baignade : surveillance de juin à septembre, drapeaux à respecter</li>
        <li>Stationnement : payant en saison estivale sur tout le front de mer</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-la-turballe": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à La Turballe — Port thon et pêche artisanale</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le premier port thonier de Loire-Atlantique</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La Turballe est historiquement le <strong>premier port de pêche au thon germon</strong> de la côte atlantique. La criée y vend chaque matin les prises des chalutiers : sardines, maquereaux, bars, dorades et langoustines. Le marnage de vive-eau est d'environ <strong>4,9 m</strong>, légèrement inférieur à Saint-Nazaire en raison de la position plus exposée à l'Atlantique. Le port abrite environ 80 bateaux de pêche professionnelle.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Pêche à pied : les rochers de Pen Bron</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La pointe de <strong>Pen Bron</strong>, au sud de La Turballe, offre un accès remarquable à l'estran rocheux par grandes marées. Les rochers exposés à marée basse (coefficient ≥ 80) révèlent des colonies de <strong>bigorneaux, moules et huîtres sauvages</strong>. La zone est peu fréquentée en dehors des saisons touristiques — idéal pour les sorties matinales en hiver. Le chemin côtier longe les rochers sur 2 km depuis le port.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Les plages de La Turballe</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>Grande Plage de La Turballe</strong> (1,5 km de sable) est exposée à l'ouest — les vagues y sont souvent présentes, en faisant un spot apprécié des body-boarders. La plage de <strong>Pen Bé</strong>, plus abritée côté nord vers Piriac, est idéale pour les familles et la baignade par petits coefficients. Entre les deux, l'estran à basse mer libère de larges zones sableuses propices à la récolte de coques (coefficient ≥ 70).</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Spécificités des marées à La Turballe</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La Turballe est exposée au large sans protection naturelle majeure — les <strong>houles atlantiques</strong> se font davantage ressentir qu'à La Baule ou dans l'estuaire de la Loire. Par vent de secteur ouest à force 4 et plus, les vagues peuvent créer du ressac dans le port. Les plaisanciers doivent anticiper les conditions météo et ne pas confondre hauteur d'eau et état de la mer.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 80 : rochers de Pen Bron accessibles — bigorneaux et moules</li>
        <li>Coefficient ≥ 70 : coques sur la Grande Plage côté nord</li>
        <li>Criée ouverte aux visiteurs le matin — renseignez-vous en mairie pour les horaires</li>
        <li>Port VHF canal 9 pour les plaisanciers en escale</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-piriac-sur-mer": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à Piriac-sur-Mer — Village de granit et presqu'île</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le village le plus pittoresque de Loire-Atlantique</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Piriac-sur-Mer est un <strong>village de pêcheurs du XVIIe siècle</strong> préservé, avec ses ruelles pavées, ses maisons de granit fleuri et son port naturel encaissé. Le marnage de vive-eau atteint environ <strong>4,8 m</strong>. Zola y séjourna à la fin du XIXe siècle et en fit le cadre de plusieurs de ses romans. Le village attire aujourd'hui artistes et amateurs de côte sauvage, loin de l'agitation des grandes stations balnéaires.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Pêche à pied : les rochers de la Pointe du Castelli</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>Pointe du Castelli</strong> et les rochers qui l'entourent sont le meilleur spot de pêche à pied de Piriac. Coefficient minimum conseillé : <strong>82</strong>. On y trouve <strong>bigorneaux, huîtres sauvages, crabes étrilles et patelles</strong>. Les rochers sont accessibles à pied depuis le port en longeant la côte vers le nord-ouest. La zone est peu connue des touristes — arrivez tôt par grandes marées d'été. L'accès par mer est également possible en kayak.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le sentier côtier GR34</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le <strong>GR34</strong> (sentier des douaniers) passe par Piriac et longe la côte sauvage jusqu'à La Turballe au sud et Mesquer au nord. C'est l'un des plus beaux tronçons du GR34 en Loire-Atlantique, avec des panoramas sur les falaises, les îlots et l'Atlantique. À marée basse, le sentier permet d'accéder à des plages et criques cachées inaccessibles à marée haute. Comptez 2h30 pour la boucle Piriac–La Turballe via le GR34.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Port et plaisance</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le port de Piriac est un port naturel semi-abrité, avec des places visiteurs limitées. L'<strong>accès se fait par l'anse nord</strong>, balisée par une tourelle verte. Le tirant d'eau maximum recommandé est de 1,5 m à mi-marée — à basse mer en morte-eau, le port peut être quasiment à sec. Excellent abri en cas de coup de vent de secteur est à nord.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 82 : Pointe du Castelli accessible — huîtres et étrilles</li>
        <li>Marché du port le dimanche matin en saison (producteurs locaux)</li>
        <li>Stationnement : parking payant en saison au-dessus du port</li>
        <li>GR34 : chaussures de marche conseillées, certains passages sont boueux</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-pornic": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à Pornic — Château médiéval et côte de Jade</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La cité médiévale de la Côte de Jade</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Pornic est dominé par son <strong>château médiéval du XIVe siècle</strong> (propriété privée, visible de l'extérieur) qui surplombe le port pittoresque. La Côte de Jade, entre Loire et Vendée, offre un littoral varié : criques rocheuses, plages de sable, falaises de schiste. Le marnage de vive-eau est d'environ <strong>5 m</strong>. Pornic est la commune la plus peuplée du sud-est de la presqu'île de Retz et un centre touristique actif toute l'année.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Pêche à pied : les zones de La Noëveillard et Pindy</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Les deux meilleurs spots de pêche à pied à Pornic sont la <strong>plage de La Noëveillard</strong> (coques et palourdes dans le sable, coefficient ≥ 75) et les rochers de <strong>Pindy</strong> vers la pointe Saint-Gildas (huîtres sauvages et bigorneaux, coefficient ≥ 85). La crique de <strong>Feuré</strong>, accessible à pied depuis le bourg, recèle également de belles colonies de bigorneaux sur ses rochers de schiste bleu. Zone classée B — consultez le classement sanitaire avant chaque sortie.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Talasothérapie et thermalisme marin</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Pornic est l'une des premières stations de <strong>thalassothérapie de la côte atlantique</strong>. L'eau de mer pompée à marée montante est utilisée dans les soins. La qualité de l'eau, surveillée par l'ARS, dépend directement du coefficient de marée et des conditions météo : les grandes marées de vive-eau renouvellent les masses d'eau et améliorent la qualité bactériologique des zones de baignade.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Port de plaisance</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le port de Pornic compte <strong>900 anneaux</strong> dont des places visiteurs disponibles en escale. L'accès se fait par l'anse depuis le large — attention aux rochers de La Couronnée par vent de secteur est. VHF canal 9. Le port est accessible à tout état de marée pour les tirants d'eau inférieurs à 2 m.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 75 : coques à La Noëveillard — zone sableuse accessible à pied</li>
        <li>Coefficient ≥ 85 : rochers de Pindy et Feuré — huîtres sauvages</li>
        <li>Marché couvert de Pornic : produits de la mer frais tous les matins</li>
        <li>GR de Pays côtier accessible depuis le port : 15 km de sentier côtier</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-saint-brevin-les-pins": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à Saint-Brevin-les-Pins — Face au pont de Saint-Nazaire</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La rive sud de l'estuaire de la Loire</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Saint-Brevin-les-Pins est situé sur la <strong>rive sud de l'estuaire de la Loire</strong>, face à Saint-Nazaire et reliée par le <strong>pont de Saint-Nazaire</strong> (premier pont suspendu de France lors de sa construction en 1975). Le marnage de vive-eau atteint environ <strong>5 m</strong>, légèrement amplifié par l'effet d'entonnoir de l'estuaire. La commune cumule 8 km de plages, une forêt de pins et un front de mer animé.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Pêche à pied côté estuaire</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La rive de l'estuaire côté Saint-Brevin offre de bonnes conditions de pêche à pied par coefficient ≥ 80. Les <strong>vasières de l'estuaire</strong> en amont de la pointe de Mindin sont riches en <strong>coques et vers de vase</strong> (utilisés comme appâts). L'estran sablo-vaseux découvert en basse mer s'étend sur plusieurs centaines de mètres par grandes vives-eaux. Attention : les courants dans l'estuaire sont forts — ne jamais s'aventurer au-delà des zones rocheuses accessibles à pied.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Les plages océaniques</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Côté Atlantique, les plages de Saint-Brevin s'étirent vers le sud sur 8 km. La <strong>plage de la Courance</strong> et la <strong>plage du Pointeau</strong> sont les plus fréquentées. Ces plages sableuses offrent de bonnes conditions de récolte de coques et palourdes à basse mer (coefficient ≥ 72). La forêt de pins des Retz, plantée au XIXe siècle, longe les plages et constitue un cadre naturel exceptionnel pour des promenades entre deux marées.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le pont de Saint-Nazaire et les courants</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le <strong>pont de Saint-Nazaire</strong> (3,4 km) est l'un des repères visuels incontournables de l'estuaire. En dessous du pont, les courants atteignent 3 à 5 nœuds en vive-eau — la navigation est autorisée mais nécessite vigilance et VHF canal 14. Les piliers du pont sont balisés. La passe nord (côté Saint-Nazaire) est plus profonde et utilisée par les navires de commerce.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 80 : vasières de la pointe de Mindin accessibles (coques)</li>
        <li>Coefficient ≥ 72 : plages sud de Saint-Brevin (récolte de palourdes)</li>
        <li>Navigation sous le pont : VHF canal 14, priorité aux navires de commerce</li>
        <li>Forêt des Retz : sentiers balisés, accès gratuit, parking gratuit hors saison</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-prefailles": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à Préfailles — La côte sauvage du pays de Retz</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La commune aux panoramas atlantiques</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Préfailles est une commune littorale du pays de Retz offrant certains des <strong>panoramas les plus sauvages de Loire-Atlantique</strong>. Les falaises de schiste plongent dans l'Atlantique, découpées par des criques et anses accessibles à marée basse. Le marnage de vive-eau est d'environ <strong>5 m</strong>. Hors saison estivale, les plages et chemins côtiers sont quasi-déserts — une solitude que les habitués protègent jalousement.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La Pointe Saint-Gildas : spot de pêche exceptionnel</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>Pointe Saint-Gildas</strong>, à l'extrémité sud de la commune de Préfailles, est l'un des spots de pêche à pied les moins fréquentés et les plus riches de Loire-Atlantique. Les rochers exposés par les grandes vives-eaux (coefficient ≥ 90) abritent des <strong>bigorneaux, moules de roche, patelles et étrilles</strong> d'une abondance rare. La pointe marque l'entrée de l'estuaire de la Loire — les courants y sont forts, restez sur les zones rocheuses et évitez de s'aventurer dans l'eau.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Les criques de Préfailles</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Entre le bourg de Préfailles et la Pointe Saint-Gildas, le sentier côtier longe plusieurs <strong>criques rocheuses</strong> accessibles uniquement à marée basse par coefficient ≥ 85 : la crique de l'Écluse, l'anse de Fontaine, et les rochers du Bec. Ces zones peu connues des touristes sont de véritables paradis pour la pêche à pied — arrivez tôt, avant 7h, pour profiter de la basse mer en solitaire et de la lumière rasante sur les rochers.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Surf et body-board</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>plage de La Comète</strong>, au cœur du bourg de Préfailles, est un spot de surf apprécié par les locaux. La houle atlantique y arrive sans obstacle, produisant des vagues régulières par vent de secteur ouest. Les conditions optimales se présentent par coefficient faible (courant limité) et houle de 1 à 2 m. Plusieurs surfeurs de Saint-Nazaire et Pornic fréquentent ce spot discret toute l'année.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 90 : Pointe Saint-Gildas — bigorneaux et étrilles exceptionnels</li>
        <li>Coefficient ≥ 85 : criques entre Préfailles et la Pointe — zones sauvages peu fréquentées</li>
        <li>Courants forts à la Pointe Saint-Gildas : restez sur les rochers, ne pas entrer dans l'eau</li>
        <li>Sentier côtier balisé : 5 km aller-retour Préfailles — Pointe Saint-Gildas</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-paimboeuf": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à Paimbœuf — L'estuaire de la Loire en profondeur</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le port fluvio-maritime de l'estuaire</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Paimbœuf est une ville-port au cœur de l'estuaire de la Loire, à <strong>42 km à l'intérieur des terres depuis l'embouchure</strong>. La marée remonte jusqu'à Paimbœuf et même au-delà — à Cordemais (55 km), la marée est encore sensible. Le marnage de vive-eau à Paimbœuf atteint environ <strong>5,4 m</strong>, légèrement supérieur à Saint-Nazaire en raison de l'effet d'entonnoir de l'estuaire. La Loire apporte son propre débit fluvial, rendant les marées plus complexes à prédire qu'en pleine mer.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Les vasières de l'estuaire</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Les <strong>vasières estuariennes</strong> autour de Paimbœuf sont d'une richesse écologique exceptionnelle. À basse mer, plusieurs centaines d'hectares de vase se découvrent, habitat critique pour les limicoles (bécasseaux, chevaliers, barges) en migration. Ces zones sont classées <strong>Natura 2000 et ZNIEFF</strong> — la pêche à pied y est réglementée. Les espèces présentes incluent anguilles, mulets et crabes verts. Consultez la DDTM 44 pour les zones autorisées.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Histoire maritime de Paimbœuf</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Paimbœuf était au XVIIIe siècle le <strong>port d'armement de Nantes</strong> pour la traite négrière — les grands navires ne pouvant remonter jusqu'à Nantes. Le <strong>musée de la Marine de Loire</strong> retrace cette histoire maritime méconnue. Les quais, en partie restaurés, témoignent de cette époque avec leurs entrepôts et magasins à sel. La Loire à Paimbœuf mesure environ 1,5 km de large — la traversée en ferry vers le nord (Couëron) donne une perspective unique sur l'estuaire.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Spécificités des marées en estuaire</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">À Paimbœuf, l'<strong>heure de pleine mer est décalée de 30 à 45 minutes</strong> par rapport à Saint-Nazaire (port de référence). Ce décalage augmente vers l'intérieur : à Nantes, il atteint 2h30 à 3h. La hauteur réelle peut s'écarter de 30 à 80 cm par rapport aux prévisions harmoniques en cas de crue de la Loire ou de fort vent d'ouest — utilisez toujours les données de ce site comme référence et non comme certitude absolue.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Décalage horaire : pleine mer environ 40 min après Saint-Nazaire</li>
        <li>Vasières Natura 2000 : zones protégées, pêche réglementée — se renseigner à la mairie</li>
        <li>Musée de la Marine de Loire : ouvert en saison, renseignez-vous pour les horaires</li>
        <li>Crue de la Loire : peut faire varier le niveau de ±80 cm par rapport aux prévisions</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-saint-gildas": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à la Pointe Saint-Gildas — L'entrée sauvage de l'estuaire</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La pointe la plus exposée de Loire-Atlantique</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>Pointe Saint-Gildas</strong> marque l'entrée sud de l'estuaire de la Loire et constitue l'un des caps les plus exposés du littoral atlantique français. Le marnage de vive-eau y atteint <strong>5,1 m</strong>, mais c'est surtout la <strong>force des courants</strong> qui la caractérise : jusqu'à 5 nœuds en vive-eau dans l'axe de l'estuaire. La catastrophe du naufrage du Noirmoutier en 1931 (200 victimes) reste dans les mémoires locales — rappel permanent du respect que mérite ce cap.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Pêche à pied : les rochers de la Pointe</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Les rochers de la Pointe Saint-Gildas, découverts uniquement par les <strong>très grandes vives-eaux (coefficient ≥ 95)</strong>, constituent l'un des spots de pêche à pied les plus exigeants et les plus riches du département. <strong>Bigorneaux géants, tourteaux, homards (très rares mais présents), étrilles</strong> — les espèces affectionnent ces zones exposées à pleine mer. La règle est stricte : ne jamais aller dans l'eau, rester sur les rochers, et connaître précisément l'heure de remontée de la marée.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Sémaphore et signaux maritimes</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le <strong>sémaphore de la Pointe Saint-Gildas</strong>, géré par la Marine nationale, surveille en permanence le trafic maritime à l'entrée de l'estuaire. Il diffuse les bulletins météo marins VHF sur le canal 79. Les conditions observées en temps réel depuis le sémaphore (état de la mer, visibilité, vent) complètent utilement les prévisions météo pour les sorties en mer depuis Pornic, Préfailles ou Saint-Brevin.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Mémorial du Noirmoutier</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>chapelle commémorative</strong> du Noirmoutier (naufrage du 14 juin 1931) se dresse près de la pointe. Le paquebot transportant 400 passagers s'était échoué par temps de brume sur la Barre de Saint-Nazaire, alors que la marée montante rendait l'accès impossible aux secours. Ce drame a conduit à l'amélioration du balisage de l'estuaire et à la modernisation des CROSS. Une plaque rappelle les 200 victimes.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 95 UNIQUEMENT pour les rochers de la Pointe — courants extrêmes sinon</li>
        <li>Ne jamais entrer dans l'eau — courants 5 nœuds en vive-eau</li>
        <li>Sémaphore VHF 79 : bulletins météo marins en temps réel</li>
        <li>Accès : parking Pointe Saint-Gildas (commune de Préfailles), sentier côtier 20 min</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-batz-sur-mer": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées à Batz-sur-Mer — Entre marais salants et Côte Sauvage</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La presqu'île guérandaise, entre deux espaces</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Batz-sur-Mer est une commune unique, coincée entre les <strong>marais salants de Guérande côté nord</strong> et la <strong>Côte Sauvage atlantique côté sud</strong>. Ce contraste exceptionnel — eau douce des marais et vagues de l'Atlantique — à moins de 2 km l'un de l'autre, en fait un des paysages les plus singuliers de Loire-Atlantique. Le marnage de vive-eau est d'environ <strong>4,9 m</strong>.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">La plage de La Govelle — spot polyvalent par excellence</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La <strong>plage de La Govelle</strong> est le spot le plus populaire de Batz-sur-Mer. Côté plage, la vague de shore break attire les bodysurfers et skimboarders. Côté estran, la zone sablo-rocheuse à marée basse (coefficient ≥ 72) livre <strong>coques, palourdes et bigorneaux</strong> en abondance. Le terrain est plat et accessible — idéal pour les familles avec enfants ou pour les débutants en pêche à pied. Arrivez 1h avant la basse mer pour avoir le temps de chercher.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Les marais salants et les paludiers</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Les marais salants de Batz-sur-Mer font partie du <strong>bassin de Guérande</strong>, le plus grand marais salant artisanal de France. Les <strong>paludiers</strong> récoltent la fleur de sel et le sel gris de mai à septembre, en fonction des conditions météo et du niveau d'eau dans les œillets (bassins d'évaporation). Le <strong>musée des Marais Salants</strong> à Batz retrace l'histoire de cette activité millénaire. Les marées influencent le niveau des étiers (chenaux) qui alimentent les marais via des écluses.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Clocher-phare de Batz</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le clocher de <strong>Saint-Guénolé</strong> de Batz-sur-Mer (56 m) est l'un des rares clochers-phares de France — il servait de repère de navigation aux pêcheurs et marins qui longeaient la côte. Du sommet (182 marches), la vue s'étend sur les marais, la Côte Sauvage, le Croisic et, par temps clair, jusqu'à l'île de Noirmoutier.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 72 : La Govelle — coques et palourdes, idéal débutants</li>
        <li>Coefficient ≥ 85 : Côte Sauvage vers Le Croisic — huîtres sauvages</li>
        <li>Musée des Marais Salants : ouvert d'avril à septembre, visite recommandée</li>
        <li>Clocher-phare : ouvert en juillet-août, accès payant</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",

"marees-le-pouliguen": """
      <h2 style="font-size:1rem;font-weight:800;color:var(--blue-d);margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--blue-l)">Marées au Pouliguen — Port de plaisance entre baie et rivière</h2>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le port jumeau de La Baule</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le Pouliguen est la commune jumelle de La Baule, partagée par l'estuaire du <strong>canal du Pouliguen</strong> (ancienne rivière canalisée). Le port de plaisance du Pouliguen compte environ <strong>800 anneaux</strong> et constitue le point de départ de nombreuses sorties en mer vers la baie de La Baule, le Croisic et les côtes vendéennes. Le marnage de vive-eau est d'environ <strong>4,8 m</strong>. La ville, plus animée que Batz-sur-Mer tout en étant moins touristique que La Baule, offre un bel équilibre entre authenticité et services.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Pêche à pied côté baie</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">La zone sableuse à l'ouest du Pouliguen, vers <strong>La Baule-les-Pins</strong>, offre de bonnes conditions de récolte de coques et palourdes par coefficient ≥ 72. Les rochers de la <strong>Pointe du Bec</strong>, à la limite ouest du Pouliguen, décèlent par coefficients élevés (≥ 85) des bigorneaux et quelques crabes. Cette zone est le reflet de l'estran entre Le Pouliguen et Le Croisic — moins riche que la Côte Sauvage mais plus accessible aux familles.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Accès au port et navigation</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">L'accès au port du Pouliguen se fait par le <strong>chenal de La Baule</strong>, balisé par des cardinales et des bouées latérales. Le chenal présente un tirant d'eau minimum de 1,5 m à basse mer de vive-eau — vérifiez les horaires avant tout mouvement. La capitainerie est joignable sur VHF canal 9. Les visiteurs trouvent facilement une place en escale de mai à septembre moyennant réservation en haute saison.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Le marché du Pouliguen</h3>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.75;margin-bottom:.7rem">Le marché du Pouliguen (mardi et vendredi matin) est réputé pour ses <strong>poissonniers qui vendent les arrivages du jour</strong> de La Turballe et Le Croisic. C'est l'occasion d'acheter bar, dorade, turbot et sardines à des prix de criée. Les coquillages vendus proviennent des producteurs locaux de la baie de Bourgneuf — palourdes, huîtres creuses et moules de bouchot.</p>

      <h3 style="font-size:.88rem;font-weight:700;color:var(--blue);margin:.8rem 0 .4rem">Conseils pratiques</h3>
      <ul style="font-size:.82rem;color:var(--text-m);line-height:1.75;padding-left:1.3rem;margin-bottom:.5rem">
        <li>Coefficient ≥ 72 : côté La Baule-les-Pins — coques et palourdes</li>
        <li>Coefficient ≥ 85 : Pointe du Bec — bigorneaux et quelques crabes</li>
        <li>Port VHF canal 9 — réservation conseillée en juillet-août</li>
        <li>Marché mardi et vendredi matin : poissons frais à prix de criée</li>
        <li>Urgence en mer : <strong>CROSS Étel — composez le 196</strong></li>
      </ul>
""",
}

# ─── FONCTIONS DE TRAITEMENT ─────────────────────────────────────────────────

def add_adsense_to_head(html):
    """Ajoute le script AdSense dans le <head> si pas déjà présent."""
    if 'pagead2.googlesyndication.com' in html:
        return html  # déjà présent
    # Insérer avant </head>
    return html.replace('</head>', ADSENSE_SCRIPT + '\n</head>', 1)

def remove_fake_ad_slots(html):
    """Supprime les blocs de fausses publicités (ad-slot)."""
    # Supprime la div ad-top entière
    html = re.sub(
        r'\n?<div class="ad-top">\s*<div class="ad-slot[^"]*">[^<]*</div>\s*</div>\n?',
        '\n',
        html,
        flags=re.DOTALL
    )
    # Supprime les ad-slot solitaires (rectangles, banners)
    html = re.sub(
        r'\n?\s*<div class="ad-slot[^"]*">\s*(?:Espace publicitaire[^<]*|Google AdSense[^<]*)\s*</div>\n?',
        '\n',
        html,
        flags=re.DOTALL
    )
    # Supprime les conteneurs ad-slot avec texte sur plusieurs lignes
    html = re.sub(
        r'\n?\s*<div class="ad-slot[^"]*">\s*\n\s*(?:Espace publicitaire|Google AdSense)[^\n]*\n\s*</div>\n?',
        '\n',
        html,
        flags=re.DOTALL
    )
    return html

def remove_broken_ins_adsense(html):
    """Supprime les <ins class='adsbygoogle'> avec data-ad-slot='AUTO' invalide."""
    html = re.sub(
        r'\n?\s*<!-- AdSense[^>]*-->.*?<script>\(adsbygoogle[^<]*</script>\n?',
        '\n',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'\n?\s*<div[^>]*margin[^>]*>\s*<span[^>]*>Publicité</span>\s*<ins class="adsbygoogle"[^>]*>.*?</script>\s*</div>\n?',
        '\n',
        html,
        flags=re.DOTALL
    )
    # Supprime aussi les <ins> seuls avec AUTO
    html = re.sub(
        r'\n?\s*<ins class="adsbygoogle"[^>]*data-ad-slot="AUTO"[^>]*>.*?<script>[^<]*</script>\n?',
        '\n',
        html,
        flags=re.DOTALL
    )
    return html

def replace_editorial_section(html, port_key):
    """Remplace la section éditoriale existante par le contenu enrichi."""
    if port_key not in EDITORIAL:
        return html

    new_content = EDITORIAL[port_key]

    # Cherche le bloc éditorial existant et le remplace
    # Pattern : div avec h2 "tout ce qu'il faut savoir" ou similaire
    pattern = r'(<div style="background:var\(--white\);border[^>]*>\s*<h2[^>]*>[^<]*(?:tout ce qu\'il faut savoir|Marées à)[^<]*</h2>)(.*?)(</div>\s*\n\s*<!-- Liens vers)'

    replacement = r'<div style="background:var(--white);border:1px solid var(--border);border-radius:12px;padding:1.4rem;box-shadow:0 2px 8px rgba(0,0,0,.07)">' + new_content + r'</div>\n    <!-- Liens vers'

    new_html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    if new_html == html:
        # Si pattern non trouvé, cherche une autre structure
        pattern2 = r'(<!-- Bloc editorial[^>]*-->\s*<div[^>]*>)(.*?)(</div>\s*\n\s*<!-- Liens vers)'
        replacement2 = r'    <!-- Bloc editorial enrichi -->\n    <div style="background:var(--white);border:1px solid var(--border);border-radius:12px;padding:1.4rem;box-shadow:0 2px 8px rgba(0,0,0,.07)">' + new_content + r'</div>\n    <!-- Liens vers'
        new_html = re.sub(pattern2, replacement2, html, flags=re.DOTALL)

    return new_html

def process_city_page(filepath, port_key):
    """Applique toutes les corrections à une page ville."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    html = add_adsense_to_head(html)
    html = remove_fake_ad_slots(html)
    html = remove_broken_ins_adsense(html)
    html = replace_editorial_section(html, port_key)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✅ Corrigé : {port_key}")
        return True
    else:
        print(f"  ⚠️  Aucun changement : {port_key}")
        return False

# ─── PAGES À TRAITER ─────────────────────────────────────────────────────────
CITY_PAGES = [
    "marees-saint-nazaire",
    "marees-le-croisic",
    "marees-la-baule",
    "marees-la-turballe",
    "marees-piriac-sur-mer",
    "marees-pornic",
    "marees-saint-brevin-les-pins",
    "marees-prefailles",
    "marees-paimboeuf",
    "marees-saint-gildas",
    "marees-batz-sur-mer",
    "marees-le-pouliguen",
]

# ─── EXÉCUTION ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🔧 Correction AdSense — Pages villes de marees-loireatlantique.fr")
    print("=" * 60)

    modified = 0
    for port_key in CITY_PAGES:
        filepath = os.path.join(BASE, port_key, "index.html")
        if os.path.exists(filepath):
            if process_city_page(filepath, port_key):
                modified += 1
        else:
            print(f"  ❌ Fichier introuvable : {port_key}/index.html")

    print(f"\n✅ {modified}/{len(CITY_PAGES)} pages corrigées")
    print("\nÉtapes suivantes :")
    print("  1. git add -A && git commit -m 'fix: corrections AdSense pages villes'")
    print("  2. git push origin main")
    print("  3. Attendre le déploiement Netlify")
    print("  4. Retourner sur AdSense > Demander un examen\n")

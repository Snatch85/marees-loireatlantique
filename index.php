<?php
/**
 * MaréesLive v5.0.0 - Site de marées moderne et immersif
 * Design refait avec cards modernes et données corrigées
 */
define('SITE_NAME', 'MaréesLive');
define('WORLDTIDES_KEY', '1843bfee-0b42-463c-8841-7c94a23bb98a');
$JOURS = ['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'];
$MOIS = ['jan','fév','mar','avr','mai','juin','juil','août','sep','oct','nov','déc'];

$PORTS = [
    'le-croisic' => ['name'=>'Le Croisic','region'=>'Loire-Atlantique','icon'=>'🌊','lat'=>47.2989,'lon'=>-2.5128,'range_low'=>1.2,'range_high'=>8.5,'desc'=>'Port pittoresque','wind_base'=>12,'wind_dir'=>'NO','sea_state'=>'Agitée'],
    'la-turballe' => ['name'=>'La Turballe','region'=>'Loire-Atlantique','icon'=>'⚓','lat'=>47.3467,'lon'=>-2.5097,'range_low'=>1.1,'range_high'=>8.2,'desc'=>'Port de pêche','wind_base'=>15,'wind_dir'=>'O','sea_state'=>'Formée'],
    'la-baule' => ['name'=>'La Baule','region'=>'Loire-Atlantique','icon'=>'🏖️','lat'=>47.2854,'lon'=>-2.3967,'range_low'=>1.3,'range_high'=>8.8,'desc'=>'Station balnéaire','wind_base'=>10,'wind_dir'=>'SO','sea_state'=>'Peu agitée'],
    'pornichet' => ['name'=>'Pornichet','region'=>'Loire-Atlantique','icon'=>'🏝️','lat'=>47.2628,'lon'=>-2.3408,'range_low'=>1.4,'range_high'=>9.1,'desc'=>'Plage de sable fin','wind_base'=>8,'wind_dir'=>'S','sea_state'=>'Belle'],
    'saint-nazaire' => ['name'=>'Saint-Nazaire','region'=>'Loire-Atlantique','icon'=>'🚢','lat'=>47.2736,'lon'=>-2.2137,'range_low'=>1.5,'range_high'=>9.5,'desc'=>'Port maritime','wind_base'=>18,'wind_dir'=>'NO','sea_state'=>'Agitée'],
    'saint-brevin-les-pins' => ['name'=>'Saint-Brevin-les-Pins','region'=>'Loire-Atlantique','icon'=>'🌳','lat'=>47.2431,'lon'=>-2.1681,'range_low'=>1.6,'range_high'=>9.8,'desc'=>'Vue sur estuaire','wind_base'=>14,'wind_dir'=>'O','sea_state'=>'Formée'],
    'pornic' => ['name'=>'Pornic','region'=>'Loire-Atlantique','icon'=>'🌊','lat'=>47.1128,'lon'=>-2.1008,'range_low'=>1.7,'range_high'=>10.2,'desc'=>'Port traditionnel','wind_base'=>11,'wind_dir'=>'SO','sea_state'=>'Peu agitée'],
    'prefailles' => ['name'=>'Préfailles','region'=>'Loire-Atlantique','icon'=>'🌊','lat'=>47.1389,'lon'=>-2.2131,'range_low'=>1.8,'range_high'=>10.5,'desc'=>'Port de pêche','wind_base'=>13,'wind_dir'=>'O','sea_state'=>'Agitée'],
    'piriac-sur-mer' => ['name'=>'Piriac-sur-Mer','region'=>'Loire-Atlantique','icon'=>'🌊','lat'=>47.3797,'lon'=>-2.5444,'range_low'=>1.9,'range_high'=>10.8,'desc'=>'Vue sur estuaire','wind_base'=>16,'wind_dir'=>'NO','sea_state'=>'Formée'],
];

$port_key = $_GET['port'] ?? 'le-croisic';
if (!array_key_exists($port_key, $PORTS)) $port_key = 'le-croisic';
$port = $PORTS[$port_key];
function esc($s) { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }

$today_ts = mktime(0,0,0);

// Création du dossier cache s'il n'existe pas
if (!file_exists(__DIR__ . '/cache')) {
    mkdir(__DIR__ . '/cache', 0755, true);
}

/**
 * Récupère les données de marées depuis l'API WorldTides
 * @param float $lat Latitude du port
 * @param float $lon Longitude du port
 * @param string $portKey Clé du port pour le nom du fichier cache
 * @return array Données de marées ou tableau avec erreur
 */
function getTides($lat, $lon, $portKey) {
    // Nom du fichier de cache basé sur la clé du port (ex: cache/le-croisic.json)
    $cache_file = __DIR__ . '/cache/' . $portKey . '.json';
    
    // Vérifier si le cache existe et est valide (12h = 43200 secondes)
    if (file_exists($cache_file)) {
        $cache_age = time() - filemtime($cache_file);
        if ($cache_age < 43200) {
            $cached_data = json_decode(file_get_contents($cache_file), true);
            if ($cached_data && isset($cached_data['extremes'])) {
                return $cached_data;
            }
        }
    }
    
    // Appel à l'API WorldTides
    $url = "https://www.worldtides.info/api/v3?extremes&heights&date=today&days=2&lat={$lat}&lon={$lon}&key=" . WORLDTIDES_KEY;
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curl_error = curl_error($ch);
    curl_close($ch);
    
    // Gestion des erreurs
    if ($response === false || $curl_error) {
        return ['error' => 'Erreur de connexion à l\'API WorldTides: ' . $curl_error];
    }
    
    $data = json_decode($response, true);
    
    if ($http_code === 401 || (isset($data['error']) && stripos($data['error'], 'invalid key') !== false)) {
        return ['error' => 'Clé API WorldTides invalide'];
    }
    
    if ($http_code !== 200 || !isset($data['extremes'])) {
        $error_msg = $data['error'] ?? 'Données de marées non disponibles';
        return ['error' => 'Erreur API WorldTides: ' . $error_msg . ' (HTTP ' . $http_code . ')'];
    }
    
    // Sauvegarder dans le cache
    file_put_contents($cache_file, json_encode($data, JSON_PRETTY_PRINT));
    
    return $data;
}

// Récupération des marées réelles depuis l'API
$tides_data = getTides($port['lat'], $port['lon'], $port_key);
$tides_error = null;
$next_tides = [];

if (isset($tides_data['error'])) {
    $tides_error = $tides_data['error'];
    // Fallback sur les données simulées en cas d'erreur
    $next_tides = getNextTides(time(), $port, 6);
} else {
    // Conversion des données API en format utilisable
    foreach ($tides_data['extremes'] as $extreme) {
        $type = ($extreme['type'] === 'high') ? 'high' : 'low';
        $direction = ($type === 'high') ? '🔺' : '🔻';
        
        // Conversion du timestamp en heure locale française
        $ts = $extreme['time'];
        $time_fr = date('H:i', $ts);
        
        $next_tides[] = [
            'ts' => $ts,
            'time' => $time_fr,
            'height' => round($extreme['height'], 2),
            'type' => $type,
            'direction' => $direction
        ];
    }
    
    // Trier par timestamp et prendre les 6 prochaines
    usort($next_tides, function($a, $b) {
        return $a['ts'] - $b['ts'];
    });
    
    // Filtrer pour ne garder que les marées futures et les 6 prochaines
    $now = time();
    $future_tides = array_filter($next_tides, function($tide) use ($now) {
        return $tide['ts'] >= $now - 3600; // Inclure marées jusqu'à 1h dans le passé
    });
    $next_tides = array_slice(array_values($future_tides), 0, 6);
}

// Calcul des marées - affichage des 6 prochaines marées hautes et basses (fallback)
function getNextTides($start_ts, $p, $count = 6) {
    $tides = [];
    $T = 44700; // période en secondes (~12h25)
    $mid = ($p['range_low'] + $p['range_high']) / 2;
    $amp = ($p['range_high'] - $p['range_low']) / 2;
    
    $current = $start_ts;
    $step = 60;
    
    $prev_height = $mid - $amp * cos(fmod($current, $T) / $T * 2 * M_PI);
    $going_up = null;
    
    while (count($tides) < $count && ($current - $start_ts) < 86400 * 2) {
        $current += $step;
        $phi = fmod($current, $T);
        if ($phi < 0) $phi += $T;
        $height = $mid - $amp * cos($phi / $T * 2 * M_PI);
        $up = ($height > $prev_height);
        
        if ($going_up !== null && $up !== $going_up) {
            $tide_ts = $current - $step;
            $tide_height = $mid - $amp * cos(fmod($tide_ts, $T) / $T * 2 * M_PI);
            $tides[] = [
                'ts' => $tide_ts,
                'time' => date('H:i', $tide_ts),
                'height' => round($tide_height, 2),
                'type' => $going_up ? 'high' : 'low',
                'direction' => $going_up ? '🔺' : '🔻'
            ];
        }
        
        $prev_height = $height;
        $going_up = $up;
    }
    
    return $tides;
}

function dayCoeff($day_start) {
    $synodic = 29.53 * 86400;
    $ref = mktime(0,0,0,1,6,2024);
    $phase = fmod($day_start - $ref, $synodic) / $synodic * 2 * M_PI;
    return (int)max(20, min(120, 70 + sin($phase) * 38));
}

function getCoeffClass($coeff) {
    if ($coeff >= 90) return 'high';
    if ($coeff >= 60) return 'medium';
    return 'low';
}

function getCoeffLabel($coeff) {
    if ($coeff >= 90) return 'Vives eaux';
    if ($coeff >= 60) return 'Coefficient fort';
    if ($coeff >= 40) return 'Coefficient moyen';
    return 'Mortes eaux';
}

$next_tides = getNextTides(time(), $port, 6);
$today_coeff = dayCoeff($today_ts);
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title><?=esc(SITE_NAME)?> - Marées <?=esc($port['name'])?></title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
    --ocean-dark:#0a1628;
    --ocean-navy:#0d1f3d;
    --ocean-blue:#0066cc;
    --ocean-light:#1a3a5c;
    --off-white:#f0f4f8;
    --text-primary:#ffffff;
    --text-secondary:#b8c5d6;
    --accent:#0099ff;
    --accent-glow:rgba(0,153,255,0.4);
    --success:#22c55e;
    --warning:#f59e0b;
    --danger:#ef4444;
    --card-bg:rgba(255,255,255,0.08);
    --card-border:rgba(255,255,255,0.12);
}
html{scroll-behavior:smooth}
body{
    font-family:'Poppins',system-ui,sans-serif;
    background:linear-gradient(180deg,var(--ocean-dark) 0%,var(--ocean-navy) 40%,var(--ocean-light) 100%);
    min-height:100vh;
    color:var(--text-primary);
    overflow-x:hidden;
}

/* HEADER AVEC IMAGE DE FOND OCEAN */
.ocean-header{
    position:relative;
    height:320px;
    overflow:hidden;
    display:flex;
    align-items:center;
    justify-content:center;
    background:linear-gradient(135deg,#0a1628 0%,#1a3a5c 100%);
}
.header-bg{
    position:absolute;
    top:0;left:0;width:100%;height:100%;
    background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 400'%3E%3Cdefs%3E%3ClinearGradient id='waveGrad' x1='0%25' y1='0%25' x2='0%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%230066cc;stop-opacity:0.3'/%3E%3Cstop offset='100%25' style='stop-color:%230099ff;stop-opacity:0.1'/%3E%3C/linearGradient%3E%3C/defs%3E%3Cpath d='M0,200 C150,280 300,120 450,200 C600,280 750,120 900,200 C1050,280 1200,120 1200,200 L1200,400 L0,400 Z' fill='url(%23waveGrad)'/%3E%3Cpath d='M0,250 C200,320 400,180 600,250 C800,320 1000,180 1200,250 L1200,400 L0,400 Z' fill='rgba(0,102,204,0.2)'/%3E%3C/svg%3E") center/cover no-repeat;
    opacity:0.6;
}
.header-overlay{
    position:absolute;
    top:0;left:0;width:100%;height:100%;
    background:radial-gradient(ellipse at center,transparent 0%,rgba(10,22,40,0.7) 100%);
}
.header-content{
    position:relative;
    z-index:10;
    text-align:center;
    padding:30px;
}

/* TITRE AVEC GLASSMORPHISM */
.site-title{
    font-size:3rem;
    font-weight:700;
    background:rgba(255,255,255,0.15);
    backdrop-filter:blur(20px);
    -webkit-backdrop-filter:blur(20px);
    padding:20px 40px;
    border-radius:20px;
    border:1px solid rgba(255,255,255,0.2);
    box-shadow:0 8px 32px rgba(0,0,0,0.3);
    display:inline-block;
    margin-bottom:15px;
    text-shadow:0 2px 10px rgba(0,0,0,0.3);
}
.port-info{
    font-size:1.1rem;
    color:var(--text-secondary);
    margin-bottom:20px;
}

/* BADGE COEFFICIENT COLORÉ */
.coeff-badge-large{
    display:inline-flex;
    align-items:center;
    gap:10px;
    padding:15px 30px;
    border-radius:50px;
    font-size:1.3rem;
    font-weight:700;
    box-shadow:0 4px 20px rgba(0,0,0,0.3);
    transition:all 0.3s ease;
}
.coeff-low{
    background:linear-gradient(135deg,var(--success),#16a34a);
    color:white;
}
.coeff-medium{
    background:linear-gradient(135deg,var(--warning),#d97706);
    color:white;
}
.coeff-high{
    background:linear-gradient(135deg,var(--danger),#dc2626);
    color:white;
}
.coeff-value{font-size:1.8rem}
.coeff-label{font-size:0.9rem;font-weight:500;opacity:0.9}

/* VAGUES ANIMÉES */
.waves-container{
    position:absolute;
    bottom:0;
    left:0;
    width:100%;
    height:80px;
    overflow:hidden;
    z-index:5;
}
.wave{
    position:absolute;
    bottom:0;
    left:0;
    width:200%;
    height:100%;
    background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 80'%3E%3Cpath d='M0,40 Q150,80 300,40 T600,40 T900,40 T1200,40 L1200,80 L0,80 Z' fill='rgba(0,153,255,0.4)'/%3E%3C/svg%3E");
    background-size:50% 100%;
    animation:waveMove 8s linear infinite;
}
.wave:nth-child(2){animation-duration:10s;opacity:0.6;bottom:5px}
.wave:nth-child(3){animation-duration:12s;opacity:0.3;bottom:10px}
@keyframes waveMove{
    0%{transform:translateX(0)}
    100%{transform:translateX(-50%)}
}

/* SELECTEUR DE PORT */
.port-selector{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    justify-content:center;
    margin-top:20px;
}
.port-btn{
    padding:10px 20px;
    background:var(--card-bg);
    border:1px solid var(--card-border);
    border-radius:25px;
    color:var(--text-primary);
    cursor:pointer;
    transition:all 0.3s ease;
    backdrop-filter:blur(10px);
    font-size:0.95rem;
    font-weight:500;
}
.port-btn:hover,.port-btn.active{
    background:var(--accent);
    border-color:var(--accent);
    box-shadow:0 0 25px var(--accent-glow);
    transform:translateY(-3px);
}

/* CONTAINER PRINCIPAL */
.main-container{
    max-width:1200px;
    margin:0 auto;
    padding:30px 20px;
    position:relative;
    z-index:10;
}

/* CARDS MODERNES */
.card{
    background:var(--card-bg);
    backdrop-filter:blur(20px);
    -webkit-backdrop-filter:blur(20px);
    border-radius:24px;
    border:1px solid var(--card-border);
    padding:30px;
    margin-bottom:30px;
    box-shadow:0 10px 40px rgba(0,0,0,0.3);
    animation:cardFadeIn 0.6s ease-out forwards;
    opacity:0;
    transform:translateY(30px);
}
.card:nth-child(1){animation-delay:0.1s}
.card:nth-child(2){animation-delay:0.2s}
.card:nth-child(3){animation-delay:0.3s}
.card:nth-child(4){animation-delay:0.4s}
@keyframes cardFadeIn{
    to{opacity:1;transform:translateY(0)}
}
.card-title{
    font-size:1.4rem;
    font-weight:600;
    margin-bottom:25px;
    display:flex;
    align-items:center;
    gap:12px;
    color:var(--text-primary);
}

/* CARDS MARÉES */
.tides-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
    gap:20px;
}
.tide-card{
    background:linear-gradient(135deg,rgba(0,102,204,0.15),rgba(0,153,255,0.08));
    border-radius:20px;
    padding:25px;
    border:1px solid rgba(0,153,255,0.2);
    display:flex;
    align-items:center;
    gap:20px;
    transition:all 0.3s ease;
    box-shadow:0 4px 15px rgba(0,0,0,0.2);
}
.tide-card:hover{
    transform:translateY(-5px);
    box-shadow:0 8px 25px rgba(0,153,255,0.3);
    border-color:var(--accent);
}
.tide-icon{
    font-size:3rem;
    width:70px;
    height:70px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:50%;
    background:rgba(255,255,255,0.1);
}
.tide-card.high .tide-icon{background:rgba(34,197,94,0.2)}
.tide-card.low .tide-icon{background:rgba(239,68,68,0.2)}
.tide-info{flex:1}
.tide-type{
    font-size:1.1rem;
    font-weight:600;
    margin-bottom:8px;
    color:var(--text-secondary);
}
.tide-time{
    font-size:1.8rem;
    font-weight:700;
    color:var(--text-primary);
}
.tide-height{
    font-size:1rem;
    color:var(--accent);
    font-weight:500;
    margin-top:5px;
}

/* SECTION MÉTÉO - CARDS SÉPARÉES */
.weather-section{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
    gap:20px;
}
.weather-card{
    background:linear-gradient(135deg,rgba(255,255,255,0.1),rgba(255,255,255,0.05));
    border-radius:20px;
    padding:25px;
    text-align:center;
    border:1px solid var(--card-border);
    transition:all 0.3s ease;
}
.weather-card:hover{
    transform:translateY(-5px);
    box-shadow:0 8px 25px rgba(0,0,0,0.3);
}
.weather-icon-large{
    font-size:3.5rem;
    margin-bottom:15px;
    display:block;
}
.weather-value{
    font-size:1.4rem;
    font-weight:700;
    color:var(--text-primary);
    margin-bottom:8px;
}
.weather-label{
    font-size:0.9rem;
    color:var(--text-secondary);
}

/* WIDGET MÉTÉO MARINE */
.marine-weather-widget{
    background:var(--card-bg);
    backdrop-filter:blur(20px);
    -webkit-backdrop-filter:blur(20px);
    border-radius:24px;
    border:1px solid var(--card-border);
    padding:25px 30px;
    margin-top:20px;
    box-shadow:0 10px 40px rgba(0,0,0,0.3);
    animation:cardFadeIn 0.6s ease-out forwards;
}
.marine-weather-title{
    font-size:1.1rem;
    font-weight:600;
    margin-bottom:20px;
    display:flex;
    align-items:center;
    gap:10px;
    color:var(--text-primary);
}
.marine-weather-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
    gap:15px;
}
.marine-weather-item{
    background:linear-gradient(135deg,rgba(0,102,204,0.15),rgba(0,153,255,0.08));
    border-radius:16px;
    padding:15px;
    border:1px solid rgba(0,153,255,0.2);
    display:flex;
    flex-direction:column;
    align-items:center;
    gap:8px;
    transition:all 0.3s ease;
}
.marine-weather-item:hover{
    transform:translateY(-3px);
    box-shadow:0 6px 20px rgba(0,153,255,0.25);
    border-color:var(--accent);
}
.marine-weather-icon{
    font-size:2rem;
}
.marine-weather-value{
    font-size:1.1rem;
    font-weight:700;
    color:var(--text-primary);
    text-align:center;
}
.marine-weather-label{
    font-size:0.8rem;
    color:var(--text-secondary);
    text-align:center;
}
.wind-arrow{
    display:inline-block;
    transition:transform 0.5s ease;
    font-size:1.2rem;
}
.wind-arrow.rotating{
    animation:windRotate 2s ease-in-out infinite;
}
@keyframes windRotate{
    0%,100%{transform:rotate(-10deg)}
    50%{transform:rotate(10deg)}
}
.weather-loading{
    text-align:center;
    padding:20px;
    color:var(--text-secondary);
}
.weather-error{
    background:rgba(239,68,68,0.2);
    border:1px solid rgba(239,68,68,0.4);
    border-radius:12px;
    padding:15px;
    color:#fca5a5;
    font-size:0.9rem;
    text-align:center;
}

/* RESPONSIVE */
@media(max-width:768px){
    .ocean-header{height:280px}
    .site-title{font-size:2rem;padding:15px 25px}
    .coeff-badge-large{padding:12px 20px;font-size:1.1rem}
    .coeff-value{font-size:1.5rem}
    .tides-grid{grid-template-columns:1fr}
    .weather-section{grid-template-columns:1fr}
    .card{padding:20px}
}
</style>
</head>
<body>
<header class="ocean-header">
    <div class="header-bg"></div>
    <div class="header-overlay"></div>
    <div class="header-content">
        <h1 class="site-title">🌊 <?=esc(SITE_NAME)?></h1>
        <p class="port-info"><?=esc($port['region'])?> • <?=esc($port['desc'])?></p>
        
        <!-- Badge coefficient -->
        <div class="coeff-badge-large coeff-<?=getCoeffClass($today_coeff)?>">
            <span class="coeff-value"><?=$today_coeff?></span>
            <span class="coeff-label"><?=getCoeffLabel($today_coeff)?></span>
        </div>
        
        <div class="port-selector">
            <?php foreach($PORTS as $key=>$p):?>
            <button class="port-btn <?=$key===$port_key?'active':''?>" onclick="window.location.href='?port=<?=esc($key)?>'">
                <?=esc($p['icon'])?> <?=esc($p['name'])?>
            </button>
            <?php endforeach;?>
        </div>
        
        <!-- Widget Météo Marine -->
        <div class="marine-weather-widget" id="marineWeatherWidget">
            <h3 class="marine-weather-title">🌊 Météo Marine - <?=esc($port['name'])?></h3>
            <div class="marine-weather-grid" id="marineWeatherContent">
                <div class="weather-loading">Chargement des données météo...</div>
            </div>
        </div>
    </div>
    <div class="waves-container">
        <div class="wave"></div>
        <div class="wave"></div>
        <div class="wave"></div>
    </div>
</header>

<main class="main-container">
    <!-- Section Marées -->
    <div class="card">
        <h2 class="card-title">🌊 Prochaines Marées</h2>
        <?php if ($tides_error): ?>
        <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <p style="color: #fca5a5; font-weight: 500;">⚠️ <?= esc($tides_error) ?></p>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 8px;">Affichage des données estimées.</p>
        </div>
        <?php endif; ?>
        <div class="tides-grid">
            <?php foreach($next_tides as $tide):?>
            <div class="tide-card <?=$tide['type']?>">
                <div class="tide-icon"><?=$tide['direction']?></div>
                <div class="tide-info">
                    <div class="tide-type"><?=$tide['type']==='high'?'Pleine Mer':'Basse Mer'?></div>
                    <div class="tide-time"><?=esc($tide['time'])?></div>
                    <div class="tide-height"><?=$tide['height']?> mètres</div>
                </div>
            </div>
            <?php endforeach;?>
        </div>
    </div>
    
    <!-- Section Météo Marine -->
    <div class="card">
        <h2 class="card-title">🌤️ Météo Marine</h2>
        <div class="weather-section">
            <div class="weather-card">
                <span class="weather-icon-large">💨</span>
                <div class="weather-value"><?=$port['wind_base']?> nœuds</div>
                <div class="weather-label">Force du vent</div>
            </div>
            <div class="weather-card">
                <span class="weather-icon-large">🧭</span>
                <div class="weather-value"><?=esc($port['wind_dir'])?></div>
                <div class="weather-label">Direction</div>
            </div>
            <div class="weather-card">
                <span class="weather-icon-large">🌊</span>
                <div class="weather-value"><?=esc($port['sea_state'])?></div>
                <div class="weather-label">État de la mer</div>
            </div>
        </div>
    </div>
</main>

<script>
// Animation au scroll pour les cards
const observerOptions = {threshold: 0.1, rootMargin: '0px 0px -50px 0px'};
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animationPlayState = 'running';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);
document.querySelectorAll('.card').forEach(card => observer.observe(card));

// Widget Météo Marine avec API Open-Meteo
const PORT_COORDS = <?=json_encode(array_map(fn($p) => ['lat' => $p['lat'], 'lon' => $p['lon']], $PORTS))?>;

async function fetchMarineWeather(lat, lon) {
    try {
        const url = `https://marine-api.open-meteo.com/v1/marine?latitude=${lat}&longitude=${lon}&current=temperature_2m,water_temperature,wave_height,wind_speed_10m,wind_direction_10m,weather_code&hourly=wind_direction_10m`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur API');
        return await response.json();
    } catch (error) {
        console.error('Erreur récupération météo:', error);
        return null;
    }
}

function getWindDirectionArrow(degrees) {
    const directions = [
        { min: 337.5, max: 360, label: 'N', arrow: '↑' },
        { min: 0, max: 22.5, label: 'N', arrow: '↑' },
        { min: 22.5, max: 67.5, label: 'NE', arrow: '↗' },
        { min: 67.5, max: 112.5, label: 'E', arrow: '→' },
        { min: 112.5, max: 157.5, label: 'SE', arrow: '↘' },
        { min: 157.5, max: 202.5, label: 'S', arrow: '↓' },
        { min: 202.5, max: 247.5, label: 'SO', arrow: '↙' },
        { min: 247.5, max: 292.5, label: 'O', arrow: '←' },
        { min: 292.5, max: 337.5, label: 'NO', arrow: '↖' }
    ];
    for (const dir of directions) {
        if (degrees >= dir.min && degrees < dir.max) {
            return dir;
        }
    }
    return { label: 'N', arrow: '↑' };
}

function getWeatherIcon(code) {
    const icons = {
        0: { icon: '☀️', text: 'Ensoleillé' },
        1: { icon: '🌤️', text: 'Peu nuageux' },
        2: { icon: '⛅', text: 'Nuageux' },
        3: { icon: '☁️', text: 'Couvert' },
        45: { icon: '🌫️', text: 'Brouillard' },
        48: { icon: '🌫️', text: 'Brouillard givrant' },
        51: { icon: '🌦️', text: 'Bruine légère' },
        53: { icon: '🌦️', text: 'Bruine modérée' },
        55: { icon: '🌧️', text: 'Bruine dense' },
        61: { icon: '🌧️', text: 'Pluie faible' },
        63: { icon: '🌧️', text: 'Pluie modérée' },
        65: { icon: '🌧️', text: 'Pluie forte' },
        80: { icon: '🌦️', text: 'Averses légères' },
        81: { icon: '🌧️', text: 'Averses modérées' },
        82: { icon: '⛈️', text: 'Averses violentes' },
        95: { icon: '⛈️', text: 'Orage' },
        96: { icon: '⛈️', text: 'Orage avec grêle' }
    };
    return icons[code] || { icon: '🌡️', text: 'Variable' };
}

function renderMarineWeather(data) {
    const container = document.getElementById('marineWeatherContent');
    if (!data || !data.current) {
        container.innerHTML = '<div class="weather-error">Données météo non disponibles</div>';
        return;
    }
    
    const current = data.current;
    const windDir = getWindDirectionArrow(current.wind_direction_10m);
    const weather = getWeatherIcon(current.weather_code);
    const windSpeedKmh = Math.round(current.wind_speed_10m * 3.6); // m/s to km/h
    
    container.innerHTML = `
        <div class="marine-weather-item">
            <span class="marine-weather-icon">🌡️</span>
            <div class="marine-weather-value">${Math.round(current.temperature_2m)}°C</div>
            <div class="marine-weather-label">Air</div>
        </div>
        <div class="marine-weather-item">
            <span class="marine-weather-icon">💧</span>
            <div class="marine-weather-value">${Math.round(current.water_temperature)}°C</div>
            <div class="marine-weather-label">Eau</div>
        </div>
        <div class="marine-weather-item">
            <span class="marine-weather-icon">💨</span>
            <div class="marine-weather-value">${windSpeedKmh} km/h ${windDir.label} <span class="wind-arrow rotating">${windDir.arrow}</span></div>
            <div class="marine-weather-label">Vent</div>
        </div>
        <div class="marine-weather-item">
            <span class="marine-weather-icon">🌊</span>
            <div class="marine-weather-value">${current.wave_height.toFixed(1)}m</div>
            <div class="marine-weather-label">Vagues</div>
        </div>
        <div class="marine-weather-item">
            <span class="marine-weather-icon">${weather.icon}</span>
            <div class="marine-weather-value">${weather.text}</div>
            <div class="marine-weather-label">Météo</div>
        </div>
    `;
}

// Charger la météo au chargement de la page
const currentPortKey = '<?=$port_key?>';
const coords = PORT_COORDS[currentPortKey];
if (coords) {
    fetchMarineWeather(coords.lat, coords.lon).then(renderMarineWeather);
}
</script>
</body>
</html>

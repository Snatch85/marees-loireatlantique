<?php
/**
 * MaréesLive v4.0.0 - Site de marées moderne et immersif
 */
define('SITE_NAME', 'MaréesLive');
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
function tideAt($ts, $p) {
    $T = 44700; $phi = fmod($ts + ($p['phase']??0)*60, $T); if ($phi < 0) $phi += $T;
    $mid = ($p['range_low']+$p['range_high'])/2; $amp = ($p['range_high']-$p['range_low'])/2;
    return round($mid - $amp*cos($phi/$T*2*M_PI), 2);
}
function dailyTides($day_start, $p) {
    $tides=[]; $prev=tideAt($day_start,$p); $going_up=null;
    for($i=1;$i<=1440;$i++) { $ts=$day_start+$i*60; $h=tideAt($ts,$p); $up=($h>$prev);
        if($going_up!==null && $up!==$going_up) { $te=$ts-30; $tides[]=['ts'=>$te,'time'=>date('H:i',$te),'height'=>tideAt($te,$p),'type'=>$going_up?'high':'low']; }
        $prev=$h; $going_up=$up;
    }
    return $tides;
}
function dayCoeff($day_start, $p) {
    $synodic=29.53*86400; $ref=mktime(0,0,0,1,6,2024); $phase=fmod($day_start-$ref,$synodic)/$synodic*2*M_PI;
    return (int)max(20,min(120,70+sin($phase)*38));
}

$days = [];
for($d=0;$d<7;$d++) {
    $ts=$today_ts+$d*86400; $dow=(int)date('w',$ts); $day_n=(int)date('j',$ts); $mon_n=(int)date('n',$ts)-1;
    $label = match($d) { 0=>"Aujourd'hui", 1=>'Demain', default=>$JOURS[$dow].' '.$day_n.' '.$MOIS[$mon_n] };
    $days[] = ['ts'=>$ts,'label'=>$label,'coeff'=>dayCoeff($ts,$port),'tides'=>dailyTides($ts,$port)];
}
$today_data = $days[0];
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title><?=esc(SITE_NAME)?> - Marées <?=esc($port['name'])?></title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--ocean-dark:#0a1628;--ocean-mid:#1e3a5f;--ocean-light:#4a90c2;--ocean-bright:#7ec8e3;--text-primary:#fff;--text-secondary:#b8d4e8;--accent:#06b6d4;--accent-glow:rgba(6,182,212,0.5)}
body{font-family:'Segoe UI',system-ui,sans-serif;background:linear-gradient(180deg,var(--ocean-dark) 0%,var(--ocean-mid) 50%,var(--ocean-light) 100%);min-height:100vh;color:var(--text-primary);overflow-x:hidden}
.parallax-header{position:relative;height:280px;overflow:hidden;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--ocean-dark),var(--ocean-mid))}
.parallax-bg{position:absolute;top:-20%;left:-10%;width:120%;height:140%;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 600'%3E%3Ccircle cx='600' cy='300' r='200' fill='rgba(126,200,227,0.1)'/%3E%3Ccircle cx='300' cy='200' r='100' fill='rgba(126,200,227,0.05)'/%3E%3C/svg%3E");transform:translateZ(0)}
.header-content{position:relative;z-index:2;text-align:center;padding:20px}
.site-title{font-size:2.8rem;font-weight:700;text-shadow:0 4px 20px rgba(0,0,0,0.3);background:linear-gradient(180deg,#fff,var(--ocean-bright));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
.port-selector{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:15px}
.port-btn{padding:8px 16px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:20px;color:var(--text-primary);cursor:pointer;transition:all 0.3s ease;backdrop-filter:blur(10px);font-size:0.9rem}
.port-btn:hover,.port-btn.active{background:var(--accent);border-color:var(--accent);box-shadow:0 0 20px var(--accent-glow);transform:translateY(-2px)}
.port-btn .fav-star{margin-left:5px;cursor:pointer}
.main-container{max-width:1200px;margin:0 auto;padding:20px;position:relative;z-index:2}
.card{background:rgba(255,255,255,0.08);backdrop-filter:blur(20px);border-radius:20px;border:1px solid rgba(255,255,255,0.1);padding:24px;margin-bottom:24px;box-shadow:0 8px 32px rgba(0,0,0,0.2)}
.card-title{font-size:1.3rem;margin-bottom:16px;display:flex;align-items:center;gap:10px}
.map-container{height:400px;border-radius:15px;overflow:hidden}
#tideMap{height:100%;width:100%}
.chart-container{position:relative;height:300px}
.tide-info-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}
.info-item{background:rgba(255,255,255,0.05);padding:16px;border-radius:12px;text-align:center}
.info-label{font-size:0.85rem;color:var(--text-secondary);margin-bottom:8px}
.info-value{font-size:1.5rem;font-weight:600;color:var(--accent)}
.countdown-container{display:flex;justify-content:space-around;flex-wrap:wrap;gap:20px}
.countdown-item{text-align:center;background:linear-gradient(135deg,rgba(6,182,212,0.2),rgba(6,182,212,0.05));padding:20px 30px;border-radius:15px;border:1px solid rgba(6,182,212,0.3)}
.countdown-label{font-size:0.9rem;color:var(--text-secondary);margin-bottom:8px}
.countdown-value{font-size:2rem;font-weight:700;color:var(--accent);font-family:monospace}
.weather-widget{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.weather-item{background:rgba(255,255,255,0.05);padding:14px;border-radius:10px;text-align:center}
.weather-icon{font-size:2rem;margin-bottom:8px}
.weather-value{font-size:1.1rem;font-weight:600}
.weather-label{font-size:0.75rem;color:var(--text-secondary)}
.tides-list{display:flex;flex-direction:column;gap:12px}
.tide-entry{display:flex;justify-content:space-between;align-items:center;padding:14px 18px;background:rgba(255,255,255,0.05);border-radius:10px;transition:transform 0.2s ease}
.tide-entry:hover{transform:translateX(5px);background:rgba(255,255,255,0.08)}
.tide-type{display:flex;align-items:center;gap:8px;font-weight:600}
.tide-type.high{color:#4ade80}.tide-type.low{color:#f87171}
.tide-time{font-size:1.3rem;font-weight:700}.tide-height{color:var(--text-secondary)}
.waves-animation{position:fixed;bottom:0;left:0;width:100%;height:120px;pointer-events:none;z-index:1}
.wave{position:absolute;bottom:0;left:0;width:200%;height:100%;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120'%3E%3Cpath d='M0,60 C150,120 350,0 600,60 C850,120 1050,0 1200,60 L1200,120 L0,120 Z' fill='rgba(126,200,227,0.3)'/%3E%3C/svg%3E");background-size:50% 100%;animation:wave 8s linear infinite}
.wave:nth-child(2){animation-duration:10s;opacity:0.5;bottom:5px}
.wave:nth-child(3){animation-duration:12s;opacity:0.3;bottom:10px}
@keyframes wave{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.mobile-swipe-hint{display:none;text-align:center;padding:10px;color:var(--text-secondary);font-size:0.85rem}
@media(max-width:768px){.parallax-header{height:220px}.site-title{font-size:2rem}.port-selector{max-height:100px;overflow-y:auto}.weather-widget{grid-template-columns:1fr}.countdown-item{padding:15px 20px}.countdown-value{font-size:1.5rem}.mobile-swipe-hint{display:block}.card{padding:16px}}
.coeff-badge{display:inline-block;padding:4px 12px;border-radius:15px;font-size:0.85rem;font-weight:600}
.coeff-vive{background:rgba(248,113,113,0.3);color:#f87171}.coeff-fort{background:rgba(251,191,36,0.3);color:#fbbf24}.coeff-moyen{background:rgba(59,130,246,0.3);color:#60a5fa}.coeff-morte{background:rgba(34,197,94,0.3);color:#4ade80}
</style>
</head>
<body>
<header class="parallax-header"><div class="parallax-bg" id="parallaxBg"></div>
<div class="header-content">
<h1 class="site-title">🌊 <?=esc(SITE_NAME)?></h1>
<p style="color:var(--text-secondary)"><?=esc($port['region'])?> • <?=esc($port['desc'])?></p>
<div class="port-selector" id="portSelector"><?php foreach($PORTS as $key=>$p):?>
<button class="port-btn <?=$key===$port_key?'active':''?>" data-port="<?=esc($key)?>"><?=esc($p['icon'])?> <?=esc($p['name'])?><span class="fav-star" data-port="<?=esc($key)?>"></span></button>
<?php endforeach;?></div>
<p class="mobile-swipe-hint">↔ Glissez pour changer de port</p>
</div></header>
<div class="waves-animation"><div class="wave"></div><div class="wave"></div><div class="wave"></div></div>
<main class="main-container">
<div class="card"><h2 class="card-title">🗺️ Carte Interactive</h2><div class="map-container"><div id="tideMap"></div></div></div>
<div class="card"><h2 class="card-title">⏱️ Prochaines Marées</h2>
<div class="countdown-container">
<div class="countdown-item"><div class="countdown-label">Pleine Mer</div><div class="countdown-value" id="highTideCountdown">--:--:--</div></div>
<div class="countdown-item"><div class="countdown-label">Basse Mer</div><div class="countdown-value" id="lowTideCountdown">--:--:--</div></div>
</div></div>
<div class="card"><h2 class="card-title">📊 Graphique des Marées (24h)</h2><div class="chart-container"><canvas id="tideChart"></canvas></div></div>
<div class="card"><h2 class="card-title">🌤️ Météo Marine</h2>
<div class="weather-widget">
<div class="weather-item"><div class="weather-icon">💨</div><div class="weather-value" id="windSpeed"><?=$port['wind_base']?> nœuds</div><div class="weather-label">Force du vent</div></div>
<div class="weather-item"><div class="weather-icon">🧭</div><div class="weather-value" id="windDir"><?=esc($port['wind_dir'])?></div><div class="weather-label">Direction</div></div>
<div class="weather-item"><div class="weather-icon">🌊</div><div class="weather-value" id="seaState"><?=esc($port['sea_state'])?></div><div class="weather-label">État de la mer</div></div>
</div></div>
<div class="card"><h2 class="card-title">📅 Marées du Jour (Coeff. <?=$today_data['coeff']?>)</h2>
<div class="tide-info-grid">
<div class="info-item"><div class="info-label">Coefficient</div><div class="info-value"><?=$today_data['coeff']?></div></div>
<div class="info-item"><div class="info-label">Type</div><div class="info-value"><span class="coeff-badge coeff-<?=$today_data['coeff']>=100?'vive':($today_data['coeff']>=70?'fort':($today_data['coeff']>=45?'moyen':'morte'))?>"><?=$today_data['coeff']>=100?'Vives eaux':($today_data['coeff']>=70?'Fort':($today_data['coeff']>=45?'Moyen':'Mortes eaux'))?></span></div></div>
<div class="info-item"><div class="info-label">Marnage</div><div class="info-value"><?=round($port['range_high']-$port['range_low'],1)?>m</div></div>
</div>
<div class="tides-list" style="margin-top:20px"><?php foreach($today_data['tides'] as $tide):?>
<div class="tide-entry"><div class="tide-type <?=$tide['type']?>"><?=$tide['type']==='high'?'⬆️':'⬇️'?> <?=$tide['type']==='high'?'Pleine Mer':'Basse Mer'?></div><div class="tide-time"><?=esc($tide['time'])?></div><div class="tide-height"><?=$tide['height']?>m</div></div>
<?php endforeach;?></div></div>
<div class="card"><h2 class="card-title">📈 Coefficients sur 30 jours</h2><div class="chart-container" style="height:200px"><canvas id="coeffChart"></canvas></div></div>
</main>
<script>
const PORTS=<?=json_encode(array_map(fn($p)=>['name'=>$p['name'],'lat'=>$p['lat'],'lon'=>$p['lon'],'icon'=>$p['icon']],$PORTS))?>;
const CURRENT_PORT='<?=$port_key?>';const TIDE_DATA=<?=json_encode($today_data['tides'])?>;
const PORT_RANGES=<?=json_encode(array_map(fn($p)=>['low'=>$p['range_low'],'high'=>$p['range_high']],$PORTS))?>;
let favorites=JSON.parse(localStorage.getItem('mareeslive_favorites')||'[]');
function updateFavStars(){document.querySelectorAll('.fav-star').forEach(star=>{star.textContent=favorites.includes(star.dataset.port)?'⭐':'☆'});
const selector=document.getElementById('portSelector'),buttons=Array.from(selector.querySelectorAll('.port-btn'));
buttons.sort((a,b)=>{const aFav=favorites.includes(a.dataset.port),bFav=favorites.includes(b.dataset.port);if(aFav&&!bFav)return -1;if(!aFav&&bFav)return 1;return 0});
buttons.forEach(btn=>selector.appendChild(btn))}
document.querySelectorAll('.fav-star').forEach(star=>{star.addEventListener('click',e=>{e.stopPropagation();const port=star.dataset.port;favorites=favorites.includes(port)?favorites.filter(p=>p!==port):[...favorites,port];localStorage.setItem('mareeslive_favorites',JSON.stringify(favorites));updateFavStars()})});
document.querySelectorAll('.port-btn').forEach(btn=>{btn.addEventListener('click',()=>{if(!btn.querySelector('.fav-star').contains(event.target))window.location.href='?port='+btn.dataset.port})});
updateFavStars();
window.addEventListener('scroll',()=>{const bg=document.getElementById('parallaxBg');if(bg)bg.style.transform=`translateY(${window.pageYOffset*0.3}px)`});
let touchStartX=0,touchEndX=0;
document.addEventListener('touchstart',e=>touchStartX=e.changedTouches[0].screenX);
document.addEventListener('touchend',e=>{touchEndX=e.changedTouches[0].screenX;const diff=touchStartX-touchEndX;if(Math.abs(diff)>50){const ports=Object.keys(PORTS),idx=ports.indexOf(CURRENT_PORT);if(diff>0&&idx<ports.length-1)window.location.href='?port='+ports[idx+1];else if(diff<0&&idx>0)window.location.href='?port='+ports[idx-1]}});
const map=L.map('tideMap').setView([47.25,-2.35],10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap'}).addTo(map);
Object.entries(PORTS).forEach(([key,p])=>{const m=L.marker([p.lat,p.lon]).addTo(map);m.bindPopup(`<b>${p.icon} ${p.name}</b><br>Cliquer pour les marées`);m.on('click',()=>window.location.href='?port='+key)});
const tideCtx=document.getElementById('tideChart').getContext('2d'),hours=[],heights=[],range=PORT_RANGES[CURRENT_PORT];
for(let i=0;i<=24;i++){hours.push(i+'h');heights.push((((range.high-range.low)/2)*Math.sin((i/24)*Math.PI*2)+((range.high+range.low)/2)).toFixed(2))}
new Chart(tideCtx,{type:'line',data:{labels:hours,datasets:[{label:'Hauteur (m)',data:heights,borderColor:'#06b6d4',backgroundColor:'rgba(6,182,212,0.2)',fill:true,tension:0.4,pointRadius:3}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{grid:{color:'rgba(255,255,255,0.1)'},ticks:{color:'#b8d4e8'}},x:{grid:{display:false},ticks:{color:'#b8d4e8'}}}}});
const coeffCtx=document.getElementById('coeffChart').getContext('2d'),coeffData=[],coeffLabels=[],today=new Date();
for(let i=0;i<30;i++){const d=new Date(today);d.setDate(d.getDate()+i);coeffLabels.push(d.getDate()+'/'+(d.getMonth()+1));coeffData.push(Math.round(70+Math.sin(((d-new Date('2024-01-06'))/(29.53*86400*1000))*Math.PI*2)*38))}
new Chart(coeffCtx,{type:'line',data:{labels:coeffLabels,datasets:[{label:'Coefficient',data:coeffData,borderColor:'#06b6d4',backgroundColor:'rgba(6,182,212,0.1)',fill:true,tension:0.3,pointRadius:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{min:20,max:120,grid:{color:'rgba(255,255,255,0.1)'},ticks:{color:'#b8d4e8'}},x:{grid:{display:false},ticks:{color:'#b8d4e8',maxTicksLimit:10}}}}});
function updateCountdown(){const now=new Date(),today=new Date(now.getFullYear(),now.getMonth(),now.getDate());let nextHigh=null,nextLow=null;
TIDE_DATA.forEach(tide=>{const[h,m]=tide.time.split(':').map(Number),tideTime=new Date(today);tideTime.setHours(h,m,0);if(tideTime>now){if(tide.type==='high'&&!nextHigh)nextHigh=tideTime;if(tide.type==='low'&&!nextLow)nextLow=tideTime}});
if(!nextHigh){nextHigh=new Date(today);nextHigh.setDate(nextHigh.getDate()+1);nextHigh.setHours(6,0,0)}
if(!nextLow){nextLow=new Date(today);nextLow.setDate(nextLow.getDate()+1);nextLow.setHours(0,0,0)}
function formatDiff(t){const d=t-now;return`${String(Math.floor(d/3600000)).padStart(2,'0')}:${String(Math.floor((d%3600000)/60000)).padStart(2,'0')}:${String(Math.floor((d%60000)/1000)).padStart(2,'0')}`}
document.getElementById('highTideCountdown').textContent=formatDiff(nextHigh);document.getElementById('lowTideCountdown').textContent=formatDiff(nextLow)}
updateCountdown();setInterval(updateCountdown,1000);
</script>
</body>
</html>

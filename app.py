import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle
import random
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from track_maps import get_track_svg, get_weather_svg
except:
    def get_track_svg(r, c='#e10600', s=300): return ''
    def get_weather_svg(a, t, s=80): return ''

def to_laptime(s):
    try:
        if s is None or (isinstance(s, float) and s != s): return "N/A"
        return f"{int(s//60)}:{s%60:06.3f}"
    except: return "N/A"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="P1TWALL", page_icon="🏎️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
html,body,[class*="css"]{font-family:'Titillium Web',sans-serif;}
.stApp{background-color:#080808;color:#fff;background-image:radial-gradient(ellipse at 20% 50%,rgba(225,6,0,.03) 0%,transparent 50%),radial-gradient(ellipse at 80% 50%,rgba(54,113,198,.03) 0%,transparent 50%);}
.stApp::before{content:'';display:block;height:3px;background:linear-gradient(90deg,#e10600,#ff4422,#e10600);position:fixed;top:0;left:0;right:0;z-index:9999;box-shadow:0 0 20px rgba(225,6,0,.8);}
.stTabs [data-baseweb="tab-list"]{background:linear-gradient(180deg,#0f0f0f,#111);border-bottom:1px solid #1a1a1a;gap:0;padding:0 16px;}
.stTabs [data-baseweb="tab"]{background:transparent;color:#555;font-family:'Titillium Web',sans-serif;font-weight:700;font-size:.85rem;letter-spacing:2px;text-transform:uppercase;padding:16px 28px;border:none;border-bottom:3px solid transparent;transition:all .2s;}
.stTabs [data-baseweb="tab"]:hover{color:#888;}
.stTabs [aria-selected="true"]{background:transparent!important;color:#fff!important;border-bottom:3px solid #e10600!important;}
[data-testid="stMetric"]{background:linear-gradient(135deg,#141414,#1a1a1a);border:1px solid #222;border-top:2px solid #e10600;border-radius:6px;padding:16px!important;box-shadow:0 4px 20px rgba(0,0,0,.4);transition:transform .2s,box-shadow .2s;}
[data-testid="stMetric"]:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(225,6,0,.15);}
[data-testid="stMetricLabel"]{color:#666!important;font-size:.7rem!important;text-transform:uppercase;letter-spacing:2px;}
[data-testid="stMetricValue"]{color:#fff!important;font-weight:700!important;font-size:1.6rem!important;}
.stSelectbox>div>div{background:#141414!important;border:1px solid #222!important;color:#fff!important;border-radius:4px!important;}
.stSelectbox>div>div:focus-within{border-color:#e10600!important;}
.stButton button{font-family:'Titillium Web',sans-serif!important;font-weight:700!important;letter-spacing:1px!important;text-transform:uppercase!important;transition:all .2s!important;}
.stButton button[kind="primary"]{background:linear-gradient(135deg,#e10600,#cc0500)!important;border:none!important;box-shadow:0 4px 15px rgba(225,6,0,.4)!important;}
.stButton button[kind="primary"]:hover{box-shadow:0 6px 25px rgba(225,6,0,.6)!important;transform:translateY(-1px)!important;}
.stButton button[kind="secondary"]{background:#141414!important;border:1px solid #333!important;color:#888!important;}
.stButton button[kind="secondary"]:hover{border-color:#e10600!important;color:#fff!important;}
hr{border-color:#1a1a1a!important;}
.stSuccess{background:rgba(57,181,74,.08)!important;border:1px solid rgba(57,181,74,.3)!important;border-left:4px solid #39b54a!important;border-radius:4px!important;}
.stInfo{background:rgba(54,113,198,.08)!important;border:1px solid rgba(54,113,198,.3)!important;border-left:4px solid #3671C6!important;border-radius:4px!important;}
.streamlit-expanderHeader{background:#141414!important;border:1px solid #1a1a1a!important;border-radius:4px!important;color:#888!important;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:#0a0a0a;}
::-webkit-scrollbar-thumb{background:#333;border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:#e10600;}
.grid-row{background:#111;border:1px solid #1a1a1a;border-radius:6px;padding:10px 16px;margin-bottom:5px;}
.narrative{background:linear-gradient(135deg,#130000,#1a0a0a);border-left:3px solid #e10600;border-radius:0 6px 6px 0;padding:16px 20px;margin:12px 0;font-style:italic;color:#bbb;line-height:1.8;}
.stat-pill{display:inline-block;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:20px;padding:3px 12px;font-size:.8rem;color:#888;margin:2px;}
.card{background:linear-gradient(135deg,#141414,#1a1a1a);border:1px solid #222;border-radius:8px;padding:20px;text-align:center;}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
TEAM_COLORS = {
    'Red Bull Racing':'#3671C6','Ferrari':'#E8002D','Mercedes':'#27F4D2',
    'McLaren':'#FF8000','Aston Martin':'#229971','Alpine':'#FF87BC',
    'Williams':'#64C4FF','RB':'#6692FF','Racing Bulls':'#6692FF',
    'Haas F1 Team':'#B6BABD','Kick Sauber':'#52E252',
    'AlphaTauri':'#5E8FAA','Alfa Romeo':'#C92D4B',
}
TEAM_NAME_DISPLAY = {
    'Haas F1 Team':'Haas','Red Bull Racing':'Red Bull','Racing Bulls':'Racing Bulls',
    'AlphaTauri':'AlphaTauri','Alfa Romeo':'Alfa Romeo','Aston Martin':'Aston Martin',
    'Alpine':'Alpine','Williams':'Williams','McLaren':'McLaren',
    'Mercedes':'Mercedes','Ferrari':'Ferrari','RB':'RB','Kick Sauber':'Kick Sauber',
}
MANUAL_DRIVERS = {
    'COL':('Franco Colapinto','ARG'),'VET':('Sebastian Vettel','GER'),
    'LAT':('Nicholas Latifi','CAN'),'MSC':('Mick Schumacher','GER'),
    'DEV':('Nyck De Vries','NED'),'HUL':('Nico Hulkenberg','GER'),
    'SAR':('Logan Sargeant','USA'),'ZHO':('Guanyu Zhou','CHN'),
    'BOT':('Valtteri Bottas','FIN'),'RIC':('Daniel Ricciardo','AUS'),
}
COMPOUND_COLORS = {'SOFT':'#e10600','MEDIUM':'#ffd700','HARD':'#ffffff','INTERMEDIATE':'#39b54a','WET':'#0067ff'}
RACE_FLAGS = {
    'Bahrain':'🇧🇭','Saudi Arabian':'🇸🇦','Australian':'🇦🇺','Japanese':'🇯🇵',
    'Chinese':'🇨🇳','Miami':'🇺🇸','Emilia Romagna':'🇮🇹','Monaco':'🇲🇨',
    'Canadian':'🇨🇦','Spanish':'🇪🇸','Austrian':'🇦🇹','British':'🇬🇧',
    'Hungarian':'🇭🇺','Belgian':'🇧🇪','Dutch':'🇳🇱','Italian':'🇮🇹',
    'Azerbaijan':'🇦🇿','Singapore':'🇸🇬','United States':'🇺🇸','Mexico City':'🇲🇽',
    'São Paulo':'🇧🇷','Las Vegas':'🇺🇸','Qatar':'🇶🇦','Abu Dhabi':'🇦🇪','French':'🇫🇷',
}
F1_POINTS = {1:25,2:18,3:15,4:12,5:10,6:8,7:6,8:4,9:2,10:1}
STRATEGIES = {
    'A':{'name':'Aggressive','detail':'Soft → Hard','desc':'Fast early pace, higher tyre deg risk. Best in cool conditions.','early_boost':0.3,'late_penalty':-0.15},
    'B':{'name':'Balanced','detail':'Medium → Medium','desc':'Consistent pace throughout. Safe points-scoring strategy.','early_boost':0.0,'late_penalty':0.0},
    'C':{'name':'Conservative','detail':'Hard → Soft','desc':'Slow start, strong finish. Good for high-deg circuits.','early_boost':-0.2,'late_penalty':0.25},
}

def tc(t): return TEAM_COLORS.get(t,'#aaaaaa')
def td(t): return TEAM_NAME_DISPLAY.get(t, t)

def race_flag(name):
    for key, flag in RACE_FLAGS.items():
        if key.lower() in name.lower():
            return flag
    return '🏁'

def badge(team, size=80):
    color = tc(team)
    name = td(team)
    initials = ''.join(w[0] for w in name.split()[:2]).upper()
    return f'<div style="width:{size}px;height:{size}px;background:{color};border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-weight:900;font-size:{size//3}px;color:#fff;flex-shrink:0;">{initials}</div>'

def avatar(abbr, team, size=80):
    url = HEADSHOTS.get(abbr,'')
    color = tc(team)
    if url:
        return f'<img src="{url}" style="width:{size}px;height:{size}px;border-radius:8px;object-fit:cover;border:2px solid {color};">'
    return f'<div style="width:{size}px;height:{size}px;border-radius:8px;background:{color};display:inline-flex;align-items:center;justify-content:center;font-weight:900;font-size:{size//4}px;color:#fff;">{abbr}</div>'

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_race_model():
    with open('data/model.pkl','rb') as f: return pickle.load(f)
@st.cache_resource
def load_qual_model():
    with open('data/model_qualifying.pkl','rb') as f: return pickle.load(f)
@st.cache_data
def load_race_data(): return pd.read_csv('data/all_seasons.csv')
@st.cache_data
def load_qual_data(): return pd.read_csv('data/qualifying.csv')
@st.cache_data
def load_driver_info(): return pd.read_csv('data/driver_info.csv')
@st.cache_data
def load_calendar(): return pd.read_csv('data/race_calendar.csv')
@st.cache_data
def load_grid(): return pd.read_csv('data/grid_positions.csv')

race_bundle = load_race_model()
r_model=race_bundle['model']; r_le_driver=race_bundle['le_driver']
r_le_compound=race_bundle['le_compound']; r_le_race=race_bundle['le_race']; r_le_team=race_bundle['le_team']
qual_bundle = load_qual_model()
q_model=qual_bundle['model']; q_le_driver=qual_bundle['le_driver']
q_le_compound=qual_bundle['le_compound']; q_le_race=qual_bundle['le_race']; q_le_team=qual_bundle['le_team']
race_df=load_race_data(); qual_df=load_qual_data()
driver_info=load_driver_info(); calendar=load_calendar(); grid_pos=load_grid()
race_stats=race_df.groupby(['Race','Year'])['LapTimeSeconds'].agg(['mean','std']).reset_index()
qual_stats=qual_df.groupby(['Race','Year'])['LapTimeSeconds'].agg(['mean','std']).reset_index()
HEADSHOTS={}

# ── Helpers ───────────────────────────────────────────────────────────────────
def driver_name(abbr):
    if abbr in MANUAL_DRIVERS: return MANUAL_DRIVERS[abbr][0]
    row = driver_info[driver_info['Abbreviation']==abbr]
    if row.empty: return abbr
    name = row['FullName'].values[0]
    return name if isinstance(name,str) and name.strip() else abbr

def driver_sort_key(abbr): return driver_name(abbr)
def driver_last(abbr): return driver_name(abbr).split()[-1]

def weather_desc(air, track, easy):
    if easy:
        if air > 35: return f"🌡️ Scorching — {air:.0f}°C air / {track:.0f}°C track. High tyre degradation expected."
        if air > 25: return f"☀️ Warm — {air:.0f}°C air / {track:.0f}°C track. Standard strategy applies."
        return f"🌥️ Cool — {air:.0f}°C air / {track:.0f}°C track. Aggressive strategies favoured."
    return f"Air: {air:.0f}°C · Track: {track:.0f}°C"

def get_race_name(official, year):
    short = official.replace(' Grand Prix','').strip()
    m = race_df[(race_df['Year']==year)&race_df['Race'].str.contains(short,na=False)]
    return m['Race'].iloc[0] if not m.empty else None

def predict_pace(driver, team, grid, rname, year):
    stats = race_stats[(race_stats['Race']==rname)&(race_stats['Year']==year)]
    if stats.empty or rname not in r_le_race.classes_: return None
    if driver not in r_le_driver.classes_ or team not in r_le_team.classes_: return None
    rd = race_df[(race_df['Race']==rname)&(race_df['Year']==year)]
    row = pd.DataFrame([{
        'Driver':r_le_driver.transform([driver])[0],'TeamName':r_le_team.transform([team])[0],
        'GridPosition':grid,'LapNumber':30,'Compound':r_le_compound.transform(['MEDIUM'])[0],
        'TyreLife':15,'AirTemp':rd['AirTemp'].mean(),'TrackTemp':rd['TrackTemp'].mean(),
        'Stint':2,'Race':r_le_race.transform([rname])[0],'Year':year
    }])
    n = r_model.predict(row)[0]
    m,s = stats['mean'].values[0],stats['std'].values[0]
    return n*s+m

def predict_race_secs(driver,team,grid,lap,compound,tyre_life,air,track,stint,race,year):
    stats = race_stats[(race_stats['Race']==race)&(race_stats['Year']==year)]
    if stats.empty or race not in r_le_race.classes_: return None
    if driver not in r_le_driver.classes_ or team not in r_le_team.classes_: return None
    if compound not in r_le_compound.classes_: return None
    row = pd.DataFrame([{
        'Driver':r_le_driver.transform([driver])[0],'TeamName':r_le_team.transform([team])[0],
        'GridPosition':grid,'LapNumber':lap,'Compound':r_le_compound.transform([compound])[0],
        'TyreLife':tyre_life,'AirTemp':air,'TrackTemp':track,'Stint':stint,
        'Race':r_le_race.transform([race])[0],'Year':year
    }])
    n = r_model.predict(row)[0]
    m,s = stats['mean'].values[0],stats['std'].values[0]
    return n*s+m

def predict_qual_secs(driver,team,lap,compound,tyre_life,air,track,race,year):
    stats = qual_stats[(qual_stats['Race']==race)&(qual_stats['Year']==year)]
    if stats.empty or race not in q_le_race.classes_: return None
    if driver not in q_le_driver.classes_ or team not in q_le_team.classes_: return None
    row = pd.DataFrame([{
        'Driver':q_le_driver.transform([driver])[0],'TeamName':q_le_team.transform([team])[0],
        'LapNumber':lap,'Compound':q_le_compound.transform([compound])[0],
        'TyreLife':tyre_life,'AirTemp':air,'TrackTemp':track,
        'Race':q_le_race.transform([race])[0],'Year':year
    }])
    n = q_model.predict(row)[0]
    m,s = stats['mean'].values[0],stats['std'].values[0]
    return n*s+m

def check_dnf(driver, team, year):
    de = grid_pos[(grid_pos['Abbreviation']==driver)&(grid_pos['Year']==year)&(grid_pos['DNFType']=='DriverDNF')]
    cd = grid_pos[(grid_pos['TeamName']==team)&(grid_pos['Year']==year)&(grid_pos['DNFType']=='CarDNF')]
    total = len(grid_pos[grid_pos['Year']==year]['Race'].unique())
    if total==0: return False
    return random.random() < min(len(de)/total + len(cd)/(total*2), 0.25)

def sim_race(rname_official, year, d1, d2, team, strat_d1, strat_d2, hierarchy, d1_is_num1):
    try:
        rname = get_race_name(rname_official, year)
        if rname is None: return None
        short = rname_official.replace(' Grand Prix','').strip()
        fg = grid_pos[grid_pos['Race'].str.contains(short,na=False)&(grid_pos['Year']==year)].copy()
        real_team = set(race_df[(race_df['TeamName']==team)&(race_df['Year']==year)]['Driver'].unique())
        field = [{'driver':r['Abbreviation'],'team':r['TeamName'],
                  'finish':r.get('Position',20),'dnf':r.get('DNFType','Finished')!='Finished'}
                 for _,r in fg.iterrows()
                 if r['Abbreviation'] not in [d1,d2] and r['Abbreviation'] not in real_team]
        d1gr=fg[fg['Abbreviation']==d1]; d2gr=fg[fg['Abbreviation']==d2]
        d1g=int(d1gr['GridPosition'].values[0]) if not d1gr.empty else 10
        d2g=int(d2gr['GridPosition'].values[0]) if not d2gr.empty else 12
        rd=race_df[(race_df['Race']==rname)&(race_df['Year']==year)]
        avg_air=rd['AirTemp'].mean() if not rd.empty else 25
        avg_track=rd['TrackTemp'].mean() if not rd.empty else 40
        d1p=predict_pace(d1,team,d1g,rname,year)
        d2p=predict_pace(d2,team,d2g,rname,year)
        avg=rd['LapTimeSeconds'].mean() if not rd.empty else 90
        if d1p is None: d1p=avg
        if d2p is None: d2p=avg+0.3
        se1=STRATEGIES[strat_d1]; se2=STRATEGIES[strat_d2]
        d1e=d1p-se1['early_boost']+se1['late_penalty']
        d2e=d2p-se2['early_boost']+se2['late_penalty']
        d1_dnf=check_dnf(d1,team,year); d2_dnf=check_dnf(d2,team,year)
        fp=race_df[(race_df['Race']==rname)&(race_df['Year']==year)].groupby('Driver')['LapTimeSeconds'].mean()
        fp=fp[~fp.index.isin(real_team|{d1,d2})]
        d1r=max(1,min(len(fp)+1,sum(1 for p in fp if p<d1e)+1))
        d2r=max(1,min(len(fp)+1,sum(1 for p in fp if p<d2e)+1))
        team_orders=False
        if hierarchy and not d1_dnf and not d2_dnf:
            if d1_is_num1 and abs(d1r-d2r)<=2 and d2r<d1r: d2r=d1r+1; team_orders=True
            elif not d1_is_num1 and abs(d1r-d2r)<=2 and d1r<d2r: d1r=d2r+1; team_orders=True
        d1f=None if d1_dnf else d1r; d2f=None if d2_dnf else d2r
        d1pts=F1_POINTS.get(d1f,0) if d1f else 0
        d2pts=F1_POINTS.get(d2f,0) if d2f else 0
        d1_fl=False; d2_fl=False
        if d1f and d1f<=10 and d1e<=d2e: d1_fl=True; d1pts+=1
        elif d2f and d2f<=10: d2_fl=True; d2pts+=1
        return {'d1_finish':d1f,'d1_pts':d1pts,'d1_dnf':d1_dnf,'d1_fl':d1_fl,'d1_grid':d1g,
                'd2_finish':d2f,'d2_pts':d2pts,'d2_dnf':d2_dnf,'d2_fl':d2_fl,'d2_grid':d2g,
                'team_orders':team_orders,'field_dnfs':[f['driver'] for f in field if f['dnf']][:3],
                'field':field,'air':avg_air,'track':avg_track,'strat_d1':strat_d1,'strat_d2':strat_d2}
    except Exception as e:
        return None

def build_standings(race_results, d1, d2, team, year):
    real_team=set(race_df[(race_df['TeamName']==team)&(race_df['Year']==year)]['Driver'].unique())
    wdc={}; wcc={}
    for rr in race_results:
        res=rr['result']
        if res['d1_finish']: wdc[d1]=wdc.get(d1,0)+res['d1_pts']
        if res['d2_finish']: wdc[d2]=wdc.get(d2,0)+res['d2_pts']
        wcc[team]=wcc.get(team,0)+res['d1_pts']+res['d2_pts']
        for fr in res.get('field',[]):
            if not fr['dnf'] and fr['finish']:
                pts=F1_POINTS.get(int(fr['finish']),0)
                drv=fr['driver']; t=fr['team']
                if drv not in real_team: wdc[drv]=wdc.get(drv,0)+pts
                if t!=team: wcc[t]=wcc.get(t,0)+pts
    if d1 not in wdc: wdc[d1]=0
    if d2 not in wdc: wdc[d2]=0
    if team not in wcc: wcc[team]=0
    return (dict(sorted(wdc.items(),key=lambda x:x[1],reverse=True)),
            dict(sorted(wcc.items(),key=lambda x:x[1],reverse=True)))

def get_actual_results(season):
    wdc={}; wcc={}
    for _,row in grid_pos[grid_pos['Year']==season].iterrows():
        if row.get('DNFType','Finished')=='Finished' and pd.notna(row.get('Position')):
            pts=F1_POINTS.get(int(row['Position']),0)
            wdc[row['Abbreviation']]=wdc.get(row['Abbreviation'],0)+pts
            wcc[row['TeamName']]=wcc.get(row['TeamName'],0)+pts
    return (dict(sorted(wdc.items(),key=lambda x:x[1],reverse=True)),
            dict(sorted(wcc.items(),key=lambda x:x[1],reverse=True)))

def standings_html(wdc, wcc, d1, d2, team, top=10):
    def drv_row(i,drv,pts):
        is_ours=drv in [d1,d2]
        bg='#1a0a0a' if is_ours else '#111'
        border=f'border-left:3px solid {tc(team)};' if is_ours else ''
        drv_team=race_df[race_df['Driver']==drv]['TeamName'].iloc[0] if not race_df[race_df['Driver']==drv].empty else ''
        img=avatar(drv,drv_team,28) if drv_team else f'<div style="width:28px;height:28px;border-radius:50%;background:#333;display:inline-flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:900;">{drv[:2]}</div>'
        name=driver_name(drv) if drv in r_le_driver.classes_ else drv
        pc=tc(team) if is_ours else '#fff'
        crown=" 🏆" if i==0 else ""
        return f'<div style="background:{bg};{border}padding:6px 10px;border-radius:4px;margin-bottom:3px;display:flex;align-items:center;gap:8px;"><span style="color:#555;width:22px;font-size:.75rem;">P{i+1}</span>{img}<span style="flex:1;font-size:.85rem;">{name}{crown}</span><span style="font-weight:700;color:{pc};">{pts}</span></div>'
    def team_row(i,t,pts):
        is_ours=t==team
        bg='#1a0a0a' if is_ours else '#111'
        border=f'border-left:3px solid {tc(t)};'
        pc=tc(team) if is_ours else '#fff'
        crown=" 🏆" if i==0 else ""
        return f'<div style="background:{bg};{border}padding:6px 10px;border-radius:4px;margin-bottom:3px;display:flex;align-items:center;gap:8px;"><span style="color:#555;width:22px;font-size:.75rem;">P{i+1}</span>{badge(t,28)}<span style="flex:1;font-size:.85rem;margin-left:4px;">{td(t)}{crown}</span><span style="font-weight:700;color:{pc};">{pts}</span></div>'
    wdc_html=''.join(drv_row(i,d,p) for i,(d,p) in enumerate(list(wdc.items())[:top]))
    wcc_html=''.join(team_row(i,t,p) for i,(t,p) in enumerate(list(wcc.items())[:top]))
    return wdc_html, wcc_html

def champ_banner(trophies, title, lines):
    lines_html=''.join(f'<div style="color:#fff;font-size:1rem;margin-top:6px;">{l}</div>' for l in lines)
    st.markdown(f'<div style="background:#1a1a1a;border:2px solid #ffd700;border-radius:8px;padding:28px;text-align:center;margin-bottom:20px;box-shadow:0 0 40px rgba(255,215,0,.15);"><div style="font-size:2.5rem;margin-bottom:8px;">{trophies}</div><div style="font-size:1.6rem;font-weight:900;color:#ffd700;letter-spacing:3px;">{title}</div>{lines_html}</div>', unsafe_allow_html=True)

def narrative_text(rn, res, d1, d2, mode, sd1, sd2):
    lines=[]
    d1n=driver_last(d1); d2n=driver_last(d2)
    if res['field_dnfs']: lines.append(f"Retirements hit the field — {', '.join(res['field_dnfs'])} failed to finish.")
    if res['d1_dnf']: lines.append(f"{d1n} retired from the race.")
    elif res['d1_finish']:
        s=STRATEGIES[sd1]['name']
        if res['d1_finish']<=3: lines.append(f"{d1n}'s {s} strategy delivered P{res['d1_finish']}.")
        elif res['d1_finish']<=10: lines.append(f"{d1n} scored {res['d1_pts']} points with P{res['d1_finish']}.")
        else: lines.append(f"A tough weekend for {d1n}, P{res['d1_finish']}.")
    if res['d2_dnf']: lines.append(f"{d2n} also retired.")
    elif res['d2_finish']:
        s=STRATEGIES[sd2]['name']
        if res['d2_finish']<=3: lines.append(f"{d2n} also delivered P{res['d2_finish']}.")
        elif res['d2_finish']<=10: lines.append(f"{d2n} scored {res['d2_pts']} points with P{res['d2_finish']}.")
        else: lines.append(f"{d2n} struggled, P{res['d2_finish']}.")
    if res['team_orders']: lines.append("Team orders were applied.")
    if res['d1_fl']: lines.append(f"{d1n} set the fastest lap.")
    elif res['d2_fl']: lines.append(f"{d2n} set the fastest lap.")
    if mode=='easy':
        total=res['d1_pts']+res['d2_pts']
        if total>=30: lines.append("Excellent haul for the team this weekend.")
        elif total>=15: lines.append("Solid points weekend.")
        elif total>0: lines.append("Points on the board — every one counts.")
        else: lines.append("A weekend to forget, but the season is long.")
    return ' '.join(lines)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 24px;background:linear-gradient(180deg,#0d0000 0%,#110000 40%,#080808 100%);border-bottom:1px solid #1a1a1a;margin-bottom:0;position:relative;overflow:hidden;">
    <div style="position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at center top,rgba(225,6,0,.1) 0%,transparent 60%);"></div>
    <div style="position:relative;z-index:1;">
        <div style="font-family:'Orbitron',monospace;font-size:3rem;font-weight:900;letter-spacing:8px;color:#fff;text-shadow:0 0 40px rgba(225,6,0,.5);margin-bottom:8px;">P1TWALL</div>
        <div style="color:#333;letter-spacing:4px;font-size:.8rem;text-transform:uppercase;">2022–2025 &nbsp;·&nbsp; XGBOOST &nbsp;·&nbsp; 62,000+ LAPS &nbsp;·&nbsp; FASTF1</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_game, tab_analytics, tab_method, tab_about = st.tabs([
    "🎮  THE GAME","📊  ANALYTICS","ℹ️  METHODOLOGY","👤  ABOUT"
])

# ── Session state ─────────────────────────────────────────────────────────────
for k,v in [('state','setup'),('gd',{})]:
    if k not in st.session_state: st.session_state[k]=v
S=st.session_state.state; G=st.session_state.gd

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — THE GAME
# ═══════════════════════════════════════════════════════════════════════════════
with tab_game:

    if S=='setup':
        st.markdown("## Team Setup")
        st.markdown("Pick your season, constructor, and two drivers. Simulate a full championship.")
        c1,c2=st.columns(2)
        with c1:
            season=st.selectbox("📅 Season",[2025,2024,2023,2022],key='season')
            all_teams=sorted(race_df[race_df['Year']==season]['TeamName'].unique(),key=td)
            team=st.selectbox("🏭 Constructor",all_teams,format_func=td,key='team')
            st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin:8px 0 16px;">{badge(team,80)}<span style="font-size:1.1rem;font-weight:700;color:{tc(team)};">{td(team)}</span></div>', unsafe_allow_html=True)
            all_drivers=sorted(r_le_driver.classes_,key=driver_sort_key)
            d1=st.selectbox("🏎️ Driver 1",all_drivers,format_func=driver_name,key='d1')
            d2_list=[d for d in all_drivers if d!=d1]
            d2=st.selectbox("🏎️ Driver 2",d2_list,format_func=driver_name,key='d2')
            hc1,hc2=st.columns(2)
            with hc1:
                st.markdown(avatar(d1,team,80),unsafe_allow_html=True)
                st.caption(driver_name(d1))
            with hc2:
                st.markdown(avatar(d2,team,80),unsafe_allow_html=True)
                st.caption(driver_name(d2))
        with c2:
            st.markdown("### Team Philosophy")
            phil=st.radio("Philosophy",["⚔️ Free to Fight","👑 Strict Hierarchy"],key='phil',label_visibility="collapsed")
            hierarchy="Hierarchy" in phil
            d1_is_num1=True
            if hierarchy:
                num1=st.radio("#1 Driver",[d1,d2],format_func=driver_name,key='num1')
                d1_is_num1=(num1==d1)
                st.markdown(f'<div style="background:#141414;border-left:4px solid {tc(team)};padding:12px;border-radius:4px;margin-top:8px;"><strong style="color:{tc(team)};">👑 {driver_name(num1)}</strong> receives strategic priority.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="background:#141414;border-left:4px solid #39b54a;padding:12px;border-radius:4px;margin-top:8px;"><strong style="color:#39b54a;">⚔️ Free to Fight</strong> — no team orders.</div>', unsafe_allow_html=True)
            st.markdown("### Game Mode")
            mode=st.radio("Mode",["⚡ Quick Result — simulate full season instantly","🎮 Full Season — race by race with strategy"],key='mode',label_visibility="collapsed")
            difficulty="easy"
            if "Full" in mode:
                diff_raw=st.radio("Difficulty",["🟢 Easy — strategy tips included","🔴 Hard — no hints"],key='diff')
                difficulty="easy" if "Easy" in diff_raw else "hard"
        st.divider()
        if st.button("🚀 START SEASON",type="primary",use_container_width=True):
            cal=calendar[calendar['Year']==season].sort_values('Round').to_dict('records')
            st.session_state.gd={
                'season':season,'team':team,'d1':d1,'d2':d2,
                'hierarchy':hierarchy,'d1_is_num1':d1_is_num1,
                'mode':'quick' if 'Quick' in mode else 'full',
                'difficulty':difficulty,'calendar':cal,
                'idx':0,'race_results':[],
                'd1_pts':0,'d2_pts':0,'team_pts':0,
                'd1_wins':0,'d2_wins':0,'d1_pods':0,'d2_pods':0,'d1_fl':0,'d2_fl':0,
            }
            st.session_state.state='simming' if 'Quick' in mode else 'pre_race'
            st.rerun()

    elif S=='simming':
        with st.spinner("🏎️  Simulating full season..."):
            for i in range(G['idx'],len(G['calendar'])):
                race=G['calendar'][i]
                res=sim_race(race['OfficialName'],G['season'],G['d1'],G['d2'],G['team'],'B','B',G['hierarchy'],G['d1_is_num1'])
                if res:
                    G['d1_pts']+=res['d1_pts']; G['d2_pts']+=res['d2_pts']
                    G['team_pts']+=res['d1_pts']+res['d2_pts']
                    if res['d1_finish']==1: G['d1_wins']+=1
                    if res['d2_finish']==1: G['d2_wins']+=1
                    if res['d1_finish'] and res['d1_finish']<=3: G['d1_pods']+=1
                    if res['d2_finish'] and res['d2_finish']<=3: G['d2_pods']+=1
                    if res['d1_fl']: G['d1_fl']+=1
                    if res['d2_fl']: G['d2_fl']+=1
                    G['race_results'].append({'race':race['OfficialName'],'result':res})
            G['idx']=len(G['calendar'])
            st.session_state.state='season_end'; st.rerun()

    elif S=='pre_race':
        idx=G['idx']; cal=G['calendar']
        if idx>=len(cal): st.session_state.state='season_end'; st.rerun()
        race=cal[idx]; rn=race['OfficialName']; flag_e=race_flag(rn)
        diff=G['difficulty']; season=G['season']
        short=rn.replace(' Grand Prix','').strip()
        rd=race_df[race_df['Race'].str.contains(short,na=False)&(race_df['Year']==season)]
        avg_air=rd['AirTemp'].mean() if not rd.empty else 25
        avg_track=rd['TrackTemp'].mean() if not rd.empty else 40
        st.markdown(f"### Race {idx+1} of {len(cal)}")
        st.markdown(f"## {flag_e} {rn}")
        # Track map + weather
        tm_col,wt_col=st.columns([3,1])
        with tm_col:
            track_svg=get_track_svg(rn,'#e10600',320)
            if track_svg: st.markdown(track_svg,unsafe_allow_html=True)
        with wt_col:
            weather_svg=get_weather_svg(avg_air,avg_track,70)
            wdesc=weather_desc(avg_air,avg_track,diff=="easy")
            st.markdown(f'<div style="text-align:center;padding:8px;">{weather_svg}<div style="font-size:.8rem;color:#aaa;margin-top:6px;">{wdesc}</div></div>',unsafe_allow_html=True)
        # Grid positions
        fg=grid_pos[grid_pos['Race'].str.contains(short,na=False)&(grid_pos['Year']==season)]
        d1gr=fg[fg['Abbreviation']==G['d1']]; d2gr=fg[fg['Abbreviation']==G['d2']]
        d1g=int(d1gr['GridPosition'].values[0]) if not d1gr.empty else 10
        d2g=int(d2gr['GridPosition'].values[0]) if not d2gr.empty else 12
        gc1,gc2,gc3=st.columns(3)
        with gc1:
            st.markdown(f'<div style="background:#141414;border:1px solid #222;border-radius:8px;padding:16px;text-align:center;">{avatar(G["d1"],G["team"],80)}<div style="font-weight:700;margin-top:8px;">{driver_name(G["d1"])}</div><div style="font-size:2rem;font-weight:900;color:{tc(G["team"])};">P{d1g}</div><div style="color:#555;font-size:.8rem;">GRID</div></div>',unsafe_allow_html=True)
        with gc2:
            st.markdown(f'<div style="background:#141414;border:1px solid #222;border-radius:8px;padding:16px;text-align:center;">{badge(G["team"],80)}<div style="font-weight:700;margin-top:8px;">{td(G["team"])}</div><div style="font-size:1rem;color:#555;margin-top:4px;">Race {idx+1} of {len(cal)}</div></div>',unsafe_allow_html=True)
        with gc3:
            st.markdown(f'<div style="background:#141414;border:1px solid #222;border-radius:8px;padding:16px;text-align:center;">{avatar(G["d2"],G["team"],80)}<div style="font-weight:700;margin-top:8px;">{driver_name(G["d2"])}</div><div style="font-size:2rem;font-weight:900;color:{tc(G["team"])};">P{d2g}</div><div style="color:#555;font-size:.8rem;">GRID</div></div>',unsafe_allow_html=True)
        # Current standings
        if G['race_results']:
            with st.expander("📊 Current Championship Standings"):
                wdc,wcc=build_standings(G['race_results'],G['d1'],G['d2'],G['team'],season)
                wdc_html,wcc_html=standings_html(wdc,wcc,G['d1'],G['d2'],G['team'])
                sc1,sc2=st.columns(2)
                with sc1: st.markdown("**🏆 Drivers**"); st.markdown(wdc_html,unsafe_allow_html=True)
                with sc2: st.markdown("**🏭 Constructors**"); st.markdown(wcc_html,unsafe_allow_html=True)
        st.divider()
        st.markdown("### Strategy")
        if 'strat_d1_sel' not in st.session_state: st.session_state.strat_d1_sel='B'
        if 'strat_d2_sel' not in st.session_state: st.session_state.strat_d2_sel='B'
        sc1,sc2=st.columns(2)
        with sc1:
            st.markdown(f"**{driver_name(G['d1'])}**")
            for k,v in STRATEGIES.items():
                selected=st.session_state.strat_d1_sel==k
                check="✓  " if selected else "   "
                desc=f"\n{v['desc']}" if diff=='easy' else ""
                if st.button(f"{check}{v['name']}  ·  {v['detail']}{desc}",key=f"d1_{k}",use_container_width=True,type="primary" if selected else "secondary"):
                    st.session_state.strat_d1_sel=k; st.rerun()
            strat_d1=st.session_state.strat_d1_sel
        with sc2:
            st.markdown(f"**{driver_name(G['d2'])}**")
            for k,v in STRATEGIES.items():
                selected=st.session_state.strat_d2_sel==k
                check="✓  " if selected else "   "
                desc=f"\n{v['desc']}" if diff=='easy' else ""
                if st.button(f"{check}{v['name']}  ·  {v['detail']}{desc}",key=f"d2_{k}",use_container_width=True,type="primary" if selected else "secondary"):
                    st.session_state.strat_d2_sel=k; st.rerun()
            strat_d2=st.session_state.strat_d2_sel
        st.divider()
        if st.button("🏁 SIMULATE RACE",type="primary",use_container_width=True):
            res=sim_race(rn,season,G['d1'],G['d2'],G['team'],strat_d1,strat_d2,G['hierarchy'],G['d1_is_num1'])
            if res:
                G['d1_pts']+=res['d1_pts']; G['d2_pts']+=res['d2_pts']
                G['team_pts']+=res['d1_pts']+res['d2_pts']
                if res['d1_finish']==1: G['d1_wins']+=1
                if res['d2_finish']==1: G['d2_wins']+=1
                if res['d1_finish'] and res['d1_finish']<=3: G['d1_pods']+=1
                if res['d2_finish'] and res['d2_finish']<=3: G['d2_pods']+=1
                if res['d1_fl']: G['d1_fl']+=1
                if res['d2_fl']: G['d2_fl']+=1
                G['race_results'].append({'race':rn,'result':res,'strat_d1':strat_d1,'strat_d2':strat_d2})
                G['last_res']=res; G['last_strat_d1']=strat_d1; G['last_strat_d2']=strat_d2
                st.session_state.state='debrief'; st.rerun()

    elif S=='debrief':
        res=G['last_res']; diff=G['difficulty']
        idx=G['idx']; rn=G['calendar'][idx]['OfficialName']
        flag_e=race_flag(rn); d1=G['d1']; d2=G['d2']; team=G['team']
        sd1=G['last_strat_d1']; sd2=G['last_strat_d2']
        if res['d1_finish']==1 or res['d2_finish']==1: st.balloons()
        elif (res['d1_finish'] and res['d1_finish']<=3) or (res['d2_finish'] and res['d2_finish']<=3):
            st.toast("🏆 Podium finish!",icon="🏆")
        if res['d1_fl'] or res['d2_fl']: st.toast("⚡ Fastest lap bonus point!",icon="⚡")
        if res['d1_dnf'] and res['d2_dnf']: st.toast("❌ Double DNF — tough weekend.",icon="❌")
        st.markdown(f"## {flag_e} {rn} — Race Result")
        def finish_str(f,dnf):
            if dnf: return "DNF"
            if f==1: return "🥇 P1"
            if f==2: return "🥈 P2"
            if f==3: return "🥉 P3"
            return f"P{f}" if f else "DNF"
        rc1,rc2=st.columns(2)
        for col,abbr,finish,dnf,pts,season_pts,fl,sd in [
            (rc1,d1,res['d1_finish'],res['d1_dnf'],res['d1_pts'],G['d1_pts'],res['d1_fl'],sd1),
            (rc2,d2,res['d2_finish'],res['d2_dnf'],res['d2_pts'],G['d2_pts'],res['d2_fl'],sd2),
        ]:
            with col:
                fl_b=" ⚡" if fl else ""
                st.markdown(f'<div class="card" style="border-top:4px solid {tc(team)};">{avatar(abbr,team,80)}<div style="font-weight:700;margin:8px 0;">{driver_name(abbr)}</div><div style="font-size:2rem;font-weight:900;">{finish_str(finish,dnf)}{fl_b}</div><div style="font-size:1.5rem;color:#e10600;font-weight:900;margin-top:6px;">+{pts} pts</div><div style="color:#555;font-size:.85rem;">Season: {season_pts} pts</div><div style="color:#555;font-size:.8rem;margin-top:4px;">{STRATEGIES[sd]["name"]} strategy</div></div>', unsafe_allow_html=True)
        st.divider()
        race_pts=res['d1_pts']+res['d2_pts']
        wdc,wcc=build_standings(G['race_results'],d1,d2,team,G['season'])
        d1_pos=list(wdc.keys()).index(d1)+1 if d1 in wdc else '—'
        d2_pos=list(wdc.keys()).index(d2)+1 if d2 in wdc else '—'
        team_pos=list(wcc.keys()).index(team)+1 if team in wcc else '—'
        tm1,tm2=st.columns(2)
        with tm1: st.metric(f"🏭 {td(team)} — Race Points",f"+{race_pts}",delta=f"Season: {G['team_pts']} pts")
        with tm2:
            st.markdown(f'<div style="background:#141414;border:1px solid #222;border-radius:6px;padding:12px 16px;"><div style="color:#555;font-size:.75rem;text-transform:uppercase;letter-spacing:1px;">Championship Position</div><div style="margin-top:8px;display:flex;gap:24px;"><div><span style="color:{tc(team)};font-weight:900;font-size:1.3rem;">P{d1_pos}</span><div style="color:#555;font-size:.8rem;">{driver_last(d1)} WDC</div></div><div><span style="color:{tc(team)};font-weight:900;font-size:1.3rem;">P{d2_pos}</span><div style="color:#555;font-size:.8rem;">{driver_last(d2)} WDC</div></div><div><span style="color:{tc(team)};font-weight:900;font-size:1.3rem;">P{team_pos}</span><div style="color:#555;font-size:.8rem;">{td(team)} WCC</div></div></div></div>', unsafe_allow_html=True)
        narr=narrative_text(rn,res,d1,d2,diff,sd1,sd2)
        st.markdown(f'<div class="narrative">"{narr}"</div>',unsafe_allow_html=True)
        st.markdown("### 📊 Championship Standings")
        wdc_html,wcc_html=standings_html(wdc,wcc,d1,d2,team)
        scc1,scc2=st.columns(2)
        with scc1: st.markdown("**🏆 Drivers**"); st.markdown(wdc_html,unsafe_allow_html=True)
        with scc2: st.markdown("**🏭 Constructors**"); st.markdown(wcc_html,unsafe_allow_html=True)
        with st.expander("📋 Full Race Result"):
            for fr in sorted(res.get('field',[]),key=lambda x:x['finish'])[:10]:
                pos=fr['finish']; color=tc(fr['team'])
                dnf_s=" — DNF" if fr['dnf'] else ""
                st.markdown(f'<div class="grid-row" style="border-left:3px solid {color};display:flex;gap:12px;align-items:center;"><span style="color:#555;width:24px;">P{int(pos) if pos else "—"}</span>{avatar(fr["driver"],fr["team"],28)}<span style="flex:1;">{driver_name(fr["driver"]) if fr["driver"] in r_le_driver.classes_ else fr["driver"]}</span><span style="color:#555;font-size:.85rem;">{td(fr["team"])}{dnf_s}</span></div>', unsafe_allow_html=True)
        st.divider()
        races_left=len(G['calendar'])-idx-1
        b1,b2,b3=st.columns(3)
        with b1:
            if st.button("🏁 NEXT RACE",type="primary",use_container_width=True):
                G['idx']+=1
                st.session_state.state='season_end' if G['idx']>=len(G['calendar']) else 'pre_race'
                st.rerun()
        with b2:
            if races_left>0 and st.button(f"⚡ AUTO-SIM {races_left} RACES",use_container_width=True):
                G['idx']+=1; st.session_state.state='simming'; st.rerun()
        with b3:
            if st.button("🔄 START OVER",use_container_width=True):
                st.session_state.state='setup'; st.session_state.gd={}; st.rerun()

    elif S=='season_end':
        d1=G['d1']; d2=G['d2']; team=G['team']
        wdc,wcc=build_standings(G['race_results'],d1,d2,team,G['season'])
        d1_wdc=list(wdc.keys()).index(d1)+1 if d1 in wdc else '—'
        d2_wdc=list(wdc.keys()).index(d2)+1 if d2 in wdc else '—'
        team_wcc=list(wcc.keys()).index(team)+1 if team in wcc else '—'
        d1_champ=list(wdc.keys())[0]==d1 if wdc else False
        d2_champ=list(wdc.keys())[0]==d2 if wdc else False
        team_champ=list(wcc.keys())[0]==team if wcc else False
        d1n=driver_name(d1); d2n=driver_name(d2)
        st.markdown(f"## 🏆 {G['season']} Season Complete")
        st.markdown(f'<div style="background:#141414;border:1px solid #1a1a1a;border-left:6px solid {tc(team)};border-radius:6px;padding:16px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">{badge(team,56)}<div><div style="font-size:1.4rem;font-weight:900;">{td(team)}</div><div style="color:#555;">P{team_wcc} Constructors · {G["team_pts"]} pts</div></div></div>', unsafe_allow_html=True)
        if d1_champ or d2_champ: st.balloons()
        elif team_champ: st.snow()
        if d1_champ and d2_champ:
            champ_banner("🏆🏆🏆","Historic 1-2 Finish",[f"<strong style='color:#ffd700;'>{d1n}</strong> — World Champion · {G['d1_pts']} pts",f"{d2n} — P2 · {G['d2_pts']} pts",f"🏭 {td(team)} — Constructors' Champions · {G['team_pts']} pts","<span style='color:#888;font-size:.85rem;'>A legendary season.</span>"])
        elif d1_champ and team_champ:
            champ_banner("🏆🏆","Double Championship",[f"<strong style='color:#ffd700;'>{d1n}</strong> — World Champion · {G['d1_pts']} pts",f"🏭 {td(team)} — Constructors' Champions · {G['team_pts']} pts"])
        elif d2_champ and team_champ:
            champ_banner("🏆🏆","Double Championship",[f"<strong style='color:#ffd700;'>{d2n}</strong> — World Champion · {G['d2_pts']} pts",f"🏭 {td(team)} — Constructors' Champions · {G['team_pts']} pts"])
        elif d1_champ:
            champ_banner("🏆","World Champion",[f"<strong style='color:#ffd700;'>{d1n}</strong> wins the Drivers' Championship",f"<span style='color:#ffd700;font-size:1.4rem;font-weight:900;'>{G['d1_pts']} pts</span>",f"🏭 {td(team)} finished P{team_wcc} in the Constructors'"])
        elif d2_champ:
            champ_banner("🏆","World Champion",[f"<strong style='color:#ffd700;'>{d2n}</strong> wins the Drivers' Championship",f"<span style='color:#ffd700;font-size:1.4rem;font-weight:900;'>{G['d2_pts']} pts</span>",f"🏭 {td(team)} finished P{team_wcc} in the Constructors'"])
        elif team_champ:
            champ_banner("🏭","Constructors' Champions",[f"{td(team)} wins the Constructors' Championship",f"<span style='color:#ffd700;font-size:1.4rem;font-weight:900;'>{G['team_pts']} pts</span>",f"{d1n} P{d1_wdc} · {d2n} P{d2_wdc} in the Drivers'"])
        st.divider()
        fc1,fc2,fc3=st.columns(3)
        for col,abbr,label,pts,wins,pods,fls,pos in [
            (fc1,d1,"DRIVER 1",G['d1_pts'],G['d1_wins'],G['d1_pods'],G['d1_fl'],d1_wdc),
            (fc2,d2,"DRIVER 2",G['d2_pts'],G['d2_wins'],G['d2_pods'],G['d2_fl'],d2_wdc),
            (fc3,None,"CONSTRUCTORS",G['team_pts'],G['d1_wins']+G['d2_wins'],G['d1_pods']+G['d2_pods'],G['d1_fl']+G['d2_fl'],team_wcc),
        ]:
            with col:
                if abbr: st.markdown(avatar(abbr,team,80),unsafe_allow_html=True)
                else: st.markdown(badge(team,80),unsafe_allow_html=True)
                name=driver_name(abbr) if abbr else td(team)
                crown=" 🏆" if (abbr==d1 and d1_champ) or (abbr==d2 and d2_champ) or (abbr is None and team_champ) else ""
                st.markdown(f'<div class="card" style="border-top:4px solid {tc(team)};"><div style="color:#555;font-size:.75rem;letter-spacing:2px;">{label}</div><div style="font-size:1rem;font-weight:700;margin:6px 0;">{name}{crown}</div><div style="font-size:2.2rem;font-weight:900;color:#e10600;">{pts}</div><div style="color:#555;font-size:.8rem;">PTS · P{pos} Championship</div><div style="margin-top:10px;"><span class="stat-pill">🏆 {wins}W</span><span class="stat-pill">🥇 {pods} POD</span><span class="stat-pill">⚡ {fls} FL</span></div></div>', unsafe_allow_html=True)
        st.divider()
        st.markdown("### 📊 Final Championship Standings")
        wdc_html,wcc_html=standings_html(wdc,wcc,d1,d2,team,top=12)
        fsc1,fsc2=st.columns(2)
        with fsc1: st.markdown("**🏆 Drivers**"); st.markdown(wdc_html,unsafe_allow_html=True)
        with fsc2: st.markdown("**🏭 Constructors**"); st.markdown(wcc_html,unsafe_allow_html=True)
        st.divider()
        # vs actual
        st.markdown("### 📊 vs Real Season")
        actual_wdc,actual_wcc=get_actual_results(G['season'])
        acc1,acc2,acc3=st.columns(3)
        for col,abbr,name,sim_pos,sim_pts,adict in [
            (acc1,d1,driver_last(d1),d1_wdc,G['d1_pts'],actual_wdc),
            (acc2,d2,driver_last(d2),d2_wdc,G['d2_pts'],actual_wdc),
        ]:
            with col:
                actual_pos=list(adict.keys()).index(abbr)+1 if abbr in adict else None
                actual_pts=adict.get(abbr,0)
                if actual_pos and sim_pos!='—':
                    diff_pos=actual_pos-int(str(sim_pos)); diff_pts=sim_pts-actual_pts
                    arrow="↑" if diff_pos>0 else ("↓" if diff_pos<0 else "→")
                    pc='#39b54a' if diff_pos>0 else ('#e10600' if diff_pos<0 else '#888')
                    st.markdown(f'<div style="background:#141414;border:1px solid #1a1a1a;border-radius:8px;padding:14px;text-align:center;"><div style="color:#888;font-size:.8rem;">{name} WDC</div><div style="font-size:1.4rem;font-weight:900;color:{pc};">{arrow} {abs(diff_pos)} places</div><div style="color:#aaa;font-size:.85rem;">P{sim_pos} sim vs P{actual_pos} real</div><div style="color:{pc};font-size:.8rem;">{("+" if diff_pts>=0 else "")}{diff_pts} pts vs real {actual_pts}</div></div>', unsafe_allow_html=True)
        with acc3:
            actual_team_pos=list(actual_wcc.keys()).index(team)+1 if team in actual_wcc else None
            actual_team_pts=actual_wcc.get(team,0)
            if actual_team_pos and team_wcc!='—':
                diff_pos=actual_team_pos-int(str(team_wcc)); diff_pts=G['team_pts']-actual_team_pts
                arrow="↑" if diff_pos>0 else ("↓" if diff_pos<0 else "→")
                pc='#39b54a' if diff_pos>0 else ('#e10600' if diff_pos<0 else '#888')
                st.markdown(f'<div style="background:#141414;border:1px solid #1a1a1a;border-radius:8px;padding:14px;text-align:center;"><div style="color:#888;font-size:.8rem;">{td(team)} WCC</div><div style="font-size:1.4rem;font-weight:900;color:{pc};">{arrow} {abs(diff_pos)} places</div><div style="color:#aaa;font-size:.85rem;">P{team_wcc} sim vs P{actual_team_pos} real</div><div style="color:{pc};font-size:.8rem;">{("+" if diff_pts>=0 else "")}{diff_pts} pts vs real {actual_team_pts}</div></div>', unsafe_allow_html=True)
        st.divider()
        tw=G['d1_wins']+G['d2_wins']; tp=G['team_pts']
        if tw>=10: v=f"A dominant season. {d1n} P{d1_wdc}, {d2n} P{d2_wdc}. {td(team)} P{team_wcc} in the constructors."
        elif tw>=5: v=f"A strong season with {tw} wins. {d1n} P{d1_wdc}, {d2n} P{d2_wdc}. {td(team)} P{team_wcc} in the constructors."
        elif tp>=150: v=f"Consistent scoring: {d1n} P{d1_wdc}, {d2n} P{d2_wdc}. {td(team)} P{team_wcc} in the constructors."
        else: v=f"A tough season. {d1n} P{d1_wdc}, {d2n} P{d2_wdc}. {td(team)} P{team_wcc}. There's work to do."
        st.markdown(f'<div class="narrative">"{v}"</div>',unsafe_allow_html=True)
        with st.expander("📋 Full Season Results"):
            for rr in G['race_results']:
                res=rr['result']
                d1f=f"P{res['d1_finish']}" if res['d1_finish'] else "DNF"
                d2f=f"P{res['d2_finish']}" if res['d2_finish'] else "DNF"
                d1c='#ffd700' if res['d1_finish']==1 else ('#555' if res['d1_dnf'] else tc(team))
                d2c='#ffd700' if res['d2_finish']==1 else ('#555' if res['d2_dnf'] else tc(team))
                fl1=" ⚡" if res['d1_fl'] else ""; fl2=" ⚡" if res['d2_fl'] else ""
                st.markdown(f'<div class="grid-row" style="display:flex;align-items:center;gap:12px;"><span>{race_flag(rr["race"])}</span><span style="color:#555;flex:1;font-size:.9rem;">{rr["race"].replace(" Grand Prix","")}</span><span style="color:{d1c};font-weight:700;min-width:90px;">{driver_last(d1)}: {d1f}{fl1}</span><span style="color:#1a1a1a;">|</span><span style="color:{d2c};font-weight:700;min-width:90px;">{driver_last(d2)}: {d2f}{fl2}</span><span style="color:#555;font-size:.85rem;min-width:50px;text-align:right;">+{res["d1_pts"]+res["d2_pts"]}pts</span></div>', unsafe_allow_html=True)
        if st.button("🔄 PLAY AGAIN",type="primary",use_container_width=True):
            st.session_state.state='setup'; st.session_state.gd={}; st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    st.markdown("## 📊 Analytics")
    ana_tabs=st.tabs(["⏱ LAP PREDICTOR","🏁 QUALIFYING","📈 RACE BREAKDOWN","⚔️ HEAD TO HEAD","🧑‍✈️ DRIVER STATS"])

    with ana_tabs[0]:
        st.markdown("## Lap Time Predictor")
        lp_year=st.selectbox("Season",sorted(race_df['Year'].unique(),reverse=True),key='lp_year')
        lp_cal=calendar[calendar['Year']==lp_year].sort_values('Round')
        lp_race_opts={r['OfficialName']:f"{race_flag(r['OfficialName'])} {r['OfficialName']}" for _,r in lp_cal.iterrows()}
        lp_race_official=st.selectbox("Circuit",list(lp_race_opts.keys()),format_func=lambda x:lp_race_opts[x],key='lp_race')
        lp_race=get_race_name(lp_race_official,lp_year) or lp_race_official
        lp_teams=sorted(race_df[(race_df['Year']==lp_year)]['TeamName'].unique(),key=td)
        lp_team=st.selectbox("Team",lp_teams,format_func=td,key='lp_team')
        lp_tdrivers=sorted(race_df[(race_df['TeamName']==lp_team)&(race_df['Year']==lp_year)]['Driver'].unique(),key=driver_sort_key)
        lp_driver=st.selectbox("Driver",lp_tdrivers,format_func=driver_name,key='lp_driver')
        lp_rdata=race_df[(race_df['Race']==lp_race)&(race_df['Year']==lp_year)]
        lp_compounds=sorted(lp_rdata['Compound'].unique()) if not lp_rdata.empty else ['SOFT','MEDIUM','HARD']
        lp_compound=st.selectbox("Tyre",lp_compounds,key='lp_comp')
        air_min=float(lp_rdata['AirTemp'].min()) if not lp_rdata.empty else 14.0
        air_max=float(lp_rdata['AirTemp'].max()) if not lp_rdata.empty else 40.0
        trk_min=float(lp_rdata['TrackTemp'].min()) if not lp_rdata.empty else 20.0
        trk_max=float(lp_rdata['TrackTemp'].max()) if not lp_rdata.empty else 65.0
        lc1,lc2,lc3=st.columns(3)
        with lc1: lp_tl=st.slider("Tyre Age",1,40,10,key='lp_tl'); lp_stint=st.slider("Stint",1,3,1,key='lp_stint')
        with lc2: lp_grid=st.slider("Grid Position",1,20,5,key='lp_grid'); lp_lap=st.slider("Lap Number",1,60,25,key='lp_lap')
        with lc3: lp_air=st.slider("Air Temp",air_min,air_max,round((air_min+air_max)/2,1),key='lp_air'); lp_track=st.slider("Track Temp",trk_min,trk_max,round((trk_min+trk_max)/2,1),key='lp_track')
        pred=predict_race_secs(lp_driver,lp_team,lp_grid,lp_lap,lp_compound,lp_tl,lp_air,lp_track,lp_stint,lp_race,lp_year)
        st.divider()
        if pred and not lp_rdata.empty:
            fastest_row=lp_rdata.loc[lp_rdata['LapTimeSeconds'].idxmin()]
            similar=lp_rdata[(lp_rdata['Compound']==lp_compound)&lp_rdata['TyreLife'].between(lp_tl-3,lp_tl+3)]
            sim_row=similar.loc[similar['LapTimeSeconds'].idxmin()] if not similar.empty else None
            hs={k:{'HeadshotUrl':v} for k,v in HEADSHOTS.items()}
            m1,m2,m3=st.columns(3)
            with m1:
                h=hs.get(lp_driver,{}).get('HeadshotUrl','')
                if h: st.image(h,width=64)
                else: st.markdown(f'<div style="width:64px;height:64px;border-radius:8px;background:{tc(lp_team)};display:inline-flex;align-items:center;justify-content:center;font-weight:900;font-size:1.2rem;color:#fff;">{lp_driver}</div>',unsafe_allow_html=True)
                st.metric("🏎️ Predicted",to_laptime(pred))
                st.caption(f"{driver_name(lp_driver)} · Lap {lp_lap} · {lp_compound} age {lp_tl}")
            with m2:
                h2=hs.get(fastest_row['Driver'],{}).get('HeadshotUrl','')
                if h2: st.image(h2,width=64)
                d=pred-fastest_row['LapTimeSeconds']
                st.metric("⚡ Race Fastest Lap",to_laptime(fastest_row['LapTimeSeconds']),delta=f"+{d:.3f}s",delta_color="inverse")
                st.caption(f"{driver_name(fastest_row['Driver'])} · Lap {int(fastest_row['LapNumber'])} · {fastest_row.get('Compound','?')} tyre")
            with m3:
                if sim_row is not None:
                    h3=hs.get(sim_row['Driver'],{}).get('HeadshotUrl','')
                    if h3: st.image(h3,width=64)
                    d2v=pred-sim_row['LapTimeSeconds']
                    st.metric(f"🔄 Fastest {lp_compound} ~{lp_tl} laps",to_laptime(sim_row['LapTimeSeconds']),delta=f"+{d2v:.3f}s",delta_color="inverse")
                    st.caption(f"{driver_name(sim_row['Driver'])} · Lap {int(sim_row['LapNumber'])}")
                else: st.info(f"No {lp_compound} laps at similar age.")
        else: st.info("Select a valid combination to see predictions.")

    with ana_tabs[1]:
        st.markdown("## Qualifying Predictor")
        q_subtabs=st.tabs(["SINGLE DRIVER","FULL GRID"])

        with q_subtabs[0]:
            qs_year=st.selectbox("Season",sorted(qual_df['Year'].unique(),reverse=True),key='qs_year')
            qs_cal=calendar[calendar['Year']==qs_year].sort_values('Round')
            qs_race_opts={r['OfficialName']:f"{race_flag(r['OfficialName'])} {r['OfficialName']}" for _,r in qs_cal.iterrows()}
            qs_race_official=st.selectbox("Circuit",list(qs_race_opts.keys()),format_func=lambda x:qs_race_opts[x],key='qs_race')
            # Map to qual model class
            qs_race_mapped=get_race_name(qs_race_official,qs_year)
            qs_race=None
            if qs_race_mapped:
                for cls in q_le_race.classes_:
                    if cls.lower() in qs_race_mapped.lower() or qs_race_mapped.lower() in cls.lower():
                        qs_race=cls; break
            if not qs_race: qs_race=qs_race_mapped or qs_race_official
            qs_teams=sorted(race_df[(race_df['Year']==qs_year)]['TeamName'].unique(),key=td)
            qs_team=st.selectbox("Team",qs_teams,format_func=td,key='qs_team')
            qs_tdrivers=sorted(race_df[(race_df['TeamName']==qs_team)&(race_df['Year']==qs_year)]['Driver'].unique(),key=driver_sort_key)
            qs_dopts={d:driver_name(d) for d in qs_tdrivers if d in q_le_driver.classes_}
            if not qs_dopts: qs_dopts={d:driver_name(d) for d in q_le_driver.classes_}
            qs_driver=st.selectbox("Driver",list(qs_dopts.keys()),format_func=lambda x:qs_dopts[x],key='qs_driver')
            qsc1,qsc2=st.columns(2)
            with qsc1: qs_comp=st.selectbox("Tyre",['SOFT','MEDIUM','HARD'],key='qs_comp'); qs_tl=st.slider("Tyre Age",1,10,3,key='qs_tl'); qs_lap=st.slider("Lap",1,3,1,key='qs_lap')
            with qsc2: qs_air=st.slider("Air Temp",14,45,25,key='qs_air'); qs_track=st.slider("Track Temp",20,65,40,key='qs_track')
            qs_pred=predict_qual_secs(qs_driver,qs_team,qs_lap,qs_comp,qs_tl,qs_air,qs_track,qs_race,qs_year) if qs_race else None
            st.divider()
            if qs_pred:
                qdf_f=qual_df[(qual_df['Race']==qs_race)&(qual_df['Year']==qs_year)]
                hs={k:{'HeadshotUrl':v} for k,v in HEADSHOTS.items()}
                qm1,qm2,qm3=st.columns(3)
                with qm1:
                    h=hs.get(qs_driver,{}).get('HeadshotUrl','')
                    if h: st.image(h,width=64)
                    st.metric("🏎️ Predicted Q3",to_laptime(qs_pred)); st.caption(f"{driver_name(qs_driver)} · {qs_comp}")
                with qm2:
                    if not qdf_f.empty:
                        pole=qdf_f.loc[qdf_f['LapTimeSeconds'].idxmin()]
                        h2=hs.get(pole['Driver'],{}).get('HeadshotUrl','')
                        if h2: st.image(h2,width=64)
                        d=qs_pred-pole['LapTimeSeconds']
                        st.metric("🏆 Pole (actual)",to_laptime(pole['LapTimeSeconds']),delta=f"+{d:.3f}s",delta_color="inverse")
                        st.caption(f"{driver_name(pole['Driver'])}")
                with qm3:
                    if not qdf_f.empty:
                        db=qdf_f[qdf_f['Driver']==qs_driver]['LapTimeSeconds'].min()
                        if not pd.isna(db):
                            d2v=qs_pred-db
                            st.metric(f"📋 {driver_name(qs_driver)} actual best",to_laptime(db),delta=f"{d2v:+.3f}s",delta_color="inverse")
            else: st.info("No qualifying data available for this circuit/season combination.")

        with q_subtabs[1]:
            fg_year=st.selectbox("Season",sorted(qual_df['Year'].unique(),reverse=True),key='fg_year')
            fg_cal=calendar[calendar['Year']==fg_year].sort_values('Round')
            fg_race_opts={r['OfficialName']:f"{race_flag(r['OfficialName'])} {r['OfficialName']}" for _,r in fg_cal.iterrows()}
            fg_race_official=st.selectbox("Circuit",list(fg_race_opts.keys()),format_func=lambda x:fg_race_opts[x],key='fg_race')
            fg_race_mapped=get_race_name(fg_race_official,fg_year)
            fg_race=None
            if fg_race_mapped:
                for cls in q_le_race.classes_:
                    if cls.lower() in fg_race_mapped.lower() or fg_race_mapped.lower() in cls.lower():
                        fg_race=cls; break
            if not fg_race: fg_race=fg_race_mapped or fg_race_official
            fgc1,fgc2=st.columns(2)
            with fgc1: fg_air=st.slider("Air Temp",14,45,25,key='fg_air'); fg_track=st.slider("Track Temp",20,65,40,key='fg_track')
            with fgc2: fg_tl=st.slider("Tyre Age",1,10,3,key='fg_tl')
            if st.button("🏁 Generate Grid",type="primary") and fg_race:
                fg_drivers=qual_df[(qual_df['Race']==fg_race)&(qual_df['Year']==fg_year)][['Driver','TeamName']].drop_duplicates('Driver')
                if fg_drivers.empty: fg_drivers=race_df[(race_df['Race']==fg_race_mapped)&(race_df['Year']==fg_year)][['Driver','TeamName']].drop_duplicates('Driver') if fg_race_mapped else pd.DataFrame()
                results=[]
                for _,row in fg_drivers.iterrows():
                    drv,tm=row['Driver'],row['TeamName']
                    if drv not in q_le_driver.classes_ or tm not in q_le_team.classes_: continue
                    p=predict_qual_secs(drv,tm,1,'SOFT',fg_tl,fg_air,fg_track,fg_race,fg_year)
                    if p: results.append({'Driver':drv,'TeamName':tm,'PredictedTime':p})
                actual_order=qual_df[(qual_df['Race']==fg_race)&(qual_df['Year']==fg_year)].groupby('Driver')['LapTimeSeconds'].min().reset_index().sort_values('LapTimeSeconds').reset_index(drop=True)
                if results:
                    grid_df=pd.DataFrame(results).sort_values('PredictedTime').reset_index(drop=True)
                    pole_t=grid_df['PredictedTime'].iloc[0]
                    hs={k:{'HeadshotUrl':v} for k,v in HEADSHOTS.items()}
                    gc1,gc2=st.columns(2)
                    with gc1:
                        st.markdown("### 🔮 Predicted")
                        for i,row in grid_df.iterrows():
                            pos=i+1; color=tc(row['TeamName'])
                            delta="POLE" if pos==1 else f"+{row['PredictedTime']-pole_t:.3f}s"
                            h=hs.get(row['Driver'],{}).get('HeadshotUrl','')
                            img=f'<img src="{h}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:2px solid {color};">' if h else f'<div style="width:32px;height:32px;border-radius:50%;background:{color};display:inline-flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:900;">{row["Driver"][:2]}</div>'
                            bc={1:'background:#ffd700;color:#000',2:'background:#aaa;color:#000',3:'background:#cd7f32;color:#fff'}.get(pos,'background:#e10600;color:#fff')
                            st.markdown(f'<div style="background:#111;border-left:3px solid {color};border-radius:4px;padding:6px 10px;margin-bottom:4px;display:flex;align-items:center;gap:8px;"><div style="{bc};width:28px;height:28px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-weight:900;font-size:.8rem;">{pos}</div>{img}<div style="flex:1;font-size:.85rem;">{driver_name(row["Driver"])}</div><div style="font-family:monospace;font-size:.85rem;">{to_laptime(row["PredictedTime"])}</div><div style="color:#e10600;font-size:.8rem;margin-left:6px;">{delta}</div></div>', unsafe_allow_html=True)
                    with gc2:
                        st.markdown("### 📋 Actual")
                        if not actual_order.empty:
                            pole_a=actual_order['LapTimeSeconds'].iloc[0]
                            for i,row in actual_order.iterrows():
                                pos=i+1
                                drv_team=race_df[race_df['Driver']==row['Driver']]['TeamName'].iloc[0] if not race_df[race_df['Driver']==row['Driver']].empty else ''
                                color=tc(drv_team)
                                delta="POLE" if pos==1 else f"+{row['LapTimeSeconds']-pole_a:.3f}s"
                                h=hs.get(row['Driver'],{}).get('HeadshotUrl','')
                                img=f'<img src="{h}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:2px solid {color};">' if h else f'<div style="width:32px;height:32px;border-radius:50%;background:{color};display:inline-flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:900;">{row["Driver"][:2]}</div>'
                                bc={1:'background:#ffd700;color:#000',2:'background:#aaa;color:#000',3:'background:#cd7f32;color:#fff'}.get(pos,'background:#333;color:#fff')
                                st.markdown(f'<div style="background:#111;border-left:3px solid {color};border-radius:4px;padding:6px 10px;margin-bottom:4px;display:flex;align-items:center;gap:8px;"><div style="{bc};width:28px;height:28px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-weight:900;font-size:.8rem;">{pos}</div>{img}<div style="flex:1;font-size:.85rem;">{driver_name(row["Driver"])}</div><div style="font-family:monospace;font-size:.85rem;">{to_laptime(row["LapTimeSeconds"])}</div><div style="color:#39b54a;font-size:.8rem;margin-left:6px;">{delta}</div></div>', unsafe_allow_html=True)
                        else: st.info("No actual qualifying data for this race.")
                else: st.warning("Not enough data to generate grid prediction.")

    with ana_tabs[2]:
        st.markdown("## Driver Race Breakdown")
        rb_year=st.selectbox("Season",sorted(race_df['Year'].unique(),reverse=True),key='rb_year')
        rb_cal=calendar[calendar['Year']==rb_year].sort_values('Round')
        rb_race_opts={r['OfficialName']:f"{race_flag(r['OfficialName'])} {r['OfficialName']}" for _,r in rb_cal.iterrows()}
        rb_race_official=st.selectbox("Circuit",list(rb_race_opts.keys()),format_func=lambda x:rb_race_opts[x],key='rb_race')
        rb_race=get_race_name(rb_race_official,rb_year) or rb_race_official
        rb_teams=sorted(race_df[(race_df['Race']==rb_race)&(race_df['Year']==rb_year)]['TeamName'].unique(),key=td)
        rb_team=st.selectbox("Team",rb_teams,format_func=td,key='rb_team') if len(rb_teams)>0 else st.selectbox("Team",[],key='rb_team')
        rb_tdrivers=sorted(race_df[(race_df['Race']==rb_race)&(race_df['Year']==rb_year)&(race_df['TeamName']==rb_team)]['Driver'].unique(),key=driver_sort_key) if rb_team else []
        rb_driver=st.selectbox("Driver",rb_tdrivers,format_func=driver_name,key='rb_driver') if rb_tdrivers else None
        if rb_driver:
            driver_race=race_df[(race_df['Race']==rb_race)&(race_df['Year']==rb_year)&(race_df['Driver']==rb_driver)].sort_values('LapNumber').copy()
            if not driver_race.empty:
                pit_laps=driver_race[driver_race['Stint'].diff()>0]['LapNumber'].tolist()
                race_all=race_df[(race_df['Race']==rb_race)&(race_df['Year']==rb_year)]
                winner_drv=race_all.groupby('Driver')['LapTimeSeconds'].mean().idxmin()
                winner_data=race_all[race_all['Driver']==winner_drv].sort_values('LapNumber') if winner_drv!=rb_driver else None
                s1,s2,s3,s4=st.columns(4)
                with s1: st.markdown(f'<div style="background:#141414;border-top:3px solid #ffd700;border-radius:4px;padding:14px;"><div style="color:#888;font-size:.75rem;">⚡ FASTEST LAP</div><div style="font-size:1.6rem;font-weight:700;color:#ffd700;">{to_laptime(driver_race["LapTimeSeconds"].min())}</div></div>', unsafe_allow_html=True)
                with s2: st.markdown(f'<div style="background:#141414;border-top:3px solid #3671C6;border-radius:4px;padding:14px;"><div style="color:#888;font-size:.75rem;">📊 AVERAGE LAP</div><div style="font-size:1.6rem;font-weight:700;color:#3671C6;">{to_laptime(driver_race["LapTimeSeconds"].mean())}</div></div>', unsafe_allow_html=True)
                with s3: st.metric("🔄 Total Laps",len(driver_race))
                with s4: st.metric("🛞 Pit Stops",len(pit_laps))
                fig=go.Figure()
                for sn in driver_race['Stint'].unique():
                    sd=driver_race[driver_race['Stint']==sn]; comp=sd['Compound'].iloc[0]
                    color=COMPOUND_COLORS.get(comp,'#aaa')
                    fig.add_trace(go.Scatter(x=sd['LapNumber'],y=sd['LapTimeSeconds'],mode='lines+markers',name=f"{driver_name(rb_driver)} S{int(sn)} {comp}",line=dict(color=color,width=2),marker=dict(size=4),connectgaps=False))
                if winner_data is not None:
                    wt=race_df[race_df['Driver']==winner_drv]['TeamName'].iloc[0]
                    fig.add_trace(go.Scatter(x=winner_data['LapNumber'],y=winner_data['LapTimeSeconds'],mode='lines',name=f"🏆 {driver_name(winner_drv)} (Race Winner)",line=dict(color=tc(wt),width=1,dash='dot'),opacity=0.5,connectgaps=False))
                for pit in pit_laps:
                    fig.add_vline(x=pit,line_dash='dash',line_color='#333',annotation_text="PIT",annotation_font_color='#666')
                fig.update_layout(template='plotly_dark',paper_bgcolor='#111',plot_bgcolor='#141414',height=420,xaxis_title="Lap",yaxis_title="Lap Time (s)",title=f"{driver_name(rb_driver)} — {rb_race} {rb_year}",legend=dict(bgcolor='#141414'))
                st.plotly_chart(fig,use_container_width=True)
                ss=driver_race.groupby(['Stint','Compound']).agg(Laps=('LapNumber','count'),AvgLap=('LapTimeSeconds','mean'),FastestLap=('LapTimeSeconds','min')).reset_index()
                ss['AvgLap']=ss['AvgLap'].apply(to_laptime); ss['FastestLap']=ss['FastestLap'].apply(to_laptime)
                st.dataframe(ss,use_container_width=True,hide_index=True)
            else: st.info("No data for this selection.")

    with ana_tabs[3]:
        st.markdown("## Head to Head")
        hh_year=st.selectbox("Season",sorted(race_df['Year'].unique(),reverse=True),key='hh_year')
        hh_cal=calendar[calendar['Year']==hh_year].sort_values('Round')
        hh_race_opts={r['OfficialName']:f"{race_flag(r['OfficialName'])} {r['OfficialName']}" for _,r in hh_cal.iterrows()}
        hh_race_official=st.selectbox("Circuit",list(hh_race_opts.keys()),format_func=lambda x:hh_race_opts[x],key='hh_race')
        hh_race=get_race_name(hh_race_official,hh_year) or hh_race_official
        hh_rdrivers=sorted(race_df[(race_df['Race']==hh_race)&(race_df['Year']==hh_year)]['Driver'].unique(),key=driver_sort_key)
        hc1,hc2=st.columns(2)
        with hc1: hh_d1=st.selectbox("Driver 1",hh_rdrivers,format_func=driver_name,key='hh_d1')
        with hc2: hh_d2=st.selectbox("Driver 2",[d for d in hh_rdrivers if d!=hh_d1],format_func=driver_name,key='hh_d2')
        d1d=race_df[(race_df['Race']==hh_race)&(race_df['Year']==hh_year)&(race_df['Driver']==hh_d1)].sort_values('LapNumber')
        d2d=race_df[(race_df['Race']==hh_race)&(race_df['Year']==hh_year)&(race_df['Driver']==hh_d2)].sort_values('LapNumber')
        if not d1d.empty and not d2d.empty:
            t1=d1d['TeamName'].iloc[0]; t2=d2d['TeamName'].iloc[0]
            hs={k:{'HeadshotUrl':v} for k,v in HEADSHOTS.items()}
            hm1,hm2,hm3,hm4=st.columns(4)
            hc1, hc2 = st.columns(2)
            with hc1:
                h=hs.get(hh_d1,{}).get('HeadshotUrl','')
                hi=f'<img src="{h}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid {tc(t1)};vertical-align:middle;margin-right:10px;">' if h else f'<div style="width:48px;height:48px;border-radius:50%;background:{tc(t1)};display:inline-flex;align-items:center;justify-content:center;font-weight:900;font-size:.75rem;color:#fff;margin-right:10px;">{hh_d1}</div>'
                st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:12px;">{hi}<span style="font-size:1rem;font-weight:700;">{driver_name(hh_d1)}</span></div>', unsafe_allow_html=True)
                m1,m2=st.columns(2)
                with m1: st.metric("Fastest",to_laptime(d1d['LapTimeSeconds'].min()))
                with m2: st.metric("Avg",to_laptime(d1d['LapTimeSeconds'].mean()))
            with hc2:
                h=hs.get(hh_d2,{}).get('HeadshotUrl','')
                hi=f'<img src="{h}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid {tc(t2)};vertical-align:middle;margin-right:10px;">' if h else f'<div style="width:48px;height:48px;border-radius:50%;background:{tc(t2)};display:inline-flex;align-items:center;justify-content:middle;font-weight:900;font-size:.75rem;color:#fff;margin-right:10px;">{hh_d2}</div>'
                st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:12px;">{hi}<span style="font-size:1rem;font-weight:700;">{driver_name(hh_d2)}</span></div>', unsafe_allow_html=True)
                m3,m4=st.columns(2)
                with m3: st.metric("Fastest",to_laptime(d2d['LapTimeSeconds'].min()))
                with m4: st.metric("Avg",to_laptime(d2d['LapTimeSeconds'].mean()))
            fig_h=go.Figure()
            fig_h.add_trace(go.Scatter(x=d1d['LapNumber'],y=d1d['LapTimeSeconds'],mode='lines',name=f"{driver_name(hh_d1)} ({td(t1)})",line=dict(color=tc(t1),width=2),connectgaps=False))
            fig_h.add_trace(go.Scatter(x=d2d['LapNumber'],y=d2d['LapTimeSeconds'],mode='lines',name=f"{driver_name(hh_d2)} ({td(t2)})",line=dict(color=tc(t2),width=2),connectgaps=False))
            fig_h.update_layout(template='plotly_dark',paper_bgcolor='#111',plot_bgcolor='#141414',height=380,xaxis_title="Lap",yaxis_title="Lap Time (s)",title=f"{driver_name(hh_d1)} vs {driver_name(hh_d2)} — {hh_race} {hh_year}")
            st.plotly_chart(fig_h,use_container_width=True)
            merged=pd.merge(d1d[['LapNumber','LapTimeSeconds']],d2d[['LapNumber','LapTimeSeconds']],on='LapNumber',suffixes=('_d1','_d2'))
            merged['Delta']=merged['LapTimeSeconds_d1']-merged['LapTimeSeconds_d2']
            fig_d=go.Figure()
            fig_d.add_trace(go.Bar(x=merged['LapNumber'],y=merged['Delta'],marker_color=[tc(t1) if v>0 else tc(t2) for v in merged['Delta']]))
            fig_d.add_hline(y=0,line_color='#fff',line_width=1)
            fig_d.update_layout(template='plotly_dark',paper_bgcolor='#111',plot_bgcolor='#141414',height=260,
                title=f"Lap Delta — {driver_name(hh_d1)} vs {driver_name(hh_d2)}",
                xaxis_title="Lap",yaxis_title="Gap (s)",
                annotations=[dict(x=0.01,y=0.95,xref='paper',yref='paper',text=f'Above zero = {driver_name(hh_d1)} slower that lap',showarrow=False,font=dict(color='#888',size=11))])
            st.plotly_chart(fig_d,use_container_width=True)
            st.markdown("### Tyre Strategy")
            tc1c,tc2c=st.columns(2)
            for col,drv,data in [(tc1c,hh_d1,d1d),(tc2c,hh_d2,d2d)]:
                with col:
                    st.markdown(f"**{driver_name(drv)}**")
                    stints=data.groupby(['Stint','Compound']).agg(Laps=('LapNumber','count'),Avg=('LapTimeSeconds','mean')).reset_index()
                    for _,s in stints.iterrows():
                        color=COMPOUND_COLORS.get(s['Compound'],'#aaa')
                        st.markdown(f'<div style="background:#141414;border-left:4px solid {color};padding:8px 12px;margin-bottom:6px;border-radius:4px;"><span style="color:{color};font-weight:700;">{s["Compound"]}</span><span style="color:#888;font-size:.85rem;margin-left:8px;">Stint {int(s["Stint"])} · {int(s["Laps"])} laps · avg {to_laptime(s["Avg"])}</span></div>', unsafe_allow_html=True)
        else: st.info("No data for this selection.")

    with ana_tabs[4]:
        st.markdown("## Driver Performance Across Seasons")
        ds_driver=st.selectbox("Driver",sorted(r_le_driver.classes_,key=driver_sort_key),format_func=driver_name,key='ds_driver')
        ds_year=st.selectbox("Season",sorted(race_df['Year'].unique(),reverse=True),key='ds_year')
        ds_cal=calendar[calendar['Year']==ds_year].sort_values('Round')
        ds_race_opts={r['OfficialName']:f"{race_flag(r['OfficialName'])} {r['OfficialName']}" for _,r in ds_cal.iterrows()}
        ds_race_official=st.selectbox("Circuit",list(ds_race_opts.keys()),format_func=lambda x:ds_race_opts[x],key='ds_race')
        ds_race=get_race_name(ds_race_official,ds_year) or ds_race_official
        drv_all=race_df[race_df['Driver']==ds_driver]
        if not drv_all.empty:
            circ_avg=drv_all.groupby('Race').apply(lambda x:(x['LapTimeSeconds'].mean()-race_df[race_df['Race']==x.name]['LapTimeSeconds'].mean())/max(race_df[race_df['Race']==x.name]['LapTimeSeconds'].std(),0.001)).sort_values()
            best_tracks=circ_avg.head(3).index.tolist()
            if best_tracks:
                st.markdown("**🏆 Strongest Circuits:**")
                st.markdown(' '.join([f'<span style="background:#0d1a0d;border:1px solid #39b54a;border-radius:4px;padding:4px 10px;font-size:.85rem;color:#39b54a;margin:2px;display:inline-block;">🏁 {t}</span>' for t in best_tracks]),unsafe_allow_html=True)
        t_data=race_df[(race_df['Driver']==ds_driver)&(race_df['Race']==ds_race)].copy()
        if not t_data.empty:
            avg_by_year=t_data.groupby('Year')['LapTimeSeconds'].mean().reset_index()
            fast_by_year=t_data.groupby('Year')['LapTimeSeconds'].min().reset_index()
            all_avg=race_df[race_df['Race']==ds_race].groupby('Driver')['LapTimeSeconds'].mean()
            if all_avg.idxmin()==ds_driver:
                st.success(f"🏆 {ds_race} is {driver_name(ds_driver)}'s best circuit — lowest avg lap time of any driver across all seasons.")
            dt=t_data.sort_values('Year',ascending=False)['TeamName'].iloc[0]; bc=tc(dt)
            col_a,col_b=st.columns(2)
            with col_a:
                fig_t=px.bar(avg_by_year,x='Year',y='LapTimeSeconds',template='plotly_dark',title=f"{driver_name(ds_driver)} avg lap at {ds_race}")
                fig_t.update_traces(marker_color=bc); fig_t.update_layout(paper_bgcolor='#111',plot_bgcolor='#141414',height=350)
                st.plotly_chart(fig_t,use_container_width=True)
            with col_b:
                fig_f=px.line(fast_by_year,x='Year',y='LapTimeSeconds',markers=True,template='plotly_dark',title=f"{driver_name(ds_driver)} fastest lap at {ds_race}")
                fig_f.update_traces(line_color=bc,marker_color=bc); fig_f.update_layout(paper_bgcolor='#111',plot_bgcolor='#141414',height=350)
                st.plotly_chart(fig_f,use_container_width=True)
            ly=avg_by_year['Year'].max()
            ldf=race_df[(race_df['Race']==ds_race)&(race_df['Year']==ly)]
            all_da=ldf.groupby(['Driver','TeamName'])['LapTimeSeconds'].mean().reset_index().sort_values('LapTimeSeconds')
            st.markdown(f"### All Drivers — {ds_race} {ly}")
            fig_all=go.Figure()
            for _,row in all_da.iterrows():
                fig_all.add_trace(go.Bar(x=[driver_name(row['Driver'])],y=[row['LapTimeSeconds']],marker_color=tc(row['TeamName']),showlegend=False))
            ym=all_da['LapTimeSeconds'].min()*.995; ymx=all_da['LapTimeSeconds'].max()*1.005
            fig_all.update_layout(template='plotly_dark',paper_bgcolor='#111',plot_bgcolor='#141414',height=350,yaxis_range=[ym,ymx])
            st.plotly_chart(fig_all,use_container_width=True)
            deg=t_data.groupby(['Compound','TyreLife'])['LapTimeSeconds'].mean().reset_index()
            fig_deg=px.line(deg,x='TyreLife',y='LapTimeSeconds',color='Compound',template='plotly_dark',color_discrete_map=COMPOUND_COLORS,title=f"{driver_name(ds_driver)} tyre degradation at {ds_race}")
            fig_deg.update_layout(paper_bgcolor='#111',plot_bgcolor='#141414',height=350)
            st.plotly_chart(fig_deg,use_container_width=True)
        else: st.info(f"No data for {driver_name(ds_driver)} at {ds_race}.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_method:
    st.markdown("## ℹ️ Methodology")
    st.markdown("*How this project works — data sources, modelling approach, and honest limitations.*")
    st.divider()
    mc1,mc2=st.columns([2,1])
    with mc1:
        st.markdown("### Data Source")
        st.markdown("All data comes from **FastF1** — an open-source Python library interfacing with the official F1 timing API. This provides lap-by-lap telemetry, weather, tyre data, and session results for every race from 2018 onwards. This project uses **2022–2025** — the current ground effect era.")
        st.markdown("### Why 2022 Onwards?")
        st.markdown("F1 introduced radical new technical regulations in 2022, switching to ground effect aerodynamics. This fundamentally changed tyre degradation, car balance, and pace differentials. Training across eras would introduce noise — a 2019 Mercedes and a 2024 Mercedes are essentially different machines.")
        st.markdown("### Feature Engineering")
        st.markdown("Raw lap times are not comparable across circuits. A 1:28 at Monaco and a 1:28 at Monza mean completely different things. Lap times are **normalised per race** using z-score standardisation: `normalised = (lap_time − mean) / std`. This lets the model learn relative pace patterns rather than absolute times.\n\n**Features:** Driver · Team · Grid Position · Lap Number (fuel proxy) · Tyre Compound · Tyre Life · Air Temp · Track Temp · Stint · Circuit · Year")
        st.markdown("### Model: XGBoost")
        st.markdown("XGBoost was chosen over linear regression (can't capture non-linear tyre deg curves), neural networks (overkill for tabular data), and Random Forest (boosting outperformed bagging on validation). **300 estimators · learning rate 0.05 · max depth 6**")
        st.markdown("### Race Simulator")
        st.markdown("""Strategy multipliers:
| Strategy | Early | Late |
|---|---|---|
| Aggressive (Soft→Hard) | +0.3s faster | -0.15s slower |
| Balanced (Medium→Medium) | Baseline | Baseline |
| Conservative (Hard→Soft) | -0.2s slower | +0.25s faster |

DNF probabilities combine driver error history and constructor mechanical failure rates, enabling "what if" scenarios.""")
        st.markdown("### Known Limitations")
        st.markdown("Safety cars not modelled · Fuel load approximated by lap number · Driver form variance not captured · Mid-race weather changes not modelled · Simulator is pace-based only")
    with mc2:
        st.markdown("### Performance")
        for label,val,color,subtitle in [
            ("Race Model MAE","0.37 σ","#e10600","≈ 0.4s across 25 circuits"),
            ("Qualifying MAE","0.40 σ","#3671C6","≈ 0.4s across qualifying"),
            ("Race Laps","62,000+","#39b54a","2022–2025 seasons"),
            ("Qual Laps","8,000+","#FF8000","2022–2025 seasons"),
            ("Circuits","25","#27F4D2","Full F1 calendar"),
            ("Seasons","4","#FF87BC","Ground effect era"),
        ]:
            st.markdown(f'<div style="background:#141414;border:1px solid #1a1a1a;border-left:3px solid {color};border-radius:6px;padding:14px 16px;margin-bottom:8px;"><div style="color:#888;font-size:.7rem;text-transform:uppercase;letter-spacing:2px;">{label}</div><div style="font-size:1.5rem;font-weight:900;color:{color};margin:4px 0;">{val}</div><div style="color:#666;font-size:.8rem;">{subtitle}</div></div>', unsafe_allow_html=True)
        st.markdown("### Stack")
        for tech in ["Python 3.12","FastF1 3.8","XGBoost","scikit-learn","Streamlit","Plotly","pandas"]:
            st.markdown(f'<span style="display:inline-block;background:#141414;border:1px solid #222;border-radius:4px;padding:3px 10px;font-size:.8rem;color:#888;margin:2px;">{tech}</span>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ABOUT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_about:
    st.markdown("""
<div style="text-align:center;padding:40px 0 24px;">
    <div style="font-family:'Orbitron',monospace;font-size:1.8rem;font-weight:900;letter-spacing:4px;color:#fff;">ABOUT THIS PROJECT</div>
    <div style="color:#333;letter-spacing:2px;font-size:.8rem;margin-top:8px;text-transform:uppercase;">Built by [Your Name] · [Your Role] · [Location]</div>
</div>
""", unsafe_allow_html=True)
 
    col1, col2 = st.columns([3, 2])
 
    with col1:
        st.markdown("""
<div style="background:#141414;border:1px solid #1a1a1a;border-left:3px solid #e10600;border-radius:8px;padding:28px;margin-bottom:16px;">
<h3 style="color:#fff;margin-top:0;">Hi, I'm Nishit Kumar! 👋</h3>
<p style="color:#aaa;line-height:1.8;">I'm a student based in London. I built this project to combine two things I care about: Formula 1 and data science. What started as a lap time predictor turned into a full analytics platform with a season simulation game.</p>
<p style="color:#aaa;line-height:1.8;">I'm currently finishing up my MSc Finance, and I spend my time either learning to code or watching F1, cricket, or football.</p>
<p style="color:#aaa;line-height:1.8;">This project covers 62,000+ race laps across 4 seasons using FastF1 data, an XGBoost regression model with ~0.4s MAE, and a Streamlit frontend with Plotly visualisations.</p>
</div>
""", unsafe_allow_html=True)
 
 
        st.markdown("""
<div style="background:#141414;border:1px solid #1a1a1a;border-left:3px solid #39b54a;border-radius:8px;padding:28px;">
<h3 style="color:#fff;margin-top:0;">Connect</h3>
<p style="color:#aaa;line-height:1.8;">Always open to talking data, F1, or new opportunities.</p>
<div style="margin-top:12px;display:flex;gap:12px;flex-wrap:wrap;">
<a href="https://linkedin.com/in/nishit-kumar-singhal" target="_blank" style="background:#0077b5;color:#fff;padding:8px 18px;border-radius:4px;text-decoration:none;font-weight:700;font-size:.85rem;letter-spacing:1px;">LinkedIn</a>
<a href="https://github.com/nksinghal1" target="_blank" style="background:#333;color:#fff;padding:8px 18px;border-radius:4px;text-decoration:none;font-weight:700;font-size:.85rem;letter-spacing:1px;">GitHub</a>
<a href="mailto:ns160902@gmail.COM" style="background:#e10600;color:#fff;padding:8px 18px;border-radius:4px;text-decoration:none;font-weight:700;font-size:.85rem;letter-spacing:1px;">Email</a>
</div>
</div>
""", unsafe_allow_html=True)
 
    with col2:
        st.markdown("### Tech Stack")
        for tech, color in [
            ("Python 3.12", "#e10600"), ("FastF1 3.8", "#FF8000"),
            ("XGBoost", "#39b54a"), ("scikit-learn", "#3671C6"),
            ("pandas", "#27F4D2"), ("Streamlit", "#FF87BC"), ("Plotly", "#9B59B6")
        ]:
            st.markdown(
                f'<div style="background:#0d0d0d;border:1px solid #1a1a1a;border-left:3px solid {color};'
                f'border-radius:4px;padding:8px 14px;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;">'
                f'<span style="color:#fff;font-weight:600;">{tech}</span>'
                f'<span style="width:8px;height:8px;border-radius:50%;background:{color};display:inline-block;box-shadow:0 0 8px {color};"></span></div>',
                unsafe_allow_html=True
            )
 
        st.markdown("### Project Stats")
        for val, label, color in [
            ("62,000+", "Race Laps", "#e10600"), ("8,000+", "Qual Laps", "#3671C6"),
            ("25", "Circuits", "#27F4D2"), ("4", "Seasons", "#FF8000"),
            ("0.37σ", "Model MAE", "#39b54a"), ("11", "Features", "#FF87BC")
        ]:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:8px 0;border-bottom:1px solid #1a1a1a;">'
                f'<span style="color:#888;font-size:.85rem;">{label}</span>'
                f'<span style="color:{color};font-weight:900;font-size:1.1rem;">{val}</span></div>',
                unsafe_allow_html=True
            )
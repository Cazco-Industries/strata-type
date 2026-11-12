"""Read-only app source inventory. No app imports or dev servers are executed."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from common import ROOT, dump, digest

WEATHER = ROOT.parent / 'strata-weather'

def semantic(name):
    name=re.sub(r'Icon$', '', name)
    name=re.sub(r'([a-zA-Z])(\d)',r'\1-\2',name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', re.sub(r'([A-Z]+)([A-Z][a-z])',r'\1-\2',name)).lower()


def main():
    p=argparse.ArgumentParser();p.add_argument('--weather',type=Path,default=WEATHER);args=p.parse_args()
    weather=args.weather.resolve()
    data=json.loads(subprocess.check_output(['node',str(ROOT/'scripts/scan_icons.mjs'),str(weather)],text=True))
    for icon in data['icons']:icon['semantic_name']=semantic(icon['name'])
    base=weather/'packages/ui/src'
    glyph=base/'condition-glyph.ts'
    conditions=re.findall(r'"([a-z-]+)"',glyph.read_text().split('const severity')[0])
    catalog=base/'weather-icons/weather-icons-catalog.ts'
    names=set(re.findall(r'"([a-z0-9-]+)"',catalog.read_text().split('export const WEATHER_ICON_NAMES = [',1)[1].split('] as const',1)[0]))
    selected=[base/'weather-icons/resolve-weather-icon.ts',base/'weather-icons/nws-map.ts']
    used={}
    for f in selected:
        for n in re.findall(r'"([a-z0-9-]+)"',f.read_text()):
            if n in names:used.setdefault(n,set()).add(str(f.relative_to(weather)))
    # Direct JSX references; the gallery/catalog enumeration is kept separate.
    for path in subprocess.check_output(['rg','-l','--glob','*.tsx','--glob','!**/node_modules/**','--glob','!**/.next/**','WeatherIcon',str(weather/'apps'),str(weather/'packages')],text=True).splitlines():
        f=Path(path)
        for n in re.findall(r'<WeatherIcon\b[^>]*?\bname=["\']([^"\']+)["\']',f.read_text()):
            if n in names:used.setdefault(n,set()).add(str(f.relative_to(weather)))
    required=[]
    for phase in ['day','night']:
        required += [f'{state}-{phase}' for state in ['clear','partly-cloudy','cloudy','fog','haze','drizzle','rain-light','rain','rain-heavy','snow-light','snow','snow-heavy','sleet','freezing-rain','hail','thunderstorm']]
    required += ['wind-calm','wind-gust','wind-direction','wind-strong','alert-watch','alert-warning','alert-advisory','alert-emergency','uv-low','uv-moderate','uv-high','uv-very-high','uv-extreme','air-quality-good','air-quality-moderate','air-quality-unhealthy-sensitive','air-quality-unhealthy','air-quality-very-unhealthy','air-quality-hazardous','tide-high','tide-low','tide-rising','tide-falling']
    required += [f'moon-{phase}' for phase in ['new','waxing-crescent','first-quarter','waxing-gibbous','full','waning-gibbous','third-quarter','waning-crescent']]
    aliases={'day-sunny':'clear-day','night-clear':'clear-night','day-cloudy':'partly-cloudy-day','night-partly-cloudy':'partly-cloudy-night','night-cloudy':'partly-cloudy-night','sprinkle':'drizzle','snowflake-cold':'cold','strong-wind':'wind-strong','windy':'wind','day-haze':'haze-day','night-fog':'fog-night','night-rain':'rain-night','night-hail':'hail-night','night-sleet':'sleet-night','day-showers':'showers-day','night-showers':'showers-night','night-sprinkle':'drizzle-night','day-sprinkle':'drizzle-day','day-sleet':'sleet-day','day-hail':'hail-day','night-thunderstorm':'thunderstorm-night','day-thunderstorm':'thunderstorm-day'}
    represented=set(conditions)|{aliases.get(n,n) for n in used}
    gaps=[{'semantic_name':n,'status':'not resolved as a distinct app condition today','catalog_available': any(aliases.get(k,k)==n for k in names)} for n in required if n not in represented]
    appfiles=[glyph,base/'condition-icon.tsx',base/'weather-icons/registry.ts',catalog,*selected]
    result={'schema':1,'app_commit':subprocess.check_output(['git','-C',str(weather),'rev-parse','HEAD'],text=True).strip(),
      'method':data['method'],'files_scanned':data['files_scanned'],'lucide':data['icons'],'manual_review':data['manual_review'],
      'condition_glyphs':[{'name':n,'semantic_name':n,'file':'packages/ui/src/condition-glyph.ts'} for n in sorted(set(conditions))],
      'nws_codes':{phase:dict(re.findall(r'\b([a-z_]+): "([a-z0-9-]+)"', (base/'weather-icons/nws-map.ts').read_text().split(f'NWS_WEATHER_ICON_{phase.upper()}_MAP')[1].split('});')[0])) for phase in ['day','night']},
      'erik_flowers_referenced':[{'name':n,'semantic_name':aliases.get(n,n),'files':sorted(files)} for n,files in sorted(used.items())],
      'erik_flowers_catalog':sorted(names),'gaps':gaps,'required_library':required,
      'evidence':{str(f.relative_to(weather)):digest(f) for f in appfiles}}
    result['counts']={'lucide_icons':len(data['icons']),'lucide_imports':sum(i['import_count'] for i in data['icons']),'lucide_usage_occurrences':sum(i['usage_count'] for i in data['icons']),'condition_glyphs':len(set(conditions)),'nws_codes':len(result['nws_codes']['day']),'erik_catalog':len(names),'erik_referenced':len(used),'library_gaps':len(gaps)}
    dump(ROOT/'inventory/icons.json',result)
    print(json.dumps(result['counts'],indent=2))

if __name__=='__main__':main()

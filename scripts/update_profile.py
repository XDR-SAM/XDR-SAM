"""Refresh public GitHub data and render repository-owned profile graphics."""
import argparse
import concurrent.futures
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'live'
USER = 'XDR-SAM'
TOKEN = os.environ.get('GITHUB_TOKEN')

def request(url, payload=None):
    headers = {'User-Agent': 'XDR-SAM-profile', 'Accept': 'application/vnd.github+json'}
    if TOKEN and url.startswith('https://api.github.com/'):
        headers['Authorization'] = f'Bearer {TOKEN}'
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=40) as response:
        return json.load(response)

class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.counts, self.tip, self.buffer = {}, {}, None, ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'td' and 'data-date' in a:
            self.cells[a['id']] = {'date': a['data-date'], 'level': int(a['data-level'])}
        if tag == 'tool-tip':
            self.tip, self.buffer = a.get('for'), ''
    def handle_data(self, data):
        if self.tip:
            self.buffer += data
    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tip:
            m = re.match(r'([\d,]+) contributions?', self.buffer.strip())
            if not m and not self.buffer.strip().startswith('No contributions'):
                raise ValueError('Unknown GitHub contribution tooltip format')
            self.counts[self.tip] = int(m[1].replace(',', '')) if m else 0
            self.tip = None

def public_calendar():
    req = urllib.request.Request(f'https://github.com/users/{USER}/contributions', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        parser = CalendarParser()
        parser.feed(r.read().decode())
    if len(parser.cells) < 350:
        raise ValueError('Incomplete public contribution calendar; preserving previous snapshot')
    return sorted([dict(v, count=parser.counts[k]) for k,v in parser.cells.items()], key=lambda d:d['date'])

def contribution_data():
    if not TOKEN:
        return public_calendar(), None
    query = '''query($login:String!) {user(login:$login) {contributionsCollection {
      totalCommitContributions contributionCalendar {weeks {contributionDays {date contributionCount}}}
    }}}'''
    result = request('https://api.github.com/graphql', {'query':query,'variables':{'login':USER}})
    if result.get('errors'):
        raise RuntimeError('GitHub GraphQL failed: '+str(result['errors']))
    c = result['data']['user']['contributionsCollection']
    days = [{'date':d['date'],'count':d['contributionCount']} for w in c['contributionCalendar']['weeks'] for d in w['contributionDays']]
    return days, c['totalCommitContributions']

def streaks(days, today):
    """UTC calendar days; allow an unfinished today to retain yesterday's streak."""
    counts = {date.fromisoformat(d['date']): d['count'] for d in days if d['date'] <= today.isoformat()}
    longest = run = 0
    previous = None
    for day in sorted(counts):
        run = run+1 if counts[day] and previous == day-timedelta(days=1) else int(counts[day]>0)
        longest = max(longest,run)
        previous = day
    day = today if counts.get(today,0)>0 else today-timedelta(days=1)
    current = 0
    while counts.get(day,0)>0:
        current += 1
        day -= timedelta(days=1)
    return current,longest

def collect():
    repos=[]
    for page in range(1, 21):
        batch=request(f'https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&per_page=100&page={page}')
        repos.extend(batch)
        if len(batch)<100:
            break
    else:
        raise ValueError('Repository pagination limit exceeded')
    original=[r for r in repos if not r['fork'] and not r['archived'] and r['name']!=USER]
    original.sort(key=lambda r:r['pushed_at'],reverse=True)
    sample=original[:30]
    languages={}
    def langs(repo):
        return request(repo['languages_url'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(langs,sample):
            for name,size in result.items():
                languages[name]=languages.get(name,0)+size
    days,commits=contribution_data()
    now=datetime.now(timezone.utc)
    days=sorted([d for d in days if d['date']<=now.date().isoformat()],key=lambda d:d['date'])
    current,longest=streaks(days,now.date())
    return {'updated':now.strftime('%Y-%m-%d %H:%M UTC'),'days':days,'commits':commits,
            'contributions':sum(d['count'] for d in days),'current_streak':current,'longest_streak':longest,
            'public_repos':len(repos),'stars':sum(r['stargazers_count'] for r in original),
            'language_sample':len(sample),'languages':languages,
            'projects':[{'name':r['name'],'url':r['html_url'],'description':r['description'],
                         'language':r['language'],'pushed':r['pushed_at'][:10]} for r in original[:6]]}

def svg(w,h,theme,title,body,css=''):
    bg,fg,muted,accent,line = ('#10130f','#f1f2e9','#a9b1a2','#c1f76d','#30392b') if theme=='dark' else ('#f4f5ed','#192313','#57634e','#44721a','#d6ddcd')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>
<style>:root{{--bg:{bg};--fg:{fg};--muted:{muted};--accent:{accent};--line:{line}}}text{{font-family:Arial,Helvetica,sans-serif;fill:var(--fg)}}.small{{fill:var(--muted);font-size:14px}}{css}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="var(--bg)" stroke="var(--line)"/>{body}</svg>'''

def t(x,y,s,size=16,cls=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}">{escape(str(s))}</text>'

def dashboard(d,theme,mobile=False):
    w,h=(640,570) if mobile else (1200,330)
    values=[('Contributions',d['contributions']),('Commit contributions',d['commits'] if d['commits'] is not None else 'Pending'),('Current streak',str(d['current_streak'])+'d'),('Longest streak',str(d['longest_streak'])+'d'),('Public repositories',d['public_repos']),('Stars / original repos',d['stars'])]
    out=[t(30,38,'GITHUB / ACTIVITY',16),t(30,65,'Rolling year · streaks use UTC contribution days',14,'small')]
    for i,(label,value) in enumerate(values):
        cols=2 if mobile else 3
        x=30+(i%cols)*(300 if mobile else 395)
        y=120+(i//cols)*(135 if mobile else 103)
        out.extend([t(x,y,str(value),44),t(x,y+28,label,14,'small')])
    out.append(t(30,h-22,'Updated '+d['updated'],14,'small'))
    return svg(w,h,theme,'GitHub activity statistics', ''.join(out))

def languages(d,theme):
    total=sum(d['languages'].values()) or 1
    entries=sorted(d['languages'].items(),key=lambda kv:-kv[1])[:6]
    out=[t(30,38,'LANGUAGE MIX',16),t(30,65,f'Code bytes · {d["language_sample"]} recently pushed, public, original repos',14,'small')]
    for i,(name,size) in enumerate(entries):
        y=104+i*44
        out.extend([t(30,y,name,17),t(520,y,f'{size/total:.1%}',16),f'<rect x="205" y="{y-13}" width="290" height="12" rx="6" fill="var(--line)"/><rect class="bar" x="205" y="{y-13}" width="{290*size/total:.2f}" height="12" rx="6" fill="var(--accent)"/>'])
    out.append(t(30,389,'Share of sampled bytes, not time spent or proficiency.',14,'small'))
    return svg(640,414,theme,'Most used languages by code bytes in sampled repositories',''.join(out),'.bar{animation:reveal 1.8s ease-out both;transform-origin:205px 0}@keyframes reveal{from{transform:scaleX(0)}to{transform:scaleX(1)}}')

def snake(d,theme):
    days=d['days']
    first=date.fromisoformat(days[0]['date'])
    start=first-timedelta(days=(first.weekday()+1)%7)
    mapped={((date.fromisoformat(day['date'])-start).days//7,(date.fromisoformat(day['date']).weekday()+1)%7):day for day in days}
    cols=max(x for x,y in mapped)+1
    step=20
    sequence=[(x,y) for y in range(7) for x in (range(cols) if y%2==0 else range(cols-1,-1,-1))]
    order={p:i for i,p in enumerate(sequence)}
    path='M'+' L'.join(f'{46+x*step},{91+y*step}' for x,y in sequence)
    length=(len(sequence)-1)*step
    colors=['var(--line)','#42582c','#648d36','#94c54b','var(--accent)']
    out=[t(30,36,'CONTRIBUTIONS / SNAKE',16),t(30,61,'Every square is a real contribution day. Follow the trail.',14,'small')]
    css=''
    maxcount=max(day['count'] for day in days) or 1
    for (x,y),day in mapped.items():
        idx=order[(x,y)]
        pct=round(96*idx/(len(sequence)-1),3)
        level=0 if not day['count'] else min(4,1+int(3*day['count']/maxcount))
        cls=f'c{idx}'
        if day['count']:
            css+=f'.{cls}{{animation:{cls} 40s linear infinite}}@keyframes {cls}{{0%,{max(0,pct-.01)}%{{opacity:1}}{pct}%,98%{{opacity:.12}}100%{{opacity:1}}}}'
        out.append(f'<rect class="{cls}" x="{38+x*step}" y="{83+y*step}" width="16" height="16" rx="4" fill="{colors[level]}"><title>{day["date"]}: {day["count"]} contributions</title></rect>')
    out.append(f'<path class="snake" d="{path}" fill="none" stroke="var(--accent)" stroke-width="10" stroke-linecap="round" stroke-dasharray="55 {length+80}" stroke-dashoffset="55"/>')
    css+=f'.snake{{animation:slither 40s linear infinite}}@keyframes slither{{0%{{stroke-dashoffset:55}}96%,100%{{stroke-dashoffset:-{length}}}}}'
    out.append(t(30,260,f'{d["contributions"]:,} contributions · '+days[0]['date']+' → '+days[-1]['date'],14,'small'))
    return svg(max(1160,cols*step+85),282,theme,'Animated snake traversing the real GitHub contribution calendar',''.join(out),css)

def markdown(value):
    value=' '.join(str(value or '').split())
    value=escape(value)
    return re.sub(r'([\\`*_|\[\]])',r'\\\1',value)

def render(d):
    OUT.mkdir(parents=True,exist_ok=True)
    for theme in ['dark','light']:
        for mobile in [False,True]:
            (OUT/f'stats-{theme}{"-mobile" if mobile else ""}.svg').write_text(dashboard(d,theme,mobile),encoding='utf-8')
        (OUT/f'languages-{theme}.svg').write_text(languages(d,theme),encoding='utf-8')
        (OUT/f'snake-{theme}.svg').write_text(snake(d,theme),encoding='utf-8')
    rows=['| Recently pushed project | Language | Last push (UTC) |','| :--- | :--- | :--- |']
    for p in d['projects']:
        label=markdown(p['name'])
        description=markdown(p['description'] or 'Explore the repository for project details.')
        if len(description)>160: description=description[:157]+'…'
        rows.append(f'| **[{label}]({p["url"]})**<br>{description} | {markdown(p["language"] or "—")} | {p["pushed"]} |')
    rows.append(f'\n<sub>Updated {d["updated"]} · Public, non-fork, non-archived repos, sorted by latest push. Automated pushes can also appear.</sub>')
    readme=ROOT/'README.md'
    content=readme.read_text(encoding='utf-8-sig')
    pattern=r'<!-- LATEST-PROJECTS:START -->.*?<!-- LATEST-PROJECTS:END -->'
    if len(re.findall(pattern,content,re.S))!=1:
        raise ValueError('README must have exactly one latest-projects marker pair')
    content=re.sub(pattern,lambda _: '<!-- LATEST-PROJECTS:START -->\n'+'\n'.join(rows)+'\n<!-- LATEST-PROJECTS:END -->',content,flags=re.S)
    readme.write_text(content,encoding='utf-8')
    (OUT/'snapshot.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--snapshot',type=Path,help='Render an existing snapshot without network access')
    args=parser.parse_args()
    data=json.loads(args.snapshot.read_text()) if args.snapshot else collect()
    render(data)
    print('Profile refreshed:',data['updated'])

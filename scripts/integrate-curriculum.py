#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'src/data/modules.json'
old=json.loads(path.read_text())
enriched_dir=ROOT/'src/data/enriched'
slugs=[item['slug'] for item in old]
slugs.extend(p.stem for p in sorted(enriched_dir.glob('*.json')) if p.stem not in slugs)
modules=[]
for slug in slugs:
    enriched=enriched_dir/f"{slug}.json"
    data=json.loads(enriched.read_text())
    item=next((module for module in old if module['slug']==slug),None)
    if item:
        for key in ('id','slug','title','category','lab'):
            assert data[key]==item[key], f'Identity changed: {slug} {key}'
    assert len(data['lessons']) >= (8 if slug=='p-values' else 6)
    video=data.get('video','')
    if video:
        assert (ROOT/'public'/video.lstrip('/')).is_file(), f'Missing video asset for {slug}: {video}'
    data['video']=video
    modules.append(data)
path.write_text(json.dumps(modules,ensure_ascii=False,indent=2)+'\n')

captions={
 'statistical-thinking':('One extreme observation can pull the mean away from most observations.','The median is usually less sensitive to the magnitude of one outlier.'),
 'probability':('A useful signal can still generate many false alarms when the event is rare.','Interpret the signal together with the base rate and false-positive rate.'),
 'distributions':('Repeated samples produce a distribution of sample means.','Under suitable assumptions, averages are less dispersed than individual returns.'),
 'estimation':('An estimate is surrounded by uncertainty, not a guarantee.','More information often narrows an interval when the model assumptions remain appropriate.'),
 'p-values':('A p-value changes continuously with the data under a specified model.','It is not the probability that the null hypothesis is true.'),
 'regression':('A regression line summarizes a relationship between inputs and outcomes.','Residuals compare observed and predicted outcomes at the same input value.'),
 'causal':('Two outcomes can move together because they share a common cause.','Association alone does not identify a causal effect.'),
 'time-series':('Quiet and turbulent periods can appear in clusters.','A rolling estimate describes local variation; it does not guarantee the next outcome.'),
 'returns-risk':('Returns compound by multiplication, not simple addition.','An equal percentage rise and fall do not cancel because their starting values differ.'),
 'portfolio':('Assets that move less synchronously can offset part of one another’s variation.','Diversification depends on covariance and weights; it does not eliminate all risk.'),
 'bayesian':('Start with a prior distribution, then combine it with evidence through a likelihood.','The posterior reflects both assumptions and observations, not the data alone.'),
 'backtesting':('Trying many uninformative strategies can still produce an apparent winner.','Keep all attempts visible and evaluate new data without reusing the test set.'),
 'kernel-density':('Each observed return receives a smooth kernel.','The overlapping kernels combine into a density estimate.'),
 'correlation':('Most paired points move together in this simulated example.','One distant point can change the correlation.')
}
for slug,(first,second) in captions.items():
    if not (ROOT/'public/videos'/f'{slug}.mp4').is_file():
        continue
    text=f'WEBVTT\n\n00:00.000 --> 00:05.000\n{first}\n\n00:05.000 --> 00:10.000\n{second}\n'
    (ROOT/'public/videos'/f'{slug}.vtt').write_text(text)
print(json.dumps({'modules':len(modules),'guided_lessons':sum(len(m['lessons']) for m in modules),'practice_blocks':sum(sum('practice' in l for l in m['lessons']) for m in modules),'word_count':sum(len(json.dumps(m,ensure_ascii=False).split()) for m in modules),'captions':len(captions)}))

import { betaBinomialPosterior, median, quantile } from "../utils/lab-math.mjs";
const NS = "http://www.w3.org/2000/svg";
type Inputs = Record<string, number>;
const palette = { ink:"#172239", navy:"#101a2b", coral:"#ef735e", coralSoft:"#f8c4bb", mint:"#5c9a7e", mintSoft:"#c6efdf", blue:"#7595c9", gold:"#eabf6b", grid:"#dfe4e8", muted:"#6b7484", white:"#fff", red:"#d85d4b" };
const make = (tag: string, attrs: Record<string,string|number> = {}) => {
  const node = document.createElementNS(NS, tag);
  for (const [key,value] of Object.entries(attrs)) node.setAttribute(key, String(value));
  return node;
};
function text(svg: SVGSVGElement, x: number, y: number, value: string, color=palette.muted, size=12, anchor="start", weight="500") {
  const item = make("text", { x,y,fill:color,"font-size":size,"font-family":"DM Sans, sans-serif","font-weight":weight,"text-anchor":anchor });
  item.textContent = value; svg.appendChild(item); return item;
}
function line(svg: SVGSVGElement,x1:number,y1:number,x2:number,y2:number,color=palette.grid,width=1,dash="") {
  const item=make("line",{x1,y1,x2,y2,stroke:color,"stroke-width":width}); if(dash)item.setAttribute("stroke-dasharray",dash); svg.appendChild(item); return item;
}
function path(svg:SVGSVGElement,points:Array<[number,number]>,color=palette.coral,width=3,fill="none") {
  if(!points.length)return;
  const d=points.map(([x,y],i)=>`${i?"L":"M"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
  const item=make("path",{d,fill,stroke:color,"stroke-width":width,"stroke-linecap":"round","stroke-linejoin":"round"}); svg.appendChild(item); return item;
}
function metric(container:HTMLElement,label:string,value:string,explain?:string) {
  const card=document.createElement("div");card.className="metric-card";card.setAttribute("data-metric",label);card.dataset.value=value;
  const l=document.createElement("span");l.className="metric-label";l.textContent=label;
  const v=document.createElement("span");v.className="metric-value";v.textContent=value;
  card.appendChild(l);card.appendChild(v);if(explain){const small=document.createElement("span");small.className="small";small.textContent=explain;card.appendChild(small)}container.appendChild(card);
}
function setExplanation(el:HTMLElement,html:string){el.innerHTML=html;}
function fmt(x:number,d=2){return Number.isFinite(x)?x.toFixed(d):"—";}
function normalCdf(x:number){const sign=x<0?-1:1;const z=Math.abs(x)/Math.sqrt(2);const t=1/(1+0.3275911*z);const erf=1-(((((1.061405429*t-1.453152027)*t+1.421413741)*t-0.284496736)*t+0.254829592)*t)*Math.exp(-z*z);return .5*(1+sign*erf);}
function seeded(seed:number){let a=seed>>>0;return()=>{a=(a*1664525+1013904223)>>>0;return a/4294967296;};}
function gaussian(rng:()=>number){const u=Math.max(1e-9,rng()),v=rng();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
function readControls(shell:HTMLElement):Inputs{const values:Inputs={};shell.querySelectorAll<HTMLInputElement>("[data-control]").forEach(input=>{values[input.dataset.control||""]=Number(input.value);const output=shell.querySelector<HTMLOutputElement>(`[data-range-output="${input.dataset.control}"]`);if(output)output.value=`${input.value}${input.dataset.suffix||""}`;});return values;}
function clearAndDraw(shell:HTMLElement,draw:(svg:SVGSVGElement,values:Inputs,results:HTMLElement,explain:HTMLElement)=>void){const svg=shell.querySelector<SVGSVGElement>("[data-chart]");const results=shell.querySelector<HTMLElement>("[data-results]");const explain=shell.querySelector<HTMLElement>("[data-explanation]");if(!svg||!results||!explain)return;svg.replaceChildren();results.replaceChildren();draw(svg,readControls(shell),results,explain);}
function frame(svg:SVGSVGElement, title:string, subtitle:string){text(svg,26,25,title,palette.ink,13,"start","700");text(svg,26,44,subtitle,palette.muted,10);}
function drawDescriptive(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Twenty-one daily changes + one movable shock day","Simulated daily yield changes · percentage points (pp)");
  const data=[-5.8,-4.2,-3.8,-3.1,-2.7,-2.1,-1.8,-1.3,-1.1,-.8,-.4,-.2,.1,.3,.6,.9,1.3,1.6,2.1,2.7,4.3];
  data.push(v.shock??8);
  const sorted=[...data].sort((a,b)=>a-b),mean=data.reduce((a,b)=>a+b,0)/data.length,med=median(data),q1=quantile(data,.25),q3=quantile(data,.75);
  const variance=data.reduce((a,b)=>a+(b-mean)**2,0)/(data.length-1),sd=Math.sqrt(variance),x0=60,x1=720,y=160,min=-14,max=20,X=(x:number)=>x0+(x-min)/(max-min)*(x1-x0);
  for(let tick=-10;tick<=20;tick+=5){const x=X(tick);line(svg,x,72,x,214,palette.grid,1);text(svg,x,235,String(tick),palette.muted,10,"middle");}
  line(svg,x0,y,x1,y,"#9da8b5",1.2);
  sorted.forEach((value,i)=>svg.appendChild(make("circle",{cx:X(value),cy:106+(i%3)*19,r:5.5,fill:value===(v.shock??8)?palette.coral:palette.blue,opacity:.88})));
  line(svg,X(mean),84,X(mean),211,palette.coral,3);line(svg,X(med),78,X(med),211,palette.mint,3);
  text(svg,Math.min(X(mean)+6,690),70,`Mean ${fmt(mean,1)} pp`,palette.coral,10,"start","700");text(svg,Math.min(X(med)+6,690),88,`Median ${fmt(med,1)} pp`,palette.mint,10,"start","700");
  text(svg,(x0+x1)/2,257,"Daily yield change (percentage points)",palette.ink,9,"middle","700");
  metric(r,"Mean",`${fmt(mean,2)} pp`);metric(r,"Median",`${fmt(med,2)} pp`);metric(r,"Sample SD",`${fmt(sd,2)} pp`);metric(r,"IQR",`${fmt(q3-q1,2)} pp`);
  setExplanation(e,`<strong>Read the graph:</strong> coral marks the mean and mint marks the median. The even-sample median averages its two central observations. An extreme observation often moves the mean and standard deviation more than the median and IQR; that is a robustness difference, not a reason to delete a genuine shock day.`);
}

function drawPvalue(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  const effect=v.effect??0,n=v.sampleSize??1,z=effect*Math.sqrt(n),p=Math.max(0,2*(1-normalCdf(Math.abs(z))));
  frame(svg,"Null reference distribution","Two-sided normal approximation · shaded tails are the p-value under H₀");
  const x0=55,x1=715,yTop=75,yBase=210,xMax=Math.max(5,Math.ceil(Math.abs(z)+1)),xMin=-xMax,X=(x:number)=>x0+(x-xMin)/(xMax-xMin)*(x1-x0),Y=(x:number)=>yBase-(Math.exp(-.5*x*x)/Math.sqrt(2*Math.PI))*300;
  for(const t of [-xMax,-xMax/2,0,xMax/2,xMax]){line(svg,X(t),yTop,X(t),yBase,palette.grid,1);text(svg,X(t),230,fmt(t,1),palette.muted,9,"middle");}
  line(svg,x0,yBase,x1,yBase,"#98a4b2",1);const points:Array<[number,number]>=[];
  for(let i=0;i<=180;i++){const x=xMin+i*(xMax-xMin)/180;points.push([X(x),Y(x)]);}path(svg,points,palette.blue,3);
  for(const sign of [-1,1]){const cutoff=Math.min(Math.abs(z),xMax),tailCutoff=sign*cutoff,region:Array<[number,number]>=[[X(sign===-1?xMin:tailCutoff),yBase]];for(let i=0;i<=40;i++){const x=sign===-1?xMin+i*(tailCutoff-xMin)/40:tailCutoff+i*(xMax-tailCutoff)/40;region.push([X(x),Y(x)]);}region.push([X(sign===-1?tailCutoff:xMax),yBase]);const d=region.map(([x,y],i)=>`${i?"L":"M"}${x} ${y}`).join(" ")+" Z";svg.appendChild(make("path",{d,fill:palette.coralSoft,opacity:.72,stroke:"none"}));}
  const obs=Math.max(xMin,Math.min(xMax,z));line(svg,X(obs),90,X(obs),yBase,palette.coral,3);svg.appendChild(make("circle",{cx:X(obs),cy:Y(obs),r:5.5,fill:palette.coral}));text(svg,X(obs),78,`z = ${fmt(z,2)}`,palette.coral,10,"middle","700");
  text(svg,(x0+x1)/2,257,"Null-model z statistic",palette.ink,9,"middle","700");const ylabel=text(svg,17,(yTop+yBase)/2,"Null density",palette.ink,8,"middle","600");ylabel.setAttribute("transform",`rotate(-90 17 ${(yTop+yBase)/2})`);
  metric(r,"Test statistic z",fmt(z,2));metric(r,"Two-sided p-value",p<.001?"< 0.001":fmt(p,3));metric(r,"Effect (SD units)",fmt(effect,2));metric(r,"Reference α","0.05");
  setExplanation(e,`<strong>Read the graph:</strong> the highlighted tails show how unusual the observed statistic would be <em>if H₀ and the model assumptions were true</em>. A smaller p-value is not the probability H₀ is true, nor a measure of effect size, practical value or causation.`);
}

function drawProbability(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"What does a positive signal mean?","Illustrative population of 1,000 cases · rates are user-controlled");const base=(v.baseRate||1)/100,sens=(v.sensitivity||0)/100,fpr=(v.falsePositive||0)/100;const total=1000,tp=Math.round(total*base*sens),fn=Math.round(total*base*(1-sens)),fp=Math.round(total*(1-base)*fpr),tn=total-tp-fn-fp,ppv=tp/(tp+fp||1);const x=55,w=650,y=90,h=48;const cols=[{n:tp,c:palette.mint,label:"True positive"},{n:fp,c:palette.coral,label:"False positive"},{n:tn,c:palette.blue,label:"True negative"},{n:fn,c:palette.gold,label:"Missed event"}];let cursor=x;cols.forEach(part=>{const width=w*part.n/total;svg.appendChild(make("rect",{x:cursor,y,width:Math.max(width,0),height:h,rx:2,fill:part.c}));cursor+=width;});
  text(svg,x,165,"1000 cases",palette.ink,11,"start","700");text(svg,x,190,`${tp} true alerts · ${fp} false alerts`,palette.muted,11);text(svg,x,220,"Positive predictive value",palette.ink,12,"start","700");svg.appendChild(make("rect",{x:x+200,y:205,width:390,height:18,rx:9,fill:"#e6e9ee"}));svg.appendChild(make("rect",{x:x+200,y:205,width:390*ppv,height:18,rx:9,fill:palette.coral}));text(svg,x+600,219,`${fmt(ppv*100,1)}%`,palette.coral,12,"end","700");
  metric(r,"Event base rate",`${fmt(base*100,1)}%`);metric(r,"True positive",String(tp));metric(r,"False positive",String(fp));metric(r,"Chance alert is real",`${fmt(ppv*100,1)}%`);
  setExplanation(e,`<strong>Read the graph:</strong> coral marks false alerts; mint marks true alerts. Even with ${fmt(sens*100,0)}% sensitivity, a low event base rate can make false positives a large share of all positive alerts. This is why the base rate belongs in the calculation.`);
}
function drawCLT(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Sampling distribution of the mean","Synthetic daily returns in percentage points · each mark is a repeated-sample mean");
  const n=Math.max(2,Math.round(v.sampleSize||30)),reps=Math.max(40,Math.round(v.repetitions||120)),rng=seeded(420+n*31),means:number[]=[];
  for(let j=0;j<reps;j++){let sum=0;for(let i=0;i<n;i++){let x=gaussian(rng);if(rng()<.035)x+=(rng()>.5?1:-1)*3.2;sum+=x;}means.push(sum/n);}
  const rawMin=Math.min(...means),rawMax=Math.max(...means),padding=Math.max(.08,(rawMax-rawMin)*.08),min=Math.floor((rawMin-padding)*4)/4,max=Math.ceil((rawMax+padding)*4)/4,x0=58,x1=710,y0=195,top=75,binN=18,bins=Array(binN).fill(0);
  means.forEach(m=>{const ix=Math.max(0,Math.min(binN-1,Math.floor((m-min)/(max-min)*binN)));bins[ix]++;});
  const maxBin=Math.max(...bins,1),bw=(x1-x0)/binN;bins.forEach((count,i)=>svg.appendChild(make("rect",{x:x0+i*bw+1,y:y0-count/maxBin*105,width:bw-2,height:count/maxBin*105,rx:3,fill:palette.blue,opacity:.82})));
  line(svg,x0,y0,x1,y0,"#98a4b2",1);for(let i=0;i<=4;i++){const tick=min+(max-min)*i/4,x=x0+i*(x1-x0)/4;line(svg,x,top,x,y0,palette.grid,1);text(svg,x,y0+18,fmt(tick,2),palette.muted,9,"middle");}
  const m=means.reduce((a,b)=>a+b,0)/means.length,sd=Math.sqrt(means.reduce((a,b)=>a+(b-m)**2,0)/(means.length-1)),zeroX=x0+(0-min)/(max-min)*(x1-x0);if(zeroX>=x0&&zeroX<=x1)line(svg,zeroX,top,zeroX,y0,palette.coral,2,"4 4");
  text(svg,(x0+x1)/2,255,"Sample mean (percentage points)",palette.ink,9,"middle","700");const ylabel=text(svg,16,(top+y0)/2,"Count of repeated samples",palette.ink,8,"middle","600");ylabel.setAttribute("transform",`rotate(-90 16 ${(top+y0)/2})`);
  metric(r,"n per sample",String(n));metric(r,"Repeated samples",String(reps));metric(r,"Mean of means (pp)",`${fmt(m,3)} pp`);metric(r,"Spread of means (pp)",`${fmt(sd,3)} pp`);
  setExplanation(e,`<strong>Read the graph:</strong> these bars show repeated <em>sample means</em>, not raw daily returns. The horizontal scale expands to include every simulated mean rather than folding outlying means into an edge bin. Larger n usually concentrates means under these simulation assumptions; the CLT does not promise real returns are normal or that tail losses disappear.`);
}

function drawConfidence(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  const n=Math.max(2,Math.round(v.sampleSize||64)),sigma=v.sigma||4,mu=.6,margin=1.96*sigma/Math.sqrt(n),rng=seeded(77+n*13+Math.round(sigma*10)),intervals:Array<{estimate:number,lo:number,hi:number,ok:boolean}>=[];
  for(let i=0;i<24;i++){const estimate=mu+gaussian(rng)*sigma/Math.sqrt(n),lo=estimate-margin,hi=estimate+margin;intervals.push({estimate,lo,hi,ok:lo<=mu&&hi>=mu});}
  const min=Math.min(-4,...intervals.map(q=>q.lo))-0.25,max=Math.max(5,...intervals.map(q=>q.hi))+0.25,x0=75,x1=710,X=(x:number)=>x0+(x-min)/(max-min)*(x1-x0);frame(svg,"Twenty-four confidence intervals from repeated samples","Fixed simulated population mean μ = 0.6 pp/month · green intervals cover it");
  let covered=0;intervals.forEach((item,i)=>{if(item.ok)covered++;const y=66+i*6.1;line(svg,X(item.lo),y,X(item.hi),y,item.ok?palette.mint:palette.coral,2);svg.appendChild(make("circle",{cx:X(item.estimate),cy:y,r:2.5,fill:item.ok?palette.mint:palette.coral}));});
  line(svg,X(mu),55,X(mu),222,palette.navy,2,"4 4");text(svg,X(mu)+7,52,"True μ",palette.navy,10,"start","700");for(let i=0;i<=4;i++){const tick=min+(max-min)*i/4,x=x0+i*(x1-x0)/4;line(svg,x,223,x,230,palette.muted,1);text(svg,x,247,fmt(tick,1),palette.muted,9,"middle");}
  text(svg,(x0+x1)/2,263,"Monthly estimate (percentage points)",palette.ink,8,"middle","700");metric(r,"Sample size",String(n));metric(r,"Standard error",`${fmt(sigma/Math.sqrt(n),2)} pp/month`);metric(r,"Reference limits μ ± 1.96 SE",`${fmt(mu-margin,2)} to ${fmt(mu+margin,2)} pp`);metric(r,"Covering intervals",`${covered} of 24`);
  setExplanation(e,`<strong>Read the graph:</strong> the dashed line is the fixed simulated population mean; each horizontal segment is one interval from a new sample. The highlighted metric gives the reference μ ± 1.96 SE limits, not a confidence interval estimated from one sample. A 95% method aims to cover the parameter in about 95% of repeated samples under its assumptions.`);
}

function drawRegression(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Synthetic market-factor example","Monthly fund excess return vs. market excess return · association only");const n=Math.max(8,Math.round(v.sampleSize||24)),noise=v.noise||8,rng=seeded(193+n*11+noise*19),data:Array<[number,number]>=[];
  for(let i=0;i<n;i++){const x=-2+4*i/(n-1),y=.25+.85*x+gaussian(rng)*noise/10;data.push([x,y]);}
  const mx=data.reduce((s,p)=>s+p[0],0)/n,my=data.reduce((s,p)=>s+p[1],0)/n,slope=data.reduce((s,p)=>s+(p[0]-mx)*(p[1]-my),0)/data.reduce((s,p)=>s+(p[0]-mx)**2,0),intercept=my-slope*mx,xmin=-2.2,xmax=2.2,fit=[intercept+slope*xmin,intercept+slope*xmax],allY=[...data.map(p=>p[1]),...fit],pad=Math.max(.2,(Math.max(...allY)-Math.min(...allY))*.08),ymin=Math.floor((Math.min(...allY)-pad)*2)/2,ymax=Math.ceil((Math.max(...allY)+pad)*2)/2,x0=78,x1=700,y0=215,y1=68,X=(x:number)=>x0+(x-xmin)/(xmax-xmin)*(x1-x0),Y=(y:number)=>y0-(y-ymin)/(ymax-ymin)*(y0-y1);
  for(let t=-2;t<=2;t++){line(svg,X(t),y1,X(t),y0,palette.grid,1);text(svg,X(t),y0+17,String(t),palette.muted,9,"middle");}
  for(let i=0;i<=4;i++){const t=ymin+(ymax-ymin)*i/4,yy=Y(t);line(svg,x0,yy,x1,yy,palette.grid,1);text(svg,x0-8,yy+3,fmt(t,1),palette.muted,8,"end");}
  line(svg,x0,y1,x0,y0,"#98a4b2",1);line(svg,x0,y0,x1,y0,"#98a4b2",1);data.forEach(([x,y])=>svg.appendChild(make("circle",{cx:X(x),cy:Y(y),r:4,fill:palette.blue,opacity:.83})));path(svg,[[X(xmin),Y(intercept+slope*xmin)],[X(xmax),Y(intercept+slope*xmax)]],palette.coral,3);
  text(svg,(x0+x1)/2,257,"Market excess return (pp)",palette.ink,9,"middle","700");const ylabel=text(svg,18,(y0+y1)/2,"Fund excess return (pp)",palette.ink,8,"middle","600");ylabel.setAttribute("transform",`rotate(-90 18 ${(y0+y1)/2})`);
  metric(r,"Estimated slope",fmt(slope,2),"fund pp per market pp");metric(r,"Intercept",`${fmt(intercept,2)} pp`);metric(r,"Observations",String(n));metric(r,"Noise SD",`${fmt(noise/10,1)} pp`);setExplanation(e,`<strong>Read the graph:</strong> the coral line is the least-squares fit. Its slope is an estimated association per percentage point of market return. The plot expands its outcome axis to include all points and fitted endpoints. The points are simulated; the chart does not establish that a market move caused an individual fund return.`);
}

function drawCausal(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"A hidden common cause can create an association","Hypothesized arrows are assumptions to examine—not facts established by a chart");const conf=(v.confounding||0)/100;const nodes=[{id:"U",x:180,y:100,label:"U · common cause",sub:"e.g. risk appetite"},{id:"X",x:400,y:70,label:"X · exposure",sub:"e.g. fund choice"},{id:"Y",x:610,y:145,label:"Y · outcome",sub:"e.g. return"}];const arrow=(a:any,b:any,width:number,color:string,dash="")=>{const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy),ux=dx/len,uy=dy/len,x1=a.x+ux*60,y1=a.y+uy*24,x2=b.x-ux*66,y2=b.y-uy*25;const ln=line(svg,x1,y1,x2,y2,color,width,dash);ln.setAttribute("marker-end","url(#arrowHead)");};const defs=make("defs");const marker=make("marker",{id:"arrowHead",markerWidth:8,markerHeight:8,refX:6,refY:3,orient:"auto"});marker.appendChild(make("path",{d:"M0,0 L0,6 L6,3 z",fill:palette.muted}));defs.appendChild(marker);svg.appendChild(defs);arrow(nodes[0],nodes[1],1+conf*3,palette.coral);arrow(nodes[0],nodes[2],1+conf*3,palette.coral);arrow(nodes[1],nodes[2],2.5,palette.mint);nodes.forEach(node=>{svg.appendChild(make("rect",{x:node.x-62,y:node.y-25,width:124,height:50,rx:14,fill:node.id==="U"?"#fff0ec":node.id==="X"?"#f0f2f7":"#e8f7ef",stroke:node.id==="U"?palette.coral:node.id==="X"?palette.blue:palette.mint,"stroke-width":1.5}));text(svg,node.x,node.y-2,node.label,palette.ink,11,"middle","700");text(svg,node.x,node.y+15,node.sub,palette.muted,9,"middle");});text(svg,383,232,"Adjusting for a pre-treatment confounder may block a backdoor path; careless adjustment can also add bias.",palette.muted,10,"middle");metric(r,"Illustrative arrow emphasis",`${fmt(conf*100,0)}%`);metric(r,"Observed association","Not causal proof");metric(r,"Design needed","Credible comparison");setExplanation(e,`<strong>Read the graph:</strong> the coral arrows show hypothesized common-cause paths; the mint arrow is the direct effect being asked about. The arrows encode a causal story that must be defended with design and subject knowledge. A small p-value cannot verify the diagram.`);
}
function drawVolatility(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Simulated returns with clustered volatility","Bars: daily return · coral line: rolling sample SD · synthetic, not market data");
  const n=100,window=Math.max(5,Math.round(v.window||20)),rng=seeded(938),returns:number[]=[];
  for(let i=0;i<n;i++){const regime=(i>34&&i<52)||(i>75&&i<87)?2.2:.55;returns.push(gaussian(rng)*regime+(i>34&&i<52&&i%5===0?1.3:0));}
  const rolling:number[]=[];for(let i=0;i<n;i++){const arr=returns.slice(Math.max(0,i-window+1),i+1),m=arr.reduce((a,b)=>a+b,0)/arr.length;rolling.push(Math.sqrt(arr.reduce((a,b)=>a+(b-m)**2,0)/Math.max(1,arr.length-1)));}
  const x0=72,x1=676,mid=143,base=212,top=76,X=(i:number)=>x0+i/(n-1)*(x1-x0),returnMax=Math.max(1,...returns.map(Math.abs)),scale=(mid-top-8)/returnMax,volMax=Math.max(...rolling,1e-6),volY=(val:number)=>base-val/volMax*(base-top);
  svg.appendChild(make("rect",{x:X(35),y:top,width:X(52)-X(35),height:base-top,fill:palette.coralSoft,opacity:.18}));
  for(let i=0;i<n;i++){const y=mid-returns[i]*scale;svg.appendChild(make("line",{x1:X(i),y1:mid,x2:X(i),y2:y,stroke:returns[i]>=0?palette.blue:palette.gold,"stroke-width":3,opacity:.85}));}
  const pts=rolling.map((val,i)=>[X(i),volY(val)] as [number,number]);path(svg,pts,palette.coral,2.6);line(svg,x0,mid,x1,mid,"#a1aab5",1);line(svg,x1,top,x1,base,palette.muted,1);
  for(const q of [-returnMax,0,returnMax]){const y=mid-q*scale;line(svg,x0-3,y,x0,y,palette.muted,1);text(svg,x0-6,y+3,fmt(q,1),palette.muted,7,"end");}
  for(const q of [0,volMax/2,volMax]){const y=volY(q);line(svg,x1,y,x1+4,y,palette.muted,1);text(svg,x1+7,y+3,fmt(q,1),palette.muted,7,"start");}
  text(svg,X(38),top+14,"higher-volatility patch",palette.red,8,"middle","700");text(svg,(x0+x1)/2,254,"Trading-day index",palette.ink,9,"middle","700");const yLeft=text(svg,18,(top+base)/2,"Daily return (pp)",palette.ink,8,"middle","600");yLeft.setAttribute("transform",`rotate(-90 18 ${(top+base)/2})`);const yRight=text(svg,749,(top+base)/2,"Rolling SD (pp)",palette.ink,8,"middle","600");yRight.setAttribute("transform",`rotate(-90 749 ${(top+base)/2})`);
  const recent=rolling.slice(-10).reduce((a,b)=>a+b,0)/10;metric(r,"Rolling window",`${window} days`);metric(r,"Recent realized σ",`${fmt(recent,2)} pp`);metric(r,"Max rolling σ",`${fmt(volMax,2)} pp`);metric(r,"Series type","Simulated");setExplanation(e,`<strong>Read the graph:</strong> the left axis gives signed daily returns and the right axis gives rolling sample standard deviation, both in percentage points. Bars and the coral line use separate, explicitly labeled scales. The synthetic patch makes clustering visible; volatility describes magnitude, not the sign of the next move.`);
}

function drawReturns(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Two-period wealth path","Each control is a simple return · wealth starts at index 100");const a=(v.returnA??0)/100,b=(v.returnB??0)/100,w0=100,w1=w0*(1+a),w2=w1*(1+b),cum=w2/w0-1,logA=Math.log(1+a),logB=Math.log(1+b),cumLog=logA+logB,vals=[w0,w1,w2],x=[120,380,640],min=Math.min(...vals),max=Math.max(...vals),pad=Math.max(2,(max-min)*.2),lo=min-pad,hi=max+pad,Y=(n:number)=>210-(n-lo)/(hi-lo)*120;
  for(let i=0;i<=2;i++){const value=lo+(hi-lo)*i/2,y=Y(value);line(svg,72,y,700,y,palette.grid,1);text(svg,66,y+3,fmt(value,1),palette.muted,8,"end");}
  line(svg,75,210,700,210,"#98a4b2",1);vals.forEach((val,i)=>{const color=i===0?palette.blue:i===1?palette.mint:palette.coral;svg.appendChild(make("circle",{cx:x[i],cy:Y(val),r:10,fill:color}));text(svg,x[i],Y(val)-18,fmt(val,2),palette.ink,13,"middle","700");text(svg,x[i],236,["Start","After period 1","After period 2"][i],palette.muted,10,"middle");if(i<2)line(svg,x[i]+10,Y(val),x[i+1]-10,Y(vals[i+1]),palette.blue,2);});
  text(svg,380,258,"Holding period",palette.ink,9,"middle","700");const ylabel=text(svg,17,145,"Wealth index",palette.ink,8,"middle","600");ylabel.setAttribute("transform","rotate(-90 17 145)");metric(r,"Cumulative simple return",`${fmt(cum*100,2)}%`);metric(r,"Simple returns added",`${fmt((a+b)*100,2)}%`);metric(r,"Sum of log returns",`${fmt(cumLog*100,2)} log points`);metric(r,"Final wealth",fmt(w2,2));setExplanation(e,`<strong>Read the graph:</strong> simple returns compound multiplicatively; log returns add and map back to the same cumulative wealth when all gross returns are positive. The sum is reported as 100×log-return points, not as a simple percentage return. Here, +10% followed by −10% leaves wealth at 99, a cumulative loss of 1%.`);
}

function drawPortfolio(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Two-asset portfolio volatility","Illustrative annual σA = 20%, σB = 10% · weights add to 100%");const rho=Math.max(-1,Math.min(1,v.correlation||0)),w=(v.weight||0)/100,sA=.2,sB=.1;const risk=(corr:number)=>Math.sqrt(w*w*sA*sA+(1-w)**2*sB*sB+2*w*(1-w)*corr*sA*sB)*100;const x0=60,x1=710,y0=215,y1=75,max=22,X=(c:number)=>x0+(c+1)/2*(x1-x0),Y=(q:number)=>y0-q/max*(y0-y1);for(let q=0;q<=20;q+=5){line(svg,x0,Y(q),x1,Y(q),palette.grid,1);text(svg,x0-9,Y(q)+3,`${q}%`,palette.muted,9,"end");}const pts:Array<[number,number]>=[];for(let i=0;i<=100;i++){const c=-1+i/50;pts.push([X(c),Y(risk(c))]);}path(svg,pts,palette.blue,3);const px=X(rho),py=Y(risk(rho));line(svg,px,75,px,py,palette.coral,1.5,"4 4");svg.appendChild(make("circle",{cx:px,cy:py,r:7,fill:palette.coral,stroke:palette.white,"stroke-width":2}));for(let c=-1;c<=1;c+=.5)text(svg,X(c),235,fmt(c,1),palette.muted,9,"middle");text(svg,(x0+x1)/2,257,"Correlation between asset returns",palette.ink,9,"middle","700");const ylabel=text(svg,18,(y0+y1)/2,"Annualized portfolio SD (%)",palette.ink,8,"middle","600");ylabel.setAttribute("transform",`rotate(-90 18 ${(y0+y1)/2})`);const current=risk(rho),weighted=(w*sA+(1-w)*sB)*100;metric(r,"Portfolio σ",`${fmt(current,2)}%`);metric(r,"Weighted σ average",`${fmt(weighted,2)}%`);metric(r,"Correlation",fmt(rho,2));metric(r,"Weight A / B",`${fmt(w*100,0)}% / ${fmt((1-w)*100,0)}%`);setExplanation(e,`<strong>Read the graph:</strong> lower correlation generally reduces the modeled portfolio standard deviation. The curve holds asset volatilities fixed; real correlations and tail dependence can change in stressed markets, so this is not a guarantee of risk reduction.`);
}
function logGamma(z:number):number{const p=[676.5203681218851,-1259.1392167224028,771.32342877765313,-176.61502916214059,12.507343278686905,-.13857109526572012,9.9843695780195716e-6,1.5056327351493116e-7];if(z<.5)return Math.log(Math.PI)-Math.log(Math.sin(Math.PI*z))-logGamma(1-z);z-=1;let x=.99999999999980993;for(let i=0;i<p.length;i++)x+=p[i]/(z+i+1);const t=z+p.length-.5;return .5*Math.log(2*Math.PI)+(z+.5)*Math.log(t)-t+Math.log(x);}
function betaPdf(x:number,a:number,b:number){if(x<=0||x>=1)return 0;return Math.exp((a-1)*Math.log(x)+(b-1)*Math.log(1-x)+logGamma(a+b)-logGamma(a)-logGamma(b));}
function drawBayesian(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Prior and posterior for an unknown success rate","Beta–Binomial illustration · successes and failures are set separately");
  const mean=(v.prior??50)/100,strength=v.priorStrength??10,success=Math.max(0,Math.round(v.successes??7)),failures=Math.max(0,Math.round(v.failures??13)),a=mean*strength,b=(1-mean)*strength,post=betaBinomialPosterior(a,b,success,failures),ap=post.alpha,bp=post.beta,pm=post.mean,sd=Math.sqrt(ap*bp/(((ap+bp)**2)*(ap+bp+1))),x0=72,x1=710,y0=210,y1=70,X=(x:number)=>x0+x*(x1-x0),max=Math.max(...Array.from({length:199},(_,i)=>Math.max(betaPdf((i+1)/200,a,b),betaPdf((i+1)/200,ap,bp))),1),Y=(x:number)=>y0-betaPdf(x,a,b)/max*(y0-y1),Yp=(x:number)=>y0-betaPdf(x,ap,bp)/max*(y0-y1);
  for(const q of [0,.25,.5,.75,1]){const x=X(q);line(svg,x,y0,x,y0+5,palette.muted,1);text(svg,x,y0+19,`${Math.round(q*100)}%`,palette.muted,8,"middle");}for(const q of [0,max/2,max]){const y=y0-q/max*(y0-y1);line(svg,x0,y,x1,y,palette.grid,1);text(svg,x0-7,y+3,fmt(q,1),palette.muted,7,"end");}line(svg,x0,y0,x1,y0,palette.muted,1);line(svg,x0,y1,x0,y0,palette.muted,1);
  const p1:Array<[number,number]>=[],p2:Array<[number,number]>=[];for(let i=1;i<200;i++){const x=i/200;p1.push([X(x),Y(x)]);p2.push([X(x),Yp(x)]);}path(svg,p1,palette.blue,2.5);path(svg,p2,palette.coral,3);line(svg,X(mean),y0,X(mean),Y(mean),palette.blue,1,"4 3");line(svg,X(pm),y0,X(pm),Yp(pm),palette.coral,1,"4 3");text(svg,78,62,"Prior",palette.blue,10,"start","700");text(svg,130,62,"Posterior",palette.coral,10,"start","700");const lo=Math.max(0,pm-1.96*sd),hi=Math.min(1,pm+1.96*sd);text(svg,(x0+x1)/2,257,"Success probability",palette.ink,9,"middle","700");const ylabel=text(svg,16,(y0+y1)/2,"Density",palette.ink,8,"middle","600");ylabel.setAttribute("transform",`rotate(-90 16 ${(y0+y1)/2})`);
  metric(r,"Prior mean",`${fmt(mean*100,1)}%`);metric(r,"Posterior mean",`${fmt(pm*100,1)}%`);metric(r,"Approx. 95% interval",`${fmt(lo*100,1)}–${fmt(hi*100,1)}%`);metric(r,"Observed results",`${success} successes · ${failures} failures`);
  setExplanation(e,`<strong>Read the graph:</strong> blue is the Beta prior and coral is the posterior after ${success} successes and ${failures} failures. The update adds each count to the matching prior parameter; the interval is a normal approximation and can be rough for a strongly skewed posterior. The posterior depends on both the data and chosen prior; it is not a guarantee about the next outcome.`);
}

function drawBacktesting(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"At least one false positive among null tests","Assumes independent null tests at α = 0.05 · real analyses may be dependent");const attempts=Math.max(1,Math.round(v.trials||1)),prob=1-Math.pow(.95,attempts),x0=65,x1=705,y0=215,y1=72,X=(n:number)=>x0+(n-1)/99*(x1-x0),Y=(p:number)=>y0-p*(y0-y1);for(let p=0;p<=1;p+=.25){line(svg,x0,Y(p),x1,Y(p),palette.grid,1);text(svg,x0-9,Y(p)+3,`${Math.round(p*100)}%`,palette.muted,9,"end");}const points:Array<[number,number]>=[];for(let n=1;n<=100;n++)points.push([X(n),Y(1-Math.pow(.95,n))]);path(svg,points,palette.blue,3);for(let n=1;n<=100;n+=19)text(svg,X(n),235,String(n),palette.muted,9,"middle");text(svg,(x0+x1)/2,257,"Number of independent null tests (m)",palette.ink,9,"middle","700");const px=X(attempts),py=Y(prob);line(svg,px,y1,px,py,palette.coral,1.5,"4 4");svg.appendChild(make("circle",{cx:px,cy:py,r:7,fill:palette.coral,stroke:palette.white,"stroke-width":2}));metric(r,"Null tests tried",String(attempts));metric(r,"Chance ≥1 false positive",`${fmt(prob*100,1)}%`);metric(r,"Single-test α","5%");metric(r,"Expected false positives",fmt(attempts*.05,2));setExplanation(e,`<strong>Read the graph:</strong> if every tested hypothesis is null and tests are independent, chance of at least one p<0.05 is 1−0.95<sup>m</sup>. Real tests may be dependent, and this calculation does not fix bad data, leakage or undisclosed analysis choices.`);
}
function drawKde(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Each observation contributes a kernel","Simulated return changes in percentage points · Gaussian kernel");
  const observations=[-2.8,-2.45,-2.2,-1.95,-1.72,-1.48,-1.25,-1.02,-.72,-.5,.28,.52,.76,1.48,1.72,1.94,2.16,2.34,2.54,2.78];
  const n=Math.max(6,Math.min(observations.length,Math.round(v.sampleSize??14))),data=observations.slice(0,n),h=Math.max(.1,v.bandwidth??.7),denom=n*h*Math.sqrt(2*Math.PI);
  const kde=(x:number)=>data.reduce((sum,xi)=>sum+Math.exp(-.5*((x-xi)/h)**2)/denom,0);
  const x0=66,x1=706,yTop=72,yBase=214,xMin=-4,xMax=4,steps=180,dx=(xMax-xMin)/steps;
  const xs=Array.from({length:steps+1},(_,i)=>xMin+i*dx),ys=xs.map(kde),yMax=Math.max(...ys)*1.18;
  const X=(x:number)=>x0+(x-xMin)/(xMax-xMin)*(x1-x0),Y=(y:number)=>yBase-y/yMax*(yBase-yTop);
  for(let tick=-4;tick<=4;tick+=2){line(svg,X(tick),yTop,X(tick),yBase,palette.grid,1);text(svg,X(tick),yBase+18,String(tick),palette.muted,10,"middle");}
  for(let j=0;j<=2;j++){const val=yMax*j/2,y=Y(val);line(svg,x0,y,x1,y,palette.grid,1);text(svg,x0-8,y+3,fmt(val,2),palette.muted,9,"end");}
  line(svg,x0,yBase,x1,yBase,"#98a4b2",1);
  for(const xi of data){const pts:Array<[number,number]>=[];for(let j=0;j<=64;j++){const x=xMin+j*(xMax-xMin)/64,y=Math.exp(-.5*((x-xi)/h)**2)/(n*h*Math.sqrt(2*Math.PI));pts.push([X(x),Y(y)]);}const component=path(svg,pts,palette.mint,1.1);if(component)component.setAttribute("opacity",".35");line(svg,X(xi),yBase-3,X(xi),yBase+4,palette.blue,1.7);}
  path(svg,xs.map((x,i)=>[X(x),Y(ys[i])] as [number,number]),palette.coral,3);
  text(svg,(x0+x1)/2,257,"Simulated return (percentage points)",palette.ink,10,"middle","700");
  const peakIndex=ys.indexOf(Math.max(...ys));let area=0;for(let i=1;i<ys.length;i++)area+=(ys[i]+ys[i-1])*.5*dx;
  metric(r,"Observations",String(n));metric(r,"Bandwidth h",`${fmt(h,2)} pp`);metric(r,"Peak location",`${fmt(xs[peakIndex],2)} pp`);metric(r,"Area in displayed range",fmt(area,3));
  setExplanation(e,`<strong>Read the graph:</strong> pale curves are the individual Gaussian contributions; coral is their sum. Increasing h spreads every contribution and usually smooths the total. The displayed area is a numerical approximation over −4 pp to +4 pp, not the probability of a point.`);
}
function drawCorrelation(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Paired data and a least-squares line","Synthetic teaching units · Pearson r describes linear association, not cause");
  const x=[-2.5,-2.12,-1.76,-1.4,-1.05,-.72,-.38,-.05,.3,.64,.98,1.34,1.72,2.12],noise=v.scatter??.8,outlier=v.outlier??0;
  const residual=[.1,-.22,.31,-.12,.18,-.25,.08,.28,-.18,.14,-.1,.23,-.16,.12];
  const y=x.map((xi,i)=>1.05*xi+residual[i]*noise+(i===x.length-1?outlier:0)),n=x.length,mx=x.reduce((a,b)=>a+b,0)/n,my=y.reduce((a,b)=>a+b,0)/n;
  const cov=x.reduce((sum,xi,i)=>sum+(xi-mx)*(y[i]-my),0)/(n-1),sx=Math.sqrt(x.reduce((sum,xi)=>sum+(xi-mx)**2,0)/(n-1)),sy=Math.sqrt(y.reduce((sum,yi)=>sum+(yi-my)**2,0)/(n-1)),rho=cov/(sx*sy);
  const slope=cov/(sx*sx),intercept=my-slope*mx,x0=70,x1=704,yTop=72,yBase=215,xMin=-2.8,xMax=2.8,yMin=Math.min(-2.5,...y)-.45,yMax=Math.max(2.5,...y)+.45;
  const X=(z:number)=>x0+(z-xMin)/(xMax-xMin)*(x1-x0),Y=(z:number)=>yBase-(z-yMin)/(yMax-yMin)*(yBase-yTop);
  for(let tick=-2;tick<=2;tick++){line(svg,X(tick),yTop,X(tick),yBase,palette.grid,1);text(svg,X(tick),yBase+17,String(tick),palette.muted,9,"middle");}
  for(let j=0;j<=4;j++){const val=yMin+(yMax-yMin)*j/4,yy=Y(val);line(svg,x0,yy,x1,yy,palette.grid,1);text(svg,x0-8,yy+3,fmt(val,1),palette.muted,9,"end");}
  line(svg,x0,yBase,x1,yBase,"#98a4b2",1);line(svg,x0,yTop,x0,yBase,"#98a4b2",1);
  for(let i=0;i<n;i++)svg.appendChild(make("circle",{cx:X(x[i]),cy:Y(y[i]),r:5,fill:i===n-1?palette.coral:palette.blue,opacity:.88}));
  path(svg,[[X(xMin),Y(intercept+slope*xMin)],[X(xMax),Y(intercept+slope*xMax)]],palette.coral,2.7);
  text(svg,(x0+x1)/2,257,"X · simulated units",palette.ink,9,"middle","700");const ylabel=text(svg,18,(yTop+yBase)/2,"Y · simulated units",palette.ink,8,"middle","600");ylabel.setAttribute("transform",`rotate(-90 18 ${(yTop+yBase)/2})`);
  metric(r,"Pearson r",fmt(rho,3));metric(r,"Sample covariance",fmt(cov),"squared units");metric(r,"Fitted slope",fmt(slope),"Y units per X unit");metric(r,"Paired observations",String(n));
  setExplanation(e,`<strong>Read the graph:</strong> blue points are the unchanged simulated pairs; coral is the moved final point and the fitted line. Correlation can be sensitive to outliers and linear shape. A visible association still does not establish which variable, if either, caused the other.`);
}
function drawEda(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  frame(svg,"Inspect the sample before summarizing it","Simulated daily yield changes (pp) · missing rows remain missing, not zero");
  const base=[-4.5,-3.2,-2.8,-2.3,-1.9,-1.7,-1.3,-1.1,-.8,-.5,-.2,0,.2,.4,.6,.8,1,1.3,1.5,1.8,2.1,2.5,3,3.2,3.5,4,4.2,4.5,5.2,6.1],all=[...base,v.shock??10],m=Math.max(0,Math.min(12,Math.round(v.missingRows??3))),missing=new Set<number>();for(let j=0;j<m;j++)missing.add(Math.floor((j+.5)*base.length/Math.max(m,1)));
  const data=all.filter((_,i)=>!missing.has(i)),mean=data.reduce((a,b)=>a+b,0)/data.length,med=median(data),iqr=quantile(data,.75)-quantile(data,.25),x0=64,x1=706,yTop=74,yBase=211,min=-8,max=20,bins=10,bw=(x1-x0)/bins,counts=Array(bins).fill(0);
  for(const value of data){const ix=Math.max(0,Math.min(bins-1,Math.floor((value-min)/(max-min)*bins)));counts[ix]++;}const maxCount=Math.max(...counts,1),X=(x:number)=>x0+(x-min)/(max-min)*(x1-x0),Y=(count:number)=>yBase-count/maxCount*95;
  for(let tick=-6;tick<=18;tick+=6){const x=X(tick);line(svg,x,yTop,x,yBase,palette.grid,1);text(svg,x,yBase+18,String(tick),palette.muted,9,"middle");}
  for(const tick of [0,Math.ceil(maxCount/2),maxCount]){const y=Y(tick);line(svg,x0,y,x1,y,palette.grid,1);text(svg,x0-8,y+3,String(tick),palette.muted,8,"end");}
  for(let i=0;i<bins;i++){const height=yBase-Y(counts[i]);svg.appendChild(make("rect",{x:x0+i*bw+2,y:Y(counts[i]),width:bw-4,height,rx:3,fill:palette.blue,opacity:.8}));}
  line(svg,x0,yBase,x1,yBase,"#98a4b2",1);line(svg,X(mean),yTop,X(mean),yBase,palette.coral,2);line(svg,X(med),yTop,X(med),yBase,palette.mint,2.5);text(svg,Math.min(X(mean)+5,x1-4),yTop+11,`Mean ${fmt(mean,1)} pp`,palette.coral,9,"start","700");text(svg,Math.min(X(med)+5,x1-4),yTop+25,`Median ${fmt(med,1)} pp`,palette.mint,9,"start","700");
  text(svg,(x0+x1)/2,257,"Daily yield change (percentage points)",palette.ink,8,"middle","700");const ylabel=text(svg,16,(yTop+yBase)/2,"Frequency (count)",palette.ink,8,"middle","600");ylabel.setAttribute("transform",`rotate(-90 16 ${(yTop+yBase)/2})`);
  metric(r,"Observed rows",String(data.length));metric(r,"Missing rows",String(m));metric(r,"Mean",`${fmt(mean,2)} pp`);metric(r,"IQR",`${fmt(iqr,2)} pp`);
  setExplanation(e,`<strong>Read the graph:</strong> coral marks the mean and mint the median. The sample has ${m} omitted rows; it does not silently fill them with zero. Quartiles use linear interpolation between ordered observations. Check whether the shock is a genuine observation before changing or deleting it.`);
}

function drawToolkit(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement){
  const n=Math.max(20,Math.round(v.rows??50)),rate=Math.max(0,Math.min(30,v.missingRate??10)),rng=seeded(327+n*19+rate*43),values:number[]=[],missing:boolean[]=[];
  for(let i=0;i<n;i++){values.push(.15+gaussian(rng)*.9);missing.push(rng()<rate/100);}
  const observed=values.filter((_,i)=>!missing[i]),mean=observed.reduce((a,b)=>a+b,0)/(observed.length||1),x0=62,x1=708,yTop=75,yBase=211,min=Math.min(-2.8,...observed)-.2,max=Math.max(2.8,...observed)+.2,X=(i:number)=>x0+i/(n-1)*(x1-x0),Y=(z:number)=>yBase-(z-min)/(max-min)*(yBase-yTop);
  frame(svg,"Synthetic table → checked summary → labeled plot","Standardized synthetic units · gaps represent missing observations, not zeros");
  for(let tick=-2;tick<=2;tick++){const yy=Y(tick);line(svg,x0,yy,x1,yy,palette.grid,1);text(svg,x0-8,yy+3,String(tick),palette.muted,9,"end");}
  for(let i=0;i<n;i++){if(missing[i])continue;if(i>0&&!missing[i-1])line(svg,X(i-1),Y(values[i-1]),X(i),Y(values[i]),palette.blue,1.7);svg.appendChild(make("circle",{cx:X(i),cy:Y(values[i]),r:2.6,fill:palette.blue,opacity:.8}));}
  line(svg,x0,yBase,x1,yBase,"#98a4b2",1);text(svg,(x0+x1)/2,257,"Row order",palette.ink,10,"middle","700");const ylabel=text(svg,16,(yTop+yBase)/2,"Standardized value",palette.ink,8,"middle","600");ylabel.setAttribute("transform",`rotate(-90 16 ${(yTop+yBase)/2})`);
  const missingCount=n-observed.length,realizedRate=missingCount/n*100;metric(r,"Rows loaded",String(n));metric(r,"Observed values",String(observed.length));metric(r,"Missing values (realized)",String(missingCount),`target chance ${fmt(rate,0)}% · realized ${fmt(realizedRate,1)}%`);metric(r,"Observed mean",fmt(mean,3),"standardized units");
  setExplanation(e,`<strong>Read the graph:</strong> every value is simulated and blank gaps are kept missing. The mean uses observed entries only. The control sets each row's missingness probability; realized missing rate varies randomly and need not equal that target in a finite file.`);
}

const drawByKind:Record<string,(svg:SVGSVGElement,v:Inputs,r:HTMLElement,e:HTMLElement)=>void>={descriptive:drawDescriptive,probability:drawProbability,clt:drawCLT,confidence:drawConfidence,pvalue:drawPvalue,regression:drawRegression,causal:drawCausal,volatility:drawVolatility,returns:drawReturns,portfolio:drawPortfolio,bayesian:drawBayesian,backtesting:drawBacktesting,kde:drawKde,correlation:drawCorrelation,eda:drawEda,toolkit:drawToolkit};
function setup(){document.querySelectorAll<HTMLElement>("[data-lab]").forEach(shell=>{const kind=shell.dataset.chartKind||"descriptive",draw=drawByKind[kind];if(!draw)return;const update=()=>clearAndDraw(shell,draw);shell.querySelectorAll<HTMLInputElement>("[data-control]").forEach(input=>input.addEventListener("input",update));update();});}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",setup,{once:true});else setup();
export {};

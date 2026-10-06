window.renderTokenLensChart=function(events){
 const rows=window.TokenLensTimeline.aggregate(events),host=document.getElementById('timeline'),legend=document.getElementById('timeline-legend'),body=document.getElementById('timeline-rows');
 host.replaceChildren();legend.replaceChildren();body.replaceChildren();
 const format=new Intl.NumberFormat('pt-BR'),compact=new Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}),names={codex:'Codex',claude_code:'Claude Code',antigravity:'Antigravity',other:'Outro'},dateLabel=day=>day.slice(8)+'/'+day.slice(5,7),text=(tag,value)=>{const el=document.createElement(tag);el.textContent=value;return el;};
 for(const row of rows){const tr=document.createElement('tr');tr.append(text('td',dateLabel(row.day)+'/'+row.day.slice(0,4)),text('td',names[row.provider]),text('td',row.model||'Modelo não informado'),text('td',format.format(row.tokens)));body.append(tr);}
 if(!rows.length){host.append(text('p','Sem consumo informado para traçar o gráfico neste filtro.'));return;}
 const colors=['#f878ed','#5ee7dc','#c6a0ff','#ffd17c','#91d995','#ff9fbd','#94c6ff'];
 const series=[...new Set(rows.map(r=>JSON.stringify([r.provider,r.model])))];
 const first=new Date(rows[0].day+'T12:00:00'),last=new Date(rows[rows.length-1].day+'T12:00:00'),days=[];
 for(let d=new Date(first);d<=last;d.setDate(d.getDate()+1)){days.push([d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-'));}
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 1040 300');svg.setAttribute('role','img');svg.setAttribute('aria-labelledby','timeline-title timeline-description');
 const add=(tag,attrs={},value)=>{const el=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));if(value!==undefined)el.textContent=value;svg.append(el);return el;};
 add('title',{id:'timeline-title'},'Tokens por data, CLI e modelo');add('desc',{id:'timeline-description'},'Soma diária de entrada e saída. Dias sem medição não são tratados como zero. Consulte a tabela de valores abaixo.');
 const max=Math.max(1,...rows.map(r=>r.tokens)),top=Math.ceil(max/4)*4,x=i=>days.length===1?548:70+i*930/(days.length-1),y=v=>240-v/top*206;
 for(let i=0;i<=4;i++){const val=top*i/4;add('line',{x1:70,x2:1000,y1:y(val),y2:y(val),stroke:'#39313e','stroke-dasharray':'3 5'});add('text',{x:54,y:y(val)+4,'text-anchor':'end',fill:'#bdb5c3','font-size':12},compact.format(val));}
 const stride=Math.max(1,Math.ceil(days.length/8));days.forEach((day,i)=>{if(i%stride===0||i===days.length-1)add('text',{x:x(i),y:272,'text-anchor':'middle',fill:'#bdb5c3','font-size':12},dateLabel(day));});
 series.forEach((key,index)=>{const [provider,model]=JSON.parse(key),color=colors[index%colors.length],label=names[provider]+' · '+(model||'Modelo não informado'),item=document.createElement('span'),dot=document.createElement('i');dot.style.backgroundColor=color;item.append(dot,document.createTextNode(label));legend.append(item);let previous=null;for(let i=0;i<days.length;i++){const row=rows.find(r=>r.day===days[i]&&r.provider===provider&&r.model===model);if(!row){previous=null;continue;}const point={x:x(i),y:y(row.tokens)};if(previous)add('line',{x1:previous.x,y1:previous.y,x2:point.x,y2:point.y,stroke:color,'stroke-width':2.5,'stroke-dasharray':index>=colors.length?'6 4':'none'});const circle=add('circle',{cx:point.x,cy:point.y,r:4,fill:color,stroke:'#18141d','stroke-width':2});const title=document.createElementNS(ns,'title');title.textContent=dateLabel(row.day)+' · '+label+': '+format.format(row.tokens)+' tokens';circle.append(title);previous=point;}});
 host.append(svg);
};

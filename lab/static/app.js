const $ = id => document.getElementById(id);
const categories = {unknown:'Não informada',coding:'Programação',debugging:'Diagnóstico',refactor:'Refatoração',research:'Pesquisa',planning:'Planejamento',other:'Outra'};
const complexities = {unknown:'Não informada',low:'Baixa',medium:'Média',high:'Alta'};
const providers = {codex:'Codex',claude_code:'Claude Code',antigravity:'Antigravity',other:'Outro'};
const scopes = {run:'Execução',turn:'Turno',request:'Requisição',context_snapshot:'Contexto (snapshot)'};
const nf = new Intl.NumberFormat('pt-BR');
function node(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function options(select,dict){for(const [value,text] of Object.entries(dict)){const o=node('option',text);o.value=value;select.append(o);}}
options($('category'),categories);
if(new URLSearchParams(location.search).get('mode')==='demo')$('mode').value='demo';
function select(dict,value,label){const el=node('select');el.setAttribute('aria-label',label);options(el,dict);el.value=value;return el;}
async function get(url,opts){const res=await fetch(url,opts);if(!res.ok)throw Error('Falha local');return res.json();}
let generation=0;
async function refresh(){
 const ticket=++generation;
 $('refresh').disabled=true;
 try{
  const q=new URLSearchParams();for(const id of ['mode','days','provider','model','category'])q.set(id,$(id).value);
  const [data,status]=await Promise.all([get('/api/events?'+q),get('/api/status')]);
  if(ticket!==generation)return;
  const demo=$('mode').value==='demo';
  $('notice').className='notice'+(demo?' demo':'');
  $('notice').textContent=demo?'Demonstração · dados fictícios, separados do uso real. Não comprovam conexão com as CLIs.':'Uso real · somente execuções instrumentadas. Dados ausentes permanecem desconhecidos.';
  const usage=data.events.filter(e=>e.scope!=='context_snapshot'), snaps=data.events.filter(e=>e.scope==='context_snapshot');
  const known=usage.filter(e=>e.usage.total_tokens!==null);
  $('tokens').textContent=known.length?nf.format(known.reduce((s,e)=>s+e.usage.total_tokens,0)):'—';
  $('coverage').textContent=`Total informado em ${known.length} de ${usage.length} medições`;
  $('runs').textContent=nf.format(usage.length);$('snapshots').textContent=nf.format(snaps.length);
  const allModels=[...new Set(data.events.map(e=>e.execution.model).filter(Boolean))];
  $('models').textContent=allModels.length;$('missing').textContent=`${data.events.filter(e=>!e.execution.model).length} medições sem modelo identificado`;
  $('model').replaceChildren();
  options($('model'),{'':data.models.length?'Todos os modelos':'Sem modelos disponíveis',...Object.fromEntries(data.models.map(m=>[m,m==='__unknown__'?'Modelo não informado':m]))});
  $('model').value=data.selected_model;
  $('model').disabled=data.models.length===0;
  const groups={};for(const e of known){const key=e.execution.model||'Modelo não informado';groups[key]=(groups[key]||0)+e.usage.total_tokens;}
  $('bars').replaceChildren();const max=Math.max(1,...Object.values(groups));
  for(const [key,value] of Object.entries(groups).sort((a,b)=>b[1]-a[1])){const row=node('div',undefined,'bar-row'),label=node('div',undefined,'bar-label'),track=node('div',undefined,'track'),meter=node('meter');label.append(node('span',key),node('strong',nf.format(value)));meter.min=0;meter.max=max;meter.value=value;meter.setAttribute('aria-label',key+': '+nf.format(value)+' tokens');track.append(meter);row.append(label,track);$('bars').append(row);}
  if(!known.length)$('bars').append(node('p','Sem consumo informado neste filtro.','muted'));
  $('suggestions').replaceChildren(...data.suggestions.map(s=>node('li',s)));
  $('connections').replaceChildren();for(const p of status.providers){const div=node('div',undefined,'connection');div.append(node('strong',providers[p.provider]),node('p',p.integration),node('p',p.last_event?'Métrica recebida: '+new Date(p.last_event).toLocaleString('pt-BR'):(p.installed?'CLI detectada · aguardando métricas':'CLI não encontrada no PATH'),'state'));$('connections').append(div);}
  $('rows').replaceChildren();$('empty').hidden=data.events.length>0;
  $('count').textContent=`${data.events.length} registros · até 100 exibidos`;
  for(const e of data.events.slice(0,100)){
   const tr=node('tr'),when=node('td',new Date(e.timestamp).toLocaleString('pt-BR')),who=node('td',providers[e.provider]);who.append(node('small',e.execution.model||'Modelo não informado'));
   const cat=select(categories,e.task.category,'Categoria da medição '+e.event_id),complex=select(complexities,e.task.complexity,'Complexidade da medição '+e.event_id),catTd=node('td'),complexTd=node('td'),action=node('td'),save=node('button','Salvar');
   catTd.append(cat);complexTd.append(complex);action.append(save);
   save.dataset.eventId=e.event_id;
   save.setAttribute('aria-label','Salvar classificação da medição '+e.event_id);
   save.addEventListener('click',async()=>{save.disabled=true;try{await get('/api/label',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({event_id:e.event_id,category:cat.value,complexity:complex.value})});$('save-status').textContent='Classificação salva localmente.';await refresh();const restored=Array.from($('rows').querySelectorAll('button')).find(b=>b.dataset.eventId===e.event_id);(restored||$('refresh')).focus({preventScroll:true});}catch{$('save-status').textContent='Não foi possível salvar. Tente novamente.';}finally{save.disabled=false;}});
   tr.append(when,who,node('td',scopes[e.scope]),node('td',e.usage.total_tokens===null?'Não informado':nf.format(e.usage.total_tokens)),catTd,complexTd,action);$('rows').append(tr);
  }
  window.renderTokenLensChart(data.events);
  window.TokenLensDropdowns.upgrade();
 }catch{ $('notice').textContent='Não foi possível atualizar as métricas. Verifique se o servidor local está ativo. Os dados abaixo podem estar desatualizados.'; }
 finally{if(ticket===generation)$('refresh').disabled=false;}
}
for(const id of ['mode','days','provider','model','category'])$(id).addEventListener('change',()=>refresh());
$('refresh').addEventListener('click',refresh);refresh();

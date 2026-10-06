const assert=require('node:assert/strict'),fs=require('node:fs'),{JSDOM}=require('jsdom');
(async()=>{
 const dom=new JSDOM(fs.readFileSync('lab/static/index.html','utf8'),{url:'http://127.0.0.1:8765/?mode=demo',runScripts:'outside-only'}),w=dom.window,d=w.document;
 w.HTMLElement.prototype.scrollIntoView=function(){};
 const events=[{event_id:'00000000-0000-4000-8000-000000000001',provider:'codex',timestamp:'2026-01-10T12:00:00Z',scope:'turn',synthetic:true,execution:{model:'gpt-5',reasoning_level:null},task:{category:'unknown',complexity:'unknown'},usage:{total_tokens:120}},{event_id:'00000000-0000-4000-8000-000000000002',provider:'claude_code',timestamp:'2026-01-11T12:00:00Z',scope:'run',synthetic:true,execution:{model:null,reasoning_level:null},task:{category:'unknown',complexity:'unknown'},usage:{total_tokens:80}}];
 let saves=0;
 w.fetch=async(url,opts)=>{assert.ok(url.startsWith('/api/'));let data;if(url==='/api/label'){const p=JSON.parse(opts.body);events.find(e=>e.event_id===p.event_id).task={category:p.category,complexity:p.complexity};saves++;data={ok:true};}else if(url.startsWith('/api/events'))data={events,suggestions:['Sugestão sintética.'],models:['gpt-5','__unknown__'],selected_model:''};else data={providers:[]};return {ok:true,json:async()=>data};};
 for(const f of ['dropdown.js','timeline.js','chart.js','app.js'])w.eval(fs.readFileSync('lab/static/'+f,'utf8'));
 const settle=()=>new Promise(resolve=>setImmediate(resolve));await settle();await settle();
 assert.equal(d.querySelector('#mode').value,'demo');assert.equal(d.querySelector('#runs').textContent,'2');assert.equal(d.querySelectorAll('#timeline circle').length,2);assert.equal(d.querySelectorAll('#timeline-rows tr').length,2);assert.equal(d.querySelectorAll('select:not([hidden])').length,0);
 const cat=d.querySelector('#rows [role=combobox]');cat.click();const planning=[...d.querySelectorAll('[role=option]')].find(o=>o.textContent==='Planejamento');planning.click();d.querySelector('#rows button').click();await settle();await settle();
 assert.equal(saves,1);assert.equal(events[0].task.category,'planning');assert.equal(d.activeElement.dataset.eventId,events[0].event_id);assert.match(d.querySelector('#save-status').textContent,/salva/);
 dom.window.close();console.log('Dashboard: synthetic chart, custom controls, classification and focus passed.');
})().catch(e=>{console.error(e);process.exitCode=1;});

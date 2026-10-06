/* Pure daily aggregation. No inferred zeros and no context snapshots. */
(function(root){
 function aggregate(events){const groups=new Map();for(const e of events){if(e.scope==='context_snapshot'||e.usage.total_tokens===null)continue;const d=new Date(e.timestamp),day=[d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-'),key=JSON.stringify([day,e.provider,e.execution.model]);if(!groups.has(key))groups.set(key,{day,provider:e.provider,model:e.execution.model,tokens:0});groups.get(key).tokens+=e.usage.total_tokens;}return [...groups.values()].sort((a,b)=>a.day.localeCompare(b.day)||a.provider.localeCompare(b.provider)||String(a.model).localeCompare(String(b.model)));}
 if(typeof module==='object'&&module.exports)module.exports={aggregate};else root.TokenLensTimeline={aggregate};
})(typeof window==='undefined'?globalThis:window);

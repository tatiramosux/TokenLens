const assert=require('node:assert/strict');
const {aggregate}=require('../lab/static/timeline.js');
const e=(provider,model,tokens,scope='run',day='2026-01-10')=>({provider,execution:{model},usage:{total_tokens:tokens},scope,timestamp:day+'T12:00:00Z'});
const out=aggregate([e('codex','gpt-5',10),e('codex','gpt-5',15),e('claude_code',null,8),e('codex','gpt-5',999,'context_snapshot'),e('codex','gpt-5',null),e('codex','gpt-5',5,'run','2026-01-12')]);
assert.equal(out.length,3);assert.equal(out.find(x=>x.provider==='codex'&&x.tokens===25).tokens,25);assert.equal(out.find(x=>x.provider==='claude_code').model,null);assert.equal(out.reduce((s,x)=>s+x.tokens,0),38);assert.equal(out.some(x=>x.day==='2026-01-11'),false);assert.deepEqual(aggregate([]),[]);
console.log('Chart aggregation: passed (synthetic only).');

async function send(){
  const message = $('#msg').value.trim();
  if(!message) return;
  addMsg(message,'user'); $('#msg').value='';

  const body = {
    message,
    user_language: "hi", // or dynamic select by user
    form: {
      age: Number($('#age').value||30),
      family_size: Number($('#family').value||1),
      income_monthly: Number($('#income').value||50000),
      expenses_monthly: Number($('#expenses').value||20000),
      insurance_type: $('#insType').value,
      country: $('#country').value,
      conditions: ($('#conds').value||'').split(',').map(s=>s.trim()).filter(Boolean),
      goal_coverage: Number($('#coverage').value||0) || null
    }
  };

  try{
    const r = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const data = await r.json();

    addMsg(data.answer,'bot');

    // Render options
    const optBox = $('#optionsBox');
    optBox.innerHTML = '';
    data.predictions.forEach(opt=>{
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `<b>${opt.tier}</b><br>Premium: ${opt.premium}<br>Risk: ${opt.risk}<br>Claim: ${opt.claim_prob}`;
      if(opt.tier === data.recommended) card.style.border = "2px solid green";
      card.onclick = ()=> addMsg(`Explain ${opt.tier} plan for me.`, 'user');
      optBox.appendChild(card);
    });

    // Render dashboard chart
    renderChart(data.predictions);
  }catch(e){ addMsg('Server error: '+e,'bot'); }
}

$('#downloadPdf').addEventListener('click', async ()=>{
  const r = await fetch('/summarize',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:"Summarize my options",form:{}})});
  const blob = await r.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = "recommendation_summary.pdf";
  a.click();
  window.URL.revokeObjectURL(url);
});

// Chart.js for dashboard
function renderChart(options){
  const ctx = document.getElementById('chart');
  new Chart(ctx, {
    type:'bar',
    data:{
      labels: options.map(o=>o.tier),
      datasets:[
        {label:'Premium', data:options.map(o=>o.premium)},
        {label:'Risk', data:options.map(o=>o.risk)},
        {label:'Claim Probability', data:options.map(o=>o.claim_prob)}
      ]
    }
  });
}


function openModal(src, title, desc){
  const m = document.getElementById('imgModal');
  if(!m) return;
  document.getElementById('modalImg').src = src;
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalDesc').textContent = desc;
  m.style.display = 'flex';
}
function closeModal(e){
  if(e.target.classList.contains('modal')){
    e.currentTarget.style.display = 'none';
  }
}
function acceptCookies(){
  try{
    localStorage.setItem('cookieAccepted','1');
    document.getElementById('cookie-banner').style.display='none';
  }catch(e){}
}
(function(){
  try{
    if(!localStorage.getItem('cookieAccepted')){
      var el = document.getElementById('cookie-banner');
      if(el) el.style.display='flex';
    }
  }catch(e){}
})();

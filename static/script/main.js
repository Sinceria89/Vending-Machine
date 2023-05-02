document.addEventListener('DOMContentLoaded', function(){
    updateClock();
    setInterval(updateClock, 1000);
});

  function updateClock() {
    let now = new Date();
    let day = now.toLocaleDateString('en-GB', { day: '2-digit' });
    let month = now.toLocaleDateString('en-GB', { month: '2-digit' });
    let year = now.toLocaleDateString('en-GB', { year: 'numeric' });
    let dayOfWeek = now.toLocaleDateString('th-TH', { weekday: 'long' });
    let time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    document.getElementById('clock').innerHTML = dayOfWeek.toUpperCase() + ' | ' + time + ' | ' + day + '-' + month + '-' + year;
  }


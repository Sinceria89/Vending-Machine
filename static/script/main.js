new InputTouchspin(document.querySelector('.touchspin'))

// Get the div elements
const inactiveDiv = document.getElementById('Inactive');
const activeDiv = document.getElementById('Active');

// Set the initial state to hidden
let isInactiveDivVisible = false;
let isActiveDivVisible = true;
inactiveDiv.style.display = 'none';
activeDiv.style.display = 'block';

// Declare the timerId variables
let inactiveTimerId;
let activeTimerId;

// Set up event listeners to detect user activity
document.addEventListener('mousemove', resetTimers);
document.addEventListener('keypress', resetTimers);

resetTimers();
// Set up a timer to check for user inactivity every 100ms
setInterval(checkActivity, 100);

// Functions to handle user activity
function resetTimers() {
    // Reset the timers and hide/show the divs if necessary
    if (isInactiveDivVisible) {
        hideInactiveDiv();
    }
    clearTimeout(inactiveTimerId);
    inactiveTimerId = setTimeout(showInactiveDiv, 5000);

    showActiveDiv(); // Always show the activeDiv
    clearTimeout(activeTimerId);
    activeTimerId = setTimeout(hideActiveDiv, 5000);
}

function checkActivity() {
    const now = new Date().getTime();
    if (now - lastActivity >= 5000 && isInactiveDivVisible) {
        hideInactiveDiv();
    }
    if (now - lastActivity < 5000 && isActiveDivVisible) {
        showActiveDiv();
    }
}

function showInactiveDiv() {
    if (!isInactiveDivVisible) {
        inactiveDiv.style.display = 'block';
        isInactiveDivVisible = true;
    }
}

function hideInactiveDiv() {
    if (isInactiveDivVisible) {
        inactiveDiv.style.display = 'none';
        isInactiveDivVisible = false;
    }
}

function showActiveDiv() {
    if (!isActiveDivVisible) {
        activeDiv.style.display = 'block';
        isActiveDivVisible = true;
    }
}

function hideActiveDiv() {
    if (isActiveDivVisible) {
        activeDiv.style.display = 'none';
        isActiveDivVisible = false;
    }
}

// Initialize the last activity time
let lastActivity = new Date().getTime();

// Set up a timer to update the last activity time every second
setInterval(() => {
    lastActivity = new Date().getTime();
}, 1000);
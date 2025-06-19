function openTab(evt, tabName) {
    let tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    let tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";

    // If "scoreboard" tab is opened, also open default sub-tab
    if (tabName === "scoreboard") {
        document.querySelector('.subTablinks').click();
    }
}


function openSubTab(evt, subTabName) {
    let subTabcontent = document.getElementsByClassName("subTabcontent");
    for (let i = 0; i < subTabcontent.length; i++) {
        subTabcontent[i].style.display = "none";
    }
    let subTablinks = document.getElementsByClassName("subTablinks");
    for (let i = 0; i < subTablinks.length; i++) {
        subTablinks[i].className = subTablinks[i].className.replace(" active", "");
    }
    document.getElementById(subTabName).style.display = "block";
    evt.currentTarget.className += " active";
}

function openStageTab(evt, stageTabName) {
    let stageTabcontent = document.getElementsByClassName("stageTabcontent");
    for (let i = 0; i < stageTabcontent.length; i++) {
        stageTabcontent[i].style.display = "none";
    }
    let stageTablinks = document.getElementsByClassName("stageTablinks");
    for (let i = 0; i < stageTablinks.length; i++) {
        stageTablinks[i].className = stageTablinks[i].className.replace(" active", "");
    }
    document.getElementById(stageTabName).style.display = "block";
    evt.currentTarget.className += " active";
}

window.onload = function() {
    document.getElementById("defaultOpen").click(); // open scoreboard tab
    document.querySelector(".subTablinks").click(); // open first sub-tab (Classement)
};


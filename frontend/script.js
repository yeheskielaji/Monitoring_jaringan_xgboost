// Initialize counts for each classification
let predictionCounts = {
    BENIGN: 0,
    DDoS: 0,
    DoS: 0,
    "Port Scan": 0,
    Bot: 0,
    "Web Attack": 0,
    "Brute Force": 0,
};

let labelCounts = {
    BENIGN: 0,
    DDoS: 0,
    DoS: 0,
    "Port Scan": 0,
    Bot: 0,
    "Web Attack": 0,
    "Brute Force": 0,
};

// Connect to Socket.IO server
const socket = io.connect();

// Chart.js configurations
let predictionData = [0, 0, 0, 0, 0, 0, 0, 0, 0];
let labelData = [0, 0, 0, 0, 0, 0, 0, 0, 0];

const predictionChart = new Chart(document.getElementById("predictionChart"), {
    type: "doughnut",
    data: {
        labels: [
            "BENIGN",
            "DDoS",
            "DoS",
            "Port Scan",
            "Bot",
            "Web Attack",
            "Brute Force",
        ],
        datasets: [{
            data: predictionData,
            backgroundColor: [
                "#4CAF50",
                "#FF5733",
                "#FFC300",
                "#36A2EB",
                "#C70039",
                "#900C3F",
                "#6F42C1",
            ],
        }, ],
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: "bottom",
            },
        },
    },
});

const labelChart = new Chart(document.getElementById("labelChart"), {
    type: "doughnut",
    data: {
        labels: [
            "BENIGN",
            "DDoS",
            "DoS",
            "Port Scan",
            "Bot",
            "Web Attack",
            "Brute Force",
        ],
        datasets: [{
            data: labelData,
            backgroundColor: [
                "#4CAF50",
                "#FF5733",
                "#FFC300",
                "#36A2EB",
                "#C70039",
                "#900C3F",
                "#6F42C1",
            ],
        }, ],
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: "bottom",
            },
        },
    },
});

const flowPacketsChart = new Chart(
    document.getElementById("flowPacketsChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                    label: "Flow Packets/s",
                    data: [],
                    borderColor: "#4CAF50",
                    fill: false,
                    yAxisID: "y",
                },
                {
                    label: "Flow Bytes/s",
                    data: [],
                    borderColor: "#FFC300",
                    fill: false,
                    yAxisID: "y1",
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Time/Index",
                    },
                },
                y: {
                    id: "y",
                    type: "linear",
                    position: "left",
                    title: {
                        display: true,
                        text: "Flow Packets/s",
                    },
                },
                y1: {
                    id: "y1",
                    type: "linear",
                    position: "right",
                    title: {
                        display: true,
                        text: "Flow Bytes/s",
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
            },
            plugins: {
                legend: {
                    position: "bottom",
                },
            },
        },
    }
);

const totalPacketsChart = new Chart(
    document.getElementById("totalPacketsChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                    label: "Total Fwd Packets",
                    data: [],
                    borderColor: "#C70039",
                    fill: false,
                    yAxisID: "y",
                },
                {
                    label: "Total Backward Packets",
                    data: [],
                    borderColor: "#36A2EB",
                    fill: false,
                    yAxisID: "y1",
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Time/Index",
                    },
                },
                y: {
                    id: "y",
                    type: "linear",
                    position: "left",
                    title: {
                        display: true,
                        text: "Total Fwd Packets",
                    },
                },
                y1: {
                    id: "y1",
                    type: "linear",
                    position: "right",
                    title: {
                        display: true,
                        text: "Total Backward Packet",
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
            },
            plugins: {
                legend: {
                    position: "bottom",
                },
            },
        },
    }
);

const packetLengthChart = new Chart(
    document.getElementById("packetLengthChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Packet Length Distribution",
                data: [],
                borderColor: "#FFC300",
                fill: false,
            }, ],
        },
    }
);

// Handle Start and Pause Simulation
document.getElementById("startBtn").onclick = function() {
    socket.emit("start_simulation");
};

document.getElementById("pauseBtn").onclick = function() {
    socket.emit("stop_simulation");
};

// Update charts with real-time data
socket.on("prediction", function(data) {
    predictionCounts[data.prediction] =
        (predictionCounts[data.prediction] || 0) + 1;
    labelCounts[data.original_label] =
        (labelCounts[data.original_label] || 0) + 1;

    // Update pie charts for prediction and original label
    updatePieChart(predictionChart, predictionData, predictionCounts);
    updatePieChart(labelChart, labelData, labelCounts);

    // Update line charts for flow_packets_s and packet_length_distribution
    updateLineChart(flowPacketsChart, data.flow_packets_s, "Flow Packets/s");
    updateLineChart(flowPacketsChart, data.flow_bytes_s, "Flow Bytes/s");
    updateLineChart(totalPacketsChart, data.total_fwd, "Total Fwd Packets");
    updateLineChart(totalPacketsChart, data.total_bwd, "Total Backward Packets");

    // Update classification counts card
    updateClassificationCounts();

    // Update the alarm card
    updateAlarm(data.prediction);
});

// Helper functions to update charts and classification list
function updatePieChart(chart, data, counts) {
    data[0] = counts["BENIGN"];
    data[1] = counts["DDoS"];
    data[2] = counts["DoS"];
    data[3] = counts["Port Scan"];
    data[4] = counts["Bot"];
    data[5] = counts["Web Attack"];
    data[6] = counts["Brute Force"];
    data[7] = counts["Infiltration"];
    data[8] = counts["Heartbleed"];
    chart.update();
}

// Helper function to update Line charts
function updateLineChart(chart, value, label) {
    chart.data.labels.push(chart.data.labels.length + 1);
    chart.data.datasets.forEach((dataset) => {
        if (dataset.label === label) {
            dataset.data.push(value);
        }
    });
    chart.update();
}

function updateBarChart(chart, value) {
    chart.data.labels.push(chart.data.labels.length + 1);
    chart.data.datasets[0].data.push(value);
    chart.update();
}

// Function to update the classification counts on the card
function updateClassificationCounts() {
    const predictionCountsList = document.getElementById("predictionCountsList");
    const labelCountsList = document.getElementById("labelCountsList");

    // Clear previous data
    predictionCountsList.innerHTML = "";
    labelCountsList.innerHTML = "";

    // Add prediction counts to the list
    for (const [key, value] of Object.entries(predictionCounts)) {
        const listItem = document.createElement("li");
        listItem.classList.add("list-group-item");
        listItem.innerHTML = `${key}: ${value}`;
        predictionCountsList.appendChild(listItem);
    }

    // Add label counts to the list
    for (const [key, value] of Object.entries(labelCounts)) {
        const listItem = document.createElement("li");
        listItem.classList.add("list-group-item");
        listItem.innerHTML = `${key}: ${value}`;
        labelCountsList.appendChild(listItem);
    }
}

// Function to handle the alarm card
function updateAlarm(attackType) {
    const alarmStatus = document.getElementById("alarmStatus");

    if (attackType !== "BENIGN") {
        if (currentAttack === attackType) {
            consecutiveAttacks += 1;
        } else {
            currentAttack = attackType;
            consecutiveAttacks = 1;
        }
    } else {
        currentAttack = null;
        consecutiveAttacks = 0;
    }

    if (consecutiveAttacks >= 5) {
        alarmStatus.innerHTML = `
<i class="bi bi-exclamation-triangle text-danger" style="font-size:5rem;"></i>
<h5 class="text-danger">ALERT! Attack Detected!</h5>
<p class="text-danger">Type: ${attackType} - Occurred ${consecutiveAttacks} times</p>
`;
        // Update the attack history
        updateAttackHistory(currentAttack, consecutiveAttacks);
    } else {
        alarmStatus.innerHTML = `
<i class="bi bi-cloud-check text-secondary" style="font-size:5rem;"></i>
<h5 class="text-secondary">No Notification</h5>
`;
    }
}

// Function to update attack history
function updateAttackHistory(currentAttack, consecutiveAttacks) {
    const attackHistory = document.getElementById("attackHistory");

    // Format waktu untuk timestamp
    const now = new Date();
    const timestamp = [
            String(now.getHours()).padStart(2, "0"),
            String(now.getMinutes()).padStart(2, "0"),
            String(now.getSeconds()).padStart(2, "0"),
        ].join(":") +
        " " + [
            String(now.getDate()).padStart(2, "0"),
            String(now.getMonth() + 1).padStart(2, "0"),
            now.getFullYear(),
        ].join(":");

    const listItem = document.createElement("li");
    listItem.classList.add("list-group-item", "bg-danger", "text-white");
    listItem.innerHTML = `
<div class="d-flex justify-content-between">
    <div>
        <strong>${currentAttack}</strong> Alert<br>
        <small>Detected at: ${timestamp}</small>
    </div>
    <span class="badge bg-light text-danger">${consecutiveAttacks}x</span>
</div>
`;

    // Remove default message if it exists
    if (
        attackHistory.children.length === 1 &&
        attackHistory.children[0].classList.contains("text-muted")
    ) {
        attackHistory.innerHTML = "";
    }
    attackHistory.prepend(listItem);
}

document.addEventListener("DOMContentLoaded", function() {
    const attackHistory = document.getElementById("attackHistory");
    attackHistory.innerHTML = `
<li class="list-group-item text-center text-muted">
    No security events detected
</li>
`;

    const alarmStatus = document.getElementById("alarmStatus");
    alarmStatus.innerHTML = `
<i class="bi bi-cloud-check text-secondary" style="font-size:5rem;"></i>
<h5 class="text-secondary">No Notification</h5>
`;
});
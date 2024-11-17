document.addEventListener("DOMContentLoaded", async () => {
    const dashboard = document.getElementById("dashboard");

    /**
     * Asynchronous function that fetches data from /api/sensors sent by a client
     * @returns Array of the sensor data (e.g. of form: [{sensor_id, last_value, dry_value, wet_value, interval_size},{...}])
     */
    async function fetchSensorData() {
        try {
            const response = await fetch("/api/sensors");
            if (!response.ok) {
                throw new Error(`HTTP Error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Error fetching sensor data:", error);
            return [];
        }
    }

    /**
     * Function to generate HTML-object for dynamic sensor-generation
     * @param {*} sensor Sensor-object fetched by fetchSensorData()
     * @returns HTML-object containing moisture-percentage, sensor id and styling
     */
    function createSensorRing(sensor) {
        const { sensor_id, last_value, dry_value, wet_value, interval_size } = sensor;

        // container for sensor
        const sensorBox = document.createElement("div");
        sensorBox.classList.add("sensor-box");

        // calculate moisture-percentage
        let moisturePercentage = parseInt(Math.floor((1-((last_value/wet_value) - 1)) * 100));

        // set color of corresponding sensor ring
        let ringColor = "";
        if (moisturePercentage >= 75 && moisturePercentage <= 100) {
            // moist
            moisturePercentage += "%";
            ringColor = "#4CAF50"; 
        } else if (moisturePercentage >= 50 && moisturePercentage < 75) {
            // mildy moist
            moisturePercentage += "%";
            ringColor = "yellowgreen";
        } else if (moisturePercentage >= 25 && moisturePercentage < 50) {
            // dry
            moisturePercentage += "%";
            ringColor = "orange";
        } else if (moisturePercentage >= 0 && moisturePercentage < 25) {
            // very dry
            moisturePercentage += "%";
            ringColor = "red";
        } else if (moisturePercentage > 1) {
            ringColor = "grey";
            moisturePercentage = "no value";
        } else {
            ringColor = "purple";
        }

        // display ring
        sensorBox.innerHTML = `
            <div class="sensor-ring" style="border-color: ${ringColor}">
                <span class="sensor-value">${moisturePercentage}</span>
            </div>
            <p class="sensor-id">${sensor_id}</p>
        `;

        return sensorBox;
    }

    /**
     * Asynchronous function to create the content for all sensors in the dashboard
     * and link the objects to their corresponding CSS-class
     */
    async function createSensorDisplay() {
        const sensorData = await fetchSensorData();

        if (!sensorData.length) {
            dashboard.innerHTML += "<p>Keine Sensordaten verfügbar.</p>";
            return;
        }

        // Container für Anzeige-Gruppen
        const groupContainer = document.createElement("div");
        groupContainer.classList.add("sensor-group-container");

        let currentGroup = document.createElement("div");
        currentGroup.classList.add("sensor-group");

        sensorData.forEach(sensor => {
            // Neues Sensor-Element erstellen
            const sensorElement = createSensorRing(sensor);
            currentGroup.appendChild(sensorElement);
            groupContainer.appendChild(currentGroup);
                
        });

        dashboard.appendChild(groupContainer);
    }


    await createSensorDisplay();
});
(function () {

    // --------------------------------------------------------
    // Heartbeat interval
    // 60 seconds = 60,000 milliseconds
    // --------------------------------------------------------

    const HEARTBEAT_INTERVAL = 60000;


    // --------------------------------------------------------
    // Send heartbeat to Flask
    // --------------------------------------------------------

    function sendHeartbeat() {

        fetch(window.HEARTBEAT_URL, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            }
        })

        .then(function (response) {

            // User is no longer logged in
            if (response.status === 401) {

                console.log(
                    "Heartbeat stopped: user is not logged in."
                );

                return null;
            }

            if (!response.ok) {

                throw new Error(
                    "Heartbeat request failed."
                );
            }

            return response.json();
        })

        .then(function (data) {

            if (!data) {
                return;
            }

            if (data.success) {

                console.log(
                    "Heartbeat sent successfully."
                );

            } else {

                console.log(
                    "Heartbeat failed:",
                    data.message
                );
            }
        })

        .catch(function (error) {

            console.log(
                "Heartbeat error:",
                error
            );

        });

    }


    // --------------------------------------------------------
    // Send first heartbeat immediately
    // --------------------------------------------------------

    sendHeartbeat();


    // --------------------------------------------------------
    // Continue sending heartbeat every 60 seconds
    // --------------------------------------------------------

    setInterval(
        sendHeartbeat,
        HEARTBEAT_INTERVAL
    );


})();
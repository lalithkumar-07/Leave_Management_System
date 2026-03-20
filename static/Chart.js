<!DOCTYPE html>
<html>
<head>
    <title>Faculty Leave Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Faculty Leaves</h1>
    <canvas id="leaveChart" width="400" height="180"></canvas>
    <script>
        const names = {{ faculty_names | tojson }};
        const taken = {{ leaves_taken | tojson }};
        const left = {{ leaves_left | tojson }};
        new Chart(document.getElementById('leaveChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: names,
                datasets: [
                  {
                    label: 'Leaves Taken',
                    data: taken,
                    backgroundColor: 'orange'
                  },
                  {
                    label: 'Leaves Left',
                    data: left,
                    backgroundColor: 'lightgreen'
                  }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    </script>
</body>
</html>

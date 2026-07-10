document.addEventListener('DOMContentLoaded', () => {
    const weightChartCtx = document.getElementById('weightChart');
    const caloriesChartCtx = document.getElementById('caloriesChart');
    const waterChartCtx = document.getElementById('waterChart');

    if (!weightChartCtx || !caloriesChartCtx || !waterChartCtx) {
        return; // Not on dashboard home page
    }

    fetch('/dashboard/chart-data')
        .then(res => res.json())
        .then(data => {
            const hasRecords = data.labels && data.labels.length > 0;
            
            // Define colors based on active theme
            const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
            const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
            const textColor = isDark ? '#a0a0ab' : '#4b5563';

            // 1. Weight Trend Chart (Line)
            if (hasRecords) {
                new Chart(weightChartCtx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Weight (kg)',
                            data: data.weight,
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                            fill: true,
                            tension: 0.4,
                            borderWidth: 2,
                            pointBackgroundColor: '#6366f1'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: { grid: { color: gridColor }, ticks: { color: textColor } },
                            y: { grid: { color: gridColor }, ticks: { color: textColor } }
                        }
                    }
                });
            } else {
                showPlaceholder(weightChartCtx, "No logs recorded yet. Complete profile or log weight.");
            }

            // 2. Calorie Target vs Consumed (Bar Chart)
            const todayCalories = data.calories && data.calories.length > 0 ? data.calories[data.calories.length - 1] : 0;
            const targetCalories = data.calorie_target || 2000;
            
            new Chart(caloriesChartCtx, {
                type: 'bar',
                data: {
                    labels: ['Consumed', 'Target'],
                    datasets: [{
                        data: [todayCalories, targetCalories],
                        backgroundColor: ['#a855f7', '#6366f1'],
                        borderRadius: 8,
                        barThickness: 30
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { grid: { display: false }, ticks: { color: textColor } },
                        y: { grid: { color: gridColor }, ticks: { color: textColor } }
                    }
                }
            });

            // 3. Water Target progress (Doughnut)
            const todayWater = data.water && data.water.length > 0 ? data.water[data.water.length - 1] : 0;
            const targetWater = data.water_target || 2500;
            const remainingWater = Math.max(0, targetWater - todayWater);
            
            new Chart(waterChartCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Logged', 'Remaining'],
                    datasets: [{
                        data: [todayWater, remainingWater],
                        backgroundColor: ['#06b6d4', 'rgba(6, 182, 212, 0.1)'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        })
        .catch(err => console.error("Error drawing dashboard charts:", err));

    function showPlaceholder(canvas, message) {
        const ctx = canvas.getContext('2d');
        canvas.style.display = 'none';
        const parent = canvas.parentNode;
        const div = document.createElement('div');
        div.className = 'text-center py-5 text-muted small';
        div.innerText = message;
        parent.appendChild(div);
    }
});

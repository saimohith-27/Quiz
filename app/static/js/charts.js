const rd = window.__RESULT_DATA__;

// -----------------------------
// Answer Distribution
// -----------------------------
new Chart(document.getElementById('statusChart'), {
  type: 'doughnut',
  data: {
    labels: Object.keys(rd.status),
    datasets: [{
      data: Object.values(rd.status)
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true
  }
});


// -----------------------------
// Category Performance
// -----------------------------
new Chart(document.getElementById('categoryChart'), {
  type: 'bar',
  data: {
    labels: Object.keys(rd.category),
    datasets: [{
      label: '% Score',
      data: Object.values(rd.category)
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Score (%)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Category'
        }
      }
    }
  }
});


// -----------------------------
// Time Analysis
// -----------------------------
new Chart(document.getElementById('timeChart'), {
  type: 'scatter',
  data: {
    datasets: [{
      label: 'Time per question (sec)',
      data: rd.timePoints.map((p, i) => ({
        x: i + 1,
        y: p[1]
      }))
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Question Number'
        },
        ticks: {
          stepSize: 1
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Time (seconds)'
        }
      }
    }
  }
});
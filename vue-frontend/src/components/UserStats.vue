<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import axios from 'axios'
import Navbar from './Navbar.vue'
import { Chart } from 'chart.js/auto'

const stats = ref({})
const trendData = ref([])
const loading = ref(true)
const error = ref('')

// chart refs
const statusCanvas = ref(null)
const trendCanvas = ref(null)

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:5000/api/user/my-statistics', {
      headers: { Authorization: `Bearer ${token}` }
    })

    stats.value = res.data.totals
    trendData.value = res.data.reservations_over_time
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load statistics'
  } finally {
    loading.value = false
  }
})

// watch to ensure DOM + data ready before rendering
watch([stats, trendData], async () => {
  if (!loading.value && !error.value) {
    await nextTick()
    renderCharts()
  }
})

function renderCharts() {
  // Pie Chart for Status Distribution
  if (statusCanvas.value) {
    new Chart(statusCanvas.value, {
      type: 'pie',
      data: {
        labels: ['Reserved', 'Occupied', 'Released'],
        datasets: [{
          data: [
            stats.value.reserved || 0,
            stats.value.occupied || 0,
            stats.value.released || 0
          ],
          backgroundColor: ['#ffc107', '#28a745', '#6c757d']
        }]
      },
      options: { plugins: { legend: { position: 'bottom' } } }
    })
  }

  // Line Chart for Reservations Over Time
  if (trendCanvas.value) {
    new Chart(trendCanvas.value, {
      type: 'line',
      data: {
        labels: trendData.value.map(t => t.date),
        datasets: [{
          label: 'Reservations Over Time',
          data: trendData.value.map(t => t.count),
          borderColor: '#007bff',
          backgroundColor: 'rgba(0, 123, 255, 0.2)',
          fill: true,
          tension: 0.3
        }]
      },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    })
  }
}
</script>

<template>
  <Navbar />
  <div class="container mt-4">
    <h2 class="text-primary text-center mb-4"> My Parking Statistics</h2>

    <div v-if="loading" class="text-center">Loading stats...</div>
    <div v-if="error" class="alert alert-danger text-center">{{ error }}</div>
    <div class="divider mb-3"></div>
    <div v-if="!loading && !error">
      <!-- Totals Summary -->
      <div class="row text-center mb-4">
        <div class="col"><h6>Total Reservations</h6><p>{{ stats.reservations }}</p></div>
        <div class="col"><h6>Reserved</h6><p>{{ stats.reserved }}</p></div>
        <div class="col"><h6>Occupied</h6><p>{{ stats.occupied }}</p></div>
        <div class="col"><h6>Released</h6><p>{{ stats.released }}</p></div>
        <!-- Round of stats.spent to two decimals -->        
        <div class="col"><h6>Total Spent</h6><p> ₹ {{ stats.spent ? stats.spent.toFixed(2) : '0.00' }}</p></div>
      </div>
      <div class="divider mb-3"></div>
      <!-- Charts -->
      <div class="row">
        <div class="col-md-6 mb-4"><canvas ref="statusCanvas"></canvas></div>
        <div class="col-md-6 mb-4"><canvas ref="trendCanvas"></canvas></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
h6 {
  font-weight: bold;
}
canvas {
  max-width: 100%;
  height: 300px !important;
}
.divider {
  height: 2px;
  background-color: #ccc;
  width: 100%;
  margin: auto;
}
</style>

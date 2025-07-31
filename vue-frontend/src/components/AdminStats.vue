<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import axios from 'axios'
import Navbar from './Navbar.vue'
import { Chart } from 'chart.js/auto'

const stats = ref({})
const lotData = ref([])
const loading = ref(true)
const error = ref('')

// chart refs
const spotsCanvas = ref(null)
const lotCanvas = ref(null)

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:5000/api/admin/statistics', {
      headers: { Authorization: `Bearer ${token}` }
    })

    stats.value = res.data.totals
    lotData.value = res.data.reservations_by_lot
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load statistics'
  } finally {
    loading.value = false
  }
})

// Watcher: when stats and lotData are loaded, render charts
watch([stats, lotData], async () => {
  if (!loading.value && !error.value) {
    await nextTick()
    renderCharts()
  }
})

function renderCharts() {
  // Pie Chart for Spot Status
  if (spotsCanvas.value) {
    new Chart(spotsCanvas.value, {
      type: 'pie',
      data: {
        labels: ['Available', 'Reserved', 'Occupied'],
        datasets: [{
          data: [
            stats.value.available_spots || 0,
            stats.value.reserved_spots || 0,
            stats.value.occupied_spots || 0
          ],
          backgroundColor: ['#28a745', '#ffc107', '#dc3545']
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          title: { display: true, text: 'Spot Status Distribution' },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || ''
                const value = context.raw || 0
                return `${label}: ${value} (${((value / stats.value.spots) * 100).toFixed(2)}%)`
              }
            }
          }
        }
      }
    })
  }

  // Bar Chart for Reservations by Lot
  if (lotCanvas.value) {
    new Chart(lotCanvas.value, {
      type: 'bar',
      data: {
        labels: lotData.value.map(l => l.lot),
        datasets: [{
          label: 'Reservations per Lot',
          data: lotData.value.map(l => l.count),
          backgroundColor: '#007bff'
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: { title: { display: true, text: 'Parking Lots' } },
          y: { title: { display: true, text: 'Number of Reservations' }, beginAtZero: true }
        },
        plugins: {
          legend: { display: false },
          title: { display: true, text: 'Reservations by Parking Lot' },
          tooltip: {
            callbacks: {
              label: (context) => {
                const value = context.raw || 0
                return `Reservations: ${value} (${((value / stats.value.reservations) * 100).toFixed(2)}%)`
              }
            }
          }
        }
      }
    })
  }
}
</script>

<template>
  <Navbar />
  <div class="container mt-4">
    <h2 class="text-primary text-center mb-4">📊 Admin Statistics</h2>

    <div v-if="loading" class="text-center">Loading stats...</div>
    <div v-if="error" class="alert alert-danger text-center">{{ error }}</div>
    <div class="divider mb-3"></div>
    <div v-if="!loading && !error">
      <!-- Totals Summary -->
      <div class="row text-center mb-2">
        <div class="col"><h6>Users</h6><p>{{ stats.users }}</p></div>
        <div class="col"><h6>Lots</h6><p>{{ stats.lots }}</p></div>
        <div class="col"><h6>Spots</h6><p>{{ stats.spots }}</p></div>
        <div class="col"><h6>Available</h6><p>{{ stats.available_spots }}</p></div>
        <div class="col"><h6>Reserved</h6><p>{{ stats.reserved_spots }}</p></div>
        <div class="col"><h6>Occupied</h6><p>{{ stats.occupied_spots }}</p></div>
        <div class="col"><h6>Reservations</h6><p>{{ stats.reservations }}</p></div>
        <div class="col"><h6>Revenue</h6><p>₹ {{ stats.revenue }}</p></div>
      </div>
    <div class="divider mb-3"></div>
      <!-- Charts -->
      <div class="row">
        <div class="col-md-6 mb-4"><canvas ref="spotsCanvas"></canvas></div>
        <div class="col-md-6 mb-4"><canvas ref="lotCanvas"></canvas></div>
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

<script setup>
import { ref, onMounted, setTransitionHooks } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'
import Navbar from './Navbar.vue'

const reservations = ref([])
const token = localStorage.getItem('token')
const router = useRouter()
const route = useRoute()
const userName = ref('')
const userId = route.params.userId
const role = ref('')
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  console.log(`Fetching reservations for user ID: ${userId}`)
    if (!token) {
      router.push('/login')
      return
    }
    const decoded = jwtDecode(token)
    role.value = decoded.role
    if (role.value !== 'admin') {
      error.value = 'Only admins can view user reservations!'
      return
    }
    fetchReservations()
})

// Refresh reservations data
const fetchReservations = async () => {
  try {
    const res = await axios.get(`http://localhost:5000/api/admin/get-user-reservations/${userId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    reservations.value = res.data
    console.log(`Reservations of user id ${userId} fetched:`, reservations.value)
    userName.value = reservations.value.length > 0 ? reservations.value[0].user_name : 'Unknown User'
  } catch (err) {
    console.error('Failed to fetch reservations:', err)
    error.value = 'Failed to load reservations.'
  } finally {
    loading.value = false
  }
}

const formatDuration = (start, end) => {
  if (!start || !end) return '-'
  const startTime = new Date(start)
  const endTime = new Date(end)
  let diffMs = endTime - startTime
  if (diffMs < 0) return '-'

  const totalMinutes = Math.floor(diffMs / (1000 * 60))
  const hours = Math.floor(totalMinutes / 60)
  const mins = totalMinutes % 60

  if (hours > 0 && mins > 0) return `${hours} hrs ${mins} mins`
  if (hours > 0) return `${hours} hrs`
  return `${mins} mins`
}

const getStatus = (res) => {
  if (!res.parking_timestamp) return 'R'
  if (res.parking_timestamp && !res.leaving_timestamp) return 'O'
  return 'X'
}

const getStatusColor = (status) => {
  return status === 'R' ? 'warning' : status === 'O' ? 'success' : 'secondary'
}

const getStatusText = (status) => {
  return status === 'R' ? 'Reserved' : status === 'O' ? 'Occupied' : 'Released'
}

const calculateHours = (start, end) => {
  if (!start || !end) return '-'
  const startTime = new Date(start)
  const endTime = new Date(end)
  const diff = (endTime - startTime) / (1000 * 60 * 60)
  // console.log(`Calculating hours: start=${start}, end=${end}, diff=${diff}`)
  if (diff < 1) return '1' // Minimum charge for less
  return diff.toFixed(1)
}
</script>

<template>
  <Navbar />
  <div class="container mt-4">
    <h2 class="text-primary mb-4 text-center">Reservations done by {{ userName }} (ID #{{ userId }})</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    <div v-if="error" class="alert alert-danger text-center">{{ error }}</div>
    <div v-if="!loading && reservations.length > 0" class="table-responsive">
      <table class="table table-bordered table-hover align-middle text-center table-striped">
        <thead class="table-light">
          <tr>
            <th>Lot Address</th>
            <th>Spot ID</th>
            <th>Cost per hour</th>
            <th>Booked At</th>
            <th>Vehicle Number</th>
            <th>Time Parked</th>
            <th>Time Released</th>
            <th>Hours</th>
            <th>Total Cost</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(res, index) in reservations" :key="res.reservation_id">
            <td><strong>Lot #{{ res.lot_id }}:</strong> {{ res.lot_address }}, {{ res.lot_city }}, {{ res.lot_pincode }}.</td>
            <td>{{ res.spot_id }}</td>
            <td>₹ {{ res.lot_price }}</td>
            <td>{{ res.booked_at }}</td>
            <td>{{ res.vehicle_number }}</td>
            <td>{{ res.parking_timestamp || '-' }}</td>
            <td>{{ res.leaving_timestamp || '-' }}</td>


            <td v-if="!res.parking_timestamp && !res.leaving_timestamp">NA</td>
            <td v-else-if="res.parking_timestamp && !res.leaving_timestamp">
            {{ formatDuration(res.parking_timestamp, new Date()) }}
          </td>

          <td v-else>
            {{ formatDuration(res.parking_timestamp, res.leaving_timestamp) }}
          </td>
            <td>{{ res.parking_cost !== null ? `₹${res.parking_cost}` : '-' }}</td>
            <td>
              <span :class="`badge bg-${getStatusColor(getStatus(res))}`">
                {{ getStatusText(getStatus(res)) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="alert alert-info text-center">No reservations found.</div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1500px;
}
.table {
  font-size: 1rem;
} 
.table th, .table td {
  vertical-align: middle;
}

</style>

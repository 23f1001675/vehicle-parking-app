<script setup>
import { ref, onMounted, setTransitionHooks } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'
import Navbar from './Navbar.vue'

const reservations = ref([])
const token = localStorage.getItem('token')
const router = useRouter()
const role = ref('')
const error = ref('')
const status = ref('')
const message = ref('')
const loading = ref(true)

onMounted(async () => {
    console.log(String(new Date()).slice(0, 24))
    if (!token) {
      router.push('/login')
      return
    }
    const decoded = jwtDecode(token)
    // console.log('Decoded token:', decoded)
    role.value = decoded.role
    fetchReservations()
})

const startExport = async () => {
  const res = await axios.post("http://localhost:5000/api/user/export", {}, {
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
  })
  const taskId = res.data.task_id
  status.value = "Export started... waiting"

  const interval = setInterval(async () => {
    try {
      const check = await axios.get(`http://localhost:5000/api/user/export/${taskId}`, {
        responseType: "blob", // may be JSON blob or CSV blob
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      })

      const contentType = check.headers["content-type"] || ""
      if (contentType.includes("text/csv")) {
        // ✅ Got CSV → download it
        clearInterval(interval)
        const blob = new Blob([check.data], { type: "text/csv" })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.setAttribute("download", "reservations.csv")
        document.body.appendChild(link)
        link.click()
        status.value = "Download complete!"
      } else {
        // ✅ Got JSON {status: "..."} instead
        const text = await check.data.text()
        const data = JSON.parse(text)
        status.value = data.status
      }
    } catch (err) {
      clearInterval(interval)
      console.error("Export failed:", err)
      status.value = "Export failed"
    }
  }, 2000)
}


// Refresh reservations data
const fetchReservations = async () => {
  try {
    const res = await axios.get(`http://localhost:5000/api/user/my-reservations`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    reservations.value = res.data
    // console.log('Reservations fetched:', reservations.value)
  } catch (err) {
    console.error('Failed to fetch reservations:', err)
    error.value = 'Failed to load reservations.'
  } finally {
    loading.value = false
  }
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

const parkNow = async (reservationId) => {
  try {
    await axios.post(`http://localhost:5000/api/user/occupy-reserved-spot/${reservationId}`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await fetchReservations()
  } catch (err) {
    console.error('Error parking now:', err)
    error.value = err.response?.data?.msg || 'Failed to park now.'
  }
}

const releaseSpot = async (reservationId) => {
  try {
    const res = await axios.post(
      `http://localhost:5000/api/user/release-spot/${reservationId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    console.log("Released:", res.data) // includes hours and cost
    await fetchReservations()
  } catch (err) {
    console.error('Error releasing:', err)
    error.value = err.response?.data?.msg || 'Failed to release spot.'
  }
}
</script>

<template>
  <Navbar />
  <div class="container mt-4">
    <h2 class="text-primary mb-4 text-center">My Reservations </h2>
     <div>
      <button @click="startExport" class="btn btn-success mb-4">Export CSV</button>
      <p v-if="status">{{ status }}</p>
    </div>
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
            <th>Vehicle Number</th>
            <th>Cost per hour</th>
            <th>Booked At</th>
            <th>Time Parked</th>
            <th>Time Released</th>
            <th>Time parked</th>
            <th>Cost</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(res, index) in reservations" :key="res.reservation_id">
            <td><strong>Lot #{{ res.lot_id }}:</strong> {{ res.lot_address }}, {{ res.lot_city }}</td>
            <td>{{ res.spot_id }}</td>
            <td>{{ res.vehicle_number }}</td>
            <td>₹ {{ res.lot_cost }}</td>
            <td>{{ res.booked_at }}</td>
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
            <td>
              <button
                v-if="getStatus(res) === 'R'"
                class="btn btn-success btn-sm"
                @click="parkNow(res.reservation_id)"
              >
                Park Now
              </button>
              <button
                v-if="getStatus(res) === 'O'"
                class="btn btn-danger btn-sm"
                @click="releaseSpot(res.reservation_id)"
              >
                Release
              </button>
              <span v-if="getStatus(res) === 'X'" class="text-muted">No action</span>
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

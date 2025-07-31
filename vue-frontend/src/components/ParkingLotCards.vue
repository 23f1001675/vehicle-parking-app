<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'

const lots = ref([])
const loading = ref(true)
const role = ref('')
const error = ref('')
const success = ref('')
const showPopup = ref(false)
const vehicleNumbers = ref({})
const popupMessage = ref('')
const token = localStorage.getItem('token')

onMounted(async () => {
    if (token) {
    const decoded = jwtDecode(token)
    role.value = decoded.role
    }
    fetchLots()
})

const fetchLots = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/admin/get-all-lots', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    lots.value = res.data
  } catch (err) {
    console.error('❌ Failed to fetch parking lots:', err)
  }
  finally {
    loading.value = false
  }
}

const reserveSpot = async (lotId) => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post(`http://localhost:5000/api/user/reserve-spot/${lotId}`, 
    { vehicle_number: vehicleNumbers.value[lotId] },
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    console.log(`✅ Spot reserved response:`, res.data)
    popupMessage.value = `✅ Reservation successful! Spot ID: ${res.data.spot_id}.`
    showPopup.value = true
    await fetchLots()
  } catch (err) {
    popupMessage.value = err.response?.data?.msg || 'Reservation failed.'
    showPopup.value = true
  }
}

const confirmDelete = (lotId) => {
  const lot = lots.value.find(l => l.id === lotId)
  if (!lot) {
    console.error(`❌ Lot # ${lotId} not found:`)
    return
  }
  if (lot.available_spots < lot.total_spots) {
    alert(`❌ Cannot delete Lot #${lotId}. Make sure all spots are empty.`);
    console.warn(`❌ Cannot delete Lot #${lotId}. Available: ${lot.available_spots}, Total: ${lot.total_spots}`);
    return;
  }

  console.log(`✅ Lot #${lotId} is eligible for deletion.`)
  if (window.confirm(`Are you sure you want to delete Lot #${lotId}? This cannot be undone.`)) {
    axios.delete(`http://localhost:5000/api/admin/delete-lot/${lotId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    .then(() => {
      lots.value = lots.value.filter(lot => lot.id !== lotId)
      success.value = `Parking lot #${lotId} deleted successfully.`
      setTimeout(() => {
        success.value = ''
      }, 1000)
    })
    .catch(err => {
      error.value = err.response?.data?.msg || 'Failed to delete parking lot.'
      console.error('❌ Error deleting parking lot:', err)
    })
  }
}
</script>

<template>
  <div class="container mt-4">
    <div v-if="error" class="alert alert-danger text-center">{{ error }}</div>
    <div v-if="success" class="alert alert-success text-center">{{ success }}</div>
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    <div v-else class="row gx-4 gy-4">
      <div
        v-for="lot in lots"
        :key="lot.id"
        class="col-12 col-md-4 d-flex align-items-stretch"
      >
        <div class="card lot-card w-100 postion-relative">
          <!-- Edit and Delete Action -->
          <div v-if="role === 'admin'" class="card-actions position-absolute top-0 end-0 p-2">
            <router-link :to="`/admin/edit-lot/${lot.id}`" style="text-decoration: none;" class="edit-button">Edit</router-link>
            <i class="bi bi-trash3-fill text-danger pointer" @click="confirmDelete(lot.id)"></i>
          </div>
          <!-- Card body -->
          <div class="card-body d-flex flex-column justify-content-between">
            <div>
              <h5 class="card-title text-primary">Lot #{{ lot.id }}</h5>
              <p class="card-text"><strong>City:</strong> {{ lot.city }}</p>
              <p class="card-text"><strong>Address:</strong> {{ lot.address }}</p>
              <p class="card-text"><strong>Pincode:</strong> {{ lot.pincode }}</p>
              <p class="card-text"><strong>Price/hr:</strong> ₹{{ lot.price }}</p>
              <p class="card-text">
                <strong>Available:</strong> {{ lot.available_spots }} / {{ lot.total_spots }}
              </p>
            </div>
            <router-link v-if="role === 'admin'" :to="`/admin/view-lot/${lot.id}`" class="btn btn-outline-primary btn-sm mt-3">
              View Details
            </router-link>
            <input v-if="role === 'user'" type="text" class="form-control mt-2" placeholder="Enter Vehicle Number" v-model="vehicleNumbers[lot.id]" :disabled="lot.available_spots === 0" required>
            <button v-if="role === 'user' && lot.available_spots > 0" class="btn btn-outline-primary btn-sm mt-2" @click="reserveSpot(lot.id)">
              Reserve a Spot
            </button>
            <button v-if="role === 'user' && lot.available_spots == 0" class="btn btn-secondary btn-sm mt-3" disabled>
              No Spots Available
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- Modal Backdrop -->
     <transition name="fade">
    <div
      v-if="showPopup"
      class="modal-backdrop"
      style="position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.5); z-index: 1050;">
    </div>
    </transition>
    <!-- Centered Popup Modal -->
     <transition name="popup">
    <div
      v-if="showPopup"
      class="bg-light rounded shadow p-4 text-center"
      style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            z-index: 1100;" 
    >
      <p class="mb-3">{{ popupMessage }}</p>
      <button class="btn btn-primary" @click="() => { showPopup = false }">
        OK
      </button>
    </div>
    </transition>
  </div>
</template>

<style scoped>
.edit-button {
  position: relative;
  display: inline-block;
  color: #0d6efd;
  font-weight: 500;
}

.edit-button::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -2px;
  width: 0;
  height: 2px;
  background-color: #0d6efd;
  transition: width 0.3s ease;
}

.edit-button:hover::after {
  width: 100%;
}

.lot-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: none;
  border-radius: 16px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.08);
}
.lot-card:hover {
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.card-title {
  font-weight: 600;
}

.card-text {
  margin-bottom: 8px;
}

.btn-sm {
  border-radius: 8px;
  transition: background-color 0.2s ease, transform 0.2s ease;
}
.btn-sm:hover {
  transform: scale(1.01);
}
.card-actions {
  z-index: 2;
}

.pointer {
  cursor: pointer;
  padding-left: 1rem;
  padding-right: 1rem;
  display: inline-block;
  transition: transform 0.2s ease;
}

.pointer:hover {
  transform: scale(1.2);
  color: #dc3545; /* or any accent */
  text-shadow: 0 0 3px rgba(0,0,0,0.2);
}
/* Fade for backdrop */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Popup animation */
.popup-enter-active, .popup-leave-active {
  transition: all 0.35s ease;
}
.popup-enter-from, .popup-leave-to {
  opacity: 0;
  transform: translate(-50%, -60%) scale(0.95);
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050;
  opacity: 1;
}

/* Smooth fade animation for backdrop */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

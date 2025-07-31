<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Navbar from './Navbar.vue'

const route = useRoute()
const router = useRouter()
const lotId = route.params.id

const city = ref('')
const address = ref('')
const pincode = ref('')
const price = ref(0)
const number_of_spots = ref(0)
const error = ref('')
const success = ref('')

onMounted(async () => {
  try {
    const res = await axios.get(`http://localhost:5000/api/admin/get-lot/${lotId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    const lot = res.data
    city.value = lot.city
    address.value = lot.address
    pincode.value = lot.pincode
    price.value = lot.price
    number_of_spots.value = lot.total_spots
  } catch (err) {
    console.error('❌ Failed to fetch lot:', err)
    error.value = 'Could not load parking lot data.'
  }
})

const updateLot = async () => {
  error.value = ''
  success.value = ''
  try {
    await axios.put(`http://localhost:5000/api/admin/edit-lot/${lotId}`, {
      city: city.value,
      address: address.value,
      pincode: pincode.value,
      price: price.value,
      number_of_spots: number_of_spots.value
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    success.value = '✅ Parking lot updated successfully.'
    setTimeout(() => router.push('/admin/dashboard'), 1000)
  } catch (err) {
    console.error('❌ Update failed:', err)
    //Print msg
    error.value = err.response?.data?.msg || 'Failed to update parking lot.'
  }
}
</script>

<template>
  <Navbar />
  <div class="container mt-5" style="max-width: 500px;">
    <h2 class="mb-4 text-center text-primary">Edit details of Parking Lot #{{ lotId }}</h2>
    <div v-if="error" class="alert alert-danger mt-3 text-center">{{ error }}</div>
    <div v-if="success" class="alert alert-success mt-3 text-center">{{ success }}</div>
    <form @submit.prevent="updateLot">
      <div class="mb-3">
            <label class="form-label">City</label>
            <input v-model="city" type="text" class="form-control" :placeholder="city" required />
        </div>
        <div class="mb-2">
            <label class="form-label">Address</label>
            <input v-model="address" type="text" class="form-control" :placeholder="address" required />
        </div>
        <div class="mb-2">
            <label class="form-label">Pincode</label>
            <input v-model="pincode" type="text" class="form-control" :placeholder="pincode" required />
        </div>
        <div class="mb-3">
            <label class="form-label">Price per hour (₹)</label>
            <!-- Minimum 0 -->  
            <input v-model="price" type="number" class="form-control" :placeholder="price" min="0" required />
        </div>

        <div class="mb-3">
            <label class="form-label">Number of Spots</label>
            <input v-model="number_of_spots" type="number" class="form-control" :placeholder="number_of_spots" min="0" required />
        </div>
      <button type="submit" class="btn btn-success w-100">Update Lot</button>
      <button type="button" class="btn btn-secondary w-100 mt-2" @click="router.push('/admin/dashboard')">Cancel</button>
    </form>

  </div>
</template>

<style scoped>
label {
    font-weight: 500;
}
</style>
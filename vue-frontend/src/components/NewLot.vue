<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Navbar from './Navbar.vue';

const router = useRouter();
const city = ref('');
const address = ref('');
const pincode = ref('');
const price = ref(0);
const number_of_spots = ref(0);
const error = ref('');
const success = ref('');

const newLot = async () => {
  error.value = '';
  try {
    const res = await axios.post('http://localhost:5000/api/admin/create-new-lot',
    {
      city: city.value,
      address: address.value,
      pincode: pincode.value,
      price: price.value,
      number_of_spots: number_of_spots.value
    },
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    console.log('✅ New lot created:', res.data);
    success.value = `✅ New Lot created successfully!`;
    setTimeout(() => router.push('/admin/dashboard'), 1000)
  } catch (err) {
    console.error('❌ Error creating new lot:', err);
    error.value =err.response?.data?.msg || 'Failed to create new lot.';
  }
};
</script>

<template>
  <Navbar />
  <div class="container mt-5" style="max-width: 400px;">
    <h2 class="mb-4 text-center text-primary">Create a new parking lot</h2>
    <form @submit.prevent="newLot">
      <div v-if="error" class="alert alert-danger mt-3 text-center">{{ error }}</div>
      <div v-if="success" class="alert alert-success mt-3 text-center">{{ success }}</div>
        <div class="mb-3">
            <label class="form-label">City</label>
            <input v-model="city" type="text" class="form-control" placeholder="Enter city name" required />
        </div>
        <div class="mb-3">
            <label class="form-label">Address</label>
            <input v-model="address" type="text" class="form-control" placeholder="Enter parking lot address" required />
        </div>
        <div class="mb-3">
            <label class="form-label">Pincode</label>
            <input v-model="pincode" type="text" class="form-control" placeholder="Enter area pincode" required />
        </div>
        <div class="mb-3">
            <label class="form-label">Price per hour (₹)</label>
            <!-- Minimum 0 -->  
            <input v-model="price" type="number" class="form-control" placeholder="Enter price per hour" min="0" required />
        </div>

        <div class="mb-3">
            <label class="form-label">Number of Spots</label>
            <input v-model="number_of_spots" type="number" class="form-control" placeholder="Enter number of spots" min="0" required />
        </div>
        <button type="submit" class="btn btn-primary w-100">Create Lot</button>
        <button type="button" class="btn btn-secondary w-100 mt-2" @click="router.push('/admin/dashboard')">Cancel</button>
        <div class="mt-5"></div>
    </form>
  </div>
</template>


<style scoped>
label {
    font-weight: 500;
}
</style>
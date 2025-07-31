<script setup>
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import Navbar from './Navbar.vue';

const route = useRoute();
const lotId = route.params.id;

const lot = ref({});
const spots = ref([]);
const error = ref('');
const loading = ref(true);

onMounted(async () => {
  try {
    const res = await axios.get(`http://localhost:5000/api/admin/get-lot/${lotId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    lot.value = res.data;
    spots.value = res.data.spots || [];
    console.log('✅ Lot data loaded:', lot.value); // Lot object
    console.log('✅ Spots data loaded:', spots.value); //Array of spot objects

  } catch (err) {
    console.error('❌ Failed to fetch lot:', err);
    error.value = 'Could not load parking lot data.';
  } finally {
    loading.value = false;
  }
});

function toIST(dateStr) {
  if (!dateStr) return '-'
  const utcDate = new Date(dateStr)
  return utcDate.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
}
</script>

<template>
  <Navbar />
  <div class="container mt-2">
    <h2 class="text-center text-success mb-3">Parking Lot #{{ lot?.id || '-' }}</h2>
    <p class="text-center text-muted mb-1">
      <strong>City:</strong> {{ lot.city || '-' }} |
      <strong>Address:</strong> {{ lot.address || '-' }} |
      <strong>Pincode:</strong> {{ lot.pincode || '-' }} |
      <strong>Price per hour:</strong> ₹{{ lot.price || '-' }} 
    </p>
    <p class="text-center text-muted mt-2" v-if="lot?.total_spots !== undefined">
      <strong>Total Spots:</strong> {{ lot.total_spots || '-' }} |
      <strong>Available:</strong> {{ lot.available_spots || '0' }} |
      <strong>Occupied:</strong> {{ lot.total_spots - lot.available_spots - lot.reserved_spots || '0' }} |
      <strong>Reserved:</strong> {{ lot.reserved_spots || '0' }}
    </p>

    <div class="divider mb-4"></div>

    <div v-if="error" class="alert alert-danger text-center">{{ error }}</div>
    <div v-if="loading" class="text-center text-primary">Loading parking layout...</div>

    <div v-else class="spots-grid">
  <div
    v-for="spot in spots"
    :key="spot.id"
    class="spot-container"
  >
    <div class="spot-id">{{ spot.id }}</div>
    <div
      class="spot-box"
      :class="{ available: spot.status === 'A', occupied: spot.status === 'O', reserved: spot.status === 'R' }"
    >
      <span>{{ spot.status }}</span>
      <div v-if="spot.user" class="hover-info">
        <div class="tooltip-arrow"></div>
        <p><strong>{{ spot.user.name }}</strong> (ID #{{ spot.user.id }})</p>
        <p>Email: {{ spot.user.email }}</p>
        <p>User's Pincode: {{ spot.user.user_pincode }}</p>
        <p v-if="spot.user.vehicle_number">Vehicle: {{ spot.user.vehicle_number }}</p>
        <p v-if="spot.user.booked_at">Booked At: {{ toIST(spot.user.booked_at) }}</p>
        <p v-if="spot.user.parking_timestamp">Parking at: {{ toIST(spot.user.parking_timestamp) }}</p>  
      </div>
    </div>
  </div>
</div>

  </div>
</template>


<style scoped>

.divider {
  height: 2px;
  background-color: #ccc;
  width: 100%;
  margin: auto;
}

.spots-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: left;
  margin-top: 10px;
  margin-left: 15px;
}

.spot-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 2px;
}

.spot-id {
  font-size: 13px;
  color: #555;
  margin-bottom: 2px;
}

.spot-box {
  width: 50px;
  height: 50px;
  /* border: 1px solid #0066cc; */
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  border-radius: 8px;
  transition: transform 0.2s;
}

.spot-box:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.spot-box.available {
  background-color: #d1fbd6;
  color: #2c662d;
}

.spot-box.occupied {
  background-color: #ffcdd2;
  color: #b71c1c;
}

.spot-box.reserved {
  background-color: #fff3cd;
  color: #856404;
}
.hover-info {
  display: none;
  position: absolute;
  top: 110%; /* show above */
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  color: #333;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  z-index: 9999;
}

.spot-box:hover .hover-info {
  display: block;
}

.tooltip-arrow {
  position: absolute;
  top: -6px; 
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 6px solid #fff;  /* same as tooltip bg */
  filter: drop-shadow(0 -1px 1px rgba(0,0,0,0.15));
}
</style>

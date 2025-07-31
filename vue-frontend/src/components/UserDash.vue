<script setup>
import Navbar from './Navbar.vue'
import ParkingLotCards from './ParkingLotCards.vue';
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';

//router
const route = useRoute();
const userId = route.params.id;
const user = ref({});

onMounted(async () => {
  const res = await axios.get(`http://localhost:5000/api/user/get-user-details/${userId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`
    }
  })
  user.value = res.data;
  // console.log("User data fetched:", user.value);
});

</script>

<template>  
    <Navbar />
  <div class="container mt-3">
    <h1 class="text-success " style="margin-left: 20px;">Welcome, {{ user.name }}!</h1>
    <p style="margin-left: 20px;">Reserve your parking spot now right away! Simple and Easy.</p>
    <ParkingLotCards />
  </div>
</template>

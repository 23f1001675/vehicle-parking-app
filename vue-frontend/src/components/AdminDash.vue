<script setup>
import Navbar from './Navbar.vue'
import ParkingLotCards from './ParkingLotCards.vue';

</script>

<template>
  <Navbar />
  <div class="container mt-3">
    <h1 class="text-success" style="margin-left: 20px;">Welcome Admin!</h1>
    <p style="margin-left: 20px;">You can manage the parking system by creating, editing and deleting parking lots!</p>
    <router-link to="/admin/create-new-lot" style="margin-left: 20px;" class="btn btn-primary">Create New Parking Lot</router-link>
    <ParkingLotCards />
  </div>
</template> 
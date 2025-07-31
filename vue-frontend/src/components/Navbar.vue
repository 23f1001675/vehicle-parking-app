<script setup>
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'
import { jwtDecode } from 'jwt-decode'
import logo from '../images/logo.png'

const router = useRouter()
const role = ref('')
const userId = ref('')

// Logout method
const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

// Decode token to get role and userId
try {
  const token = localStorage.getItem('token')
  if (token) {
    const decoded = jwtDecode(token)
    role.value = decoded.role
    userId.value = decoded.sub || decoded.id
  }
} catch (e) {
  console.error('Token decode failed:', e)
}

// Compute dashboard route based on role
const dashboardLink = computed(() => {
  if (role.value === 'admin') return '/admin/dashboard'
  if (role.value === 'user') return `/user/${userId.value}/dashboard`
  return '/'
})
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-white bg-white shadow-sm sticky-top">
    <div class="container-fluid">
      <router-link :to="dashboardLink" class="d-flex align-items-center text-decoration-none me-4" id="navbar-brand">
        <img :src="logo" alt="AutoPark Logo" style="width: 48px; height: 48px;" />
        <span class="ms-2 fw-bold fs-5 text-dark">AutoPark</span>
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbar"
        aria-controls="navbar"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbar">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li v-if="role === 'admin'" class="nav-item">
            <router-link class="nav-link" to="/admin/view-all-users">Manage Users</router-link>
          </li>
          <li v-if="role === 'admin'" class="nav-item ">
            <router-link class="nav-link" to="/admin/statistics">Statistics</router-link>
          </li>

          <li v-if="role === 'user'" class="nav-item">
            <router-link class="nav-link" to="/user/my-reservations">My Reservations</router-link>
          </li>
          <li v-if="role === 'user'" class="nav-item">
            <router-link class="nav-link" to="/user/my-statistics">Statistics</router-link>
          </li>
        </ul>

        <button class="btn btn-outline-light ms-auto" id="logout-btn" @click="logout">Logout</button>
      </div>
    </div>
  </nav>
</template>

<style scoped>
#navbar-brand {
  margin-left: 50px;
}
#logout-btn {
  margin-right: 50px;
  font-weight: 500;
  color: #639fd3;
}
.navbar {
  font-weight: 500;
  border-bottom: 1px solid #ddd;
}
.router-link-active {
  font-weight: bold;
  color: #176899 !important;
}
</style>

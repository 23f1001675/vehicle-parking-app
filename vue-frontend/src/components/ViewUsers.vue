<script setup>  
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'
import Navbar from './Navbar.vue'

const users = ref([])
const token = localStorage.getItem('token')
const router = useRouter()
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    if (!token) {
      router.push('/login')
      return
    }
    const decoded = jwtDecode(token)
    if (decoded.role !== 'admin') {
      error.value = 'Only admins can view all users data!'
      return
    }
    const res = await axios.get('http://localhost:5000/api/admin/get-all-users', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    users.value = res.data
    console.log('Users data fetched:', users.value)
  } catch (err) {
    console.error('Failed to fetch reservations:', err)
    error.value = 'Failed to load reservations.'
  } finally {
    loading.value = false
  }
})

const goToUserReservations = (userId) => {
  router.push({ name: 'ViewUserReservations', params: { userId } })
}
</script>

<template>
  <Navbar />
  <div class="container mt-4">
    <h2 class="text-primary mb-4 text-center">Users Data</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-if="error" class="alert alert-danger text-center">{{ error }}</div>
    <div v-if="!loading && !error && users.length !== 0">
      <table class="table table-bordered table-striped table-hover text-center">
        <thead>
          <tr>
            <th>User ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Residing Pincode</th>
            <th>Date Registered</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in users"
            :key="user.id"
            @click="goToUserReservations(user.id)"
            style="cursor: pointer;"
          >
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.user_pincode }}</td>
            <td>{{ user.date_joined }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="alert alert-info text-center">No users found.</div>
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

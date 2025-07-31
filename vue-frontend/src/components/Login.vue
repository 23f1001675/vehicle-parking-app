<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')

const login = async () => {
  error.value = ''
  try {
    const res = await axios.post('http://localhost:5000/api/auth/login', {
      email: email.value,
      password: password.value
    })
    console.log('✅ Login successful:', res.data)

    const token = res.data.access_token
    localStorage.setItem('token', token)

    const decoded = jwtDecode(token)
    console.log('📦 Decoded token:', decoded)

    if (decoded.role === 'admin') {
      console.log('Redirecting to admin dashboard....')
      router.push('/admin/dashboard')
    } else if (decoded.role === 'user') {
      console.log('Redirecting to user dashboard....')
      router.push(`/user/${decoded.sub || decoded.id}/dashboard`)
    } else {
      console.log('🚫 Role not recognized:', decoded.role)
      error.value = 'Unauthorized role.'
    }

  } catch (err) {
    console.error('❌ Login error:', err)
    error.value = 'Invalid email or password'
  }
}

</script>

<template>
  <div class="container mt-5" style="max-width: 400px;">
    <h2 class="mb-4 text-center text-primary">Login</h2>
    <form @submit.prevent="login">
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="email" type="email" class="form-control" placeholder="something@domain.com" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-control" placeholder="Enter password" required />
      </div>
      <button type="submit" class="btn btn-primary w-100">Login</button>
    </form>
    <br>
    <div class="mt-3 text-center">
      <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
    </div>
    <div v-if="error" class="alert alert-danger mt-3 text-center">{{ error }}</div>
  </div>
</template>

<!-- Registration page => form fields are name, email, password -->
<script setup>
import { useRouter } from 'vue-router' 
import { ref } from 'vue'
import axios from 'axios'

const router = useRouter()
const name = ref('')
const email = ref('')
const user_pincode = ref('')
const password = ref('')
const error = ref('')
const register = async () => {
  error.value = ''
  try {
    const res = await axios.post('http://localhost:5000/api/auth/register', {
      name: name.value,
      email: email.value,
      password: password.value,
      user_pincode: user_pincode.value,
    })
    console.log(res.data)
    alert('Registration successful. Redirecting to login page.')
    router.push('/login')
  } catch (err) {
    error.value = 'Registration failed. Please try again.'
    console.error(err)
  }
}
</script>

<template>
  <div class="container mt-5" style="max-width: 400px;">
    <h2 class="mb-4 text-center text-primary">Register</h2>
    <form @submit.prevent="register">
      <div class="mb-3">
        <label class="form-label">Name</label>
        <input v-model="name" type="text" class="form-control" placeholder="Enter name" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="email" type="email" class="form-control" placeholder="something@domain.com" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Pincode</label>
        <input v-model="user_pincode" type="text" class="form-control" placeholder="Enter your area pincode" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Your Password</label>
        <input v-model="password" type="password" class="form-control" placeholder="Set a password" required />
      </div>

      <button type="submit" class="btn btn-primary w-100">Register</button>
    </form>
    <div class="mt-3 text-center">
      <p>Already have an account? <router-link to="/login">Login here</router-link></p>
    </div>
    <div v-if="error" class="alert alert-danger mt-3 text-center">{{ error }}</div>
  </div>
</template>

<style scoped>
.container {
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
</style>
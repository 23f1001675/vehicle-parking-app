<script setup>
import { useRouter } from 'vue-router'
import logo from '../images/logo.png'
const router = useRouter()

const goToLogin = () => router.push('/login')
const goToRegister = () => router.push('/register')
</script>

<template>
  <div class="landing-page d-flex flex-column justify-content-center align-items-center vh-100 text-center">
    <img :src="logo" alt="AutoPark Logo" class="logo mb-4" />
    <h1 class="title mb-3">Welcome to AutoPark</h1>
    <p class="subtitle mb-4">Tap. Reserve. Park. It's that simple.</p>
    <slot></slot>
    <div class="d-flex gap-3">
      <button class="btn neon-btn px-4" @click="goToLogin">Login</button>
      <button class="btn neon-btn-outline px-4" @click="goToRegister">Register</button>
    </div>
  </div>
</template>

<style scoped>
.landing-page {
  background-color: #010c1f;
  color: #a6d8ff;
  padding: 2rem;
}

.logo {
  width: 250px;
  max-width: 80%;
  filter: drop-shadow(0 0 10px #00bfff);
}

.title {
  font-size: 2.8rem;
  font-weight: bold;
  color: #00bfff;
}

.subtitle {
  font-size: 1.2rem;
  color: #a6d8ff;
  opacity: 0.85;
}

.neon-btn {
  background-color: #00bfff;
  color: #000;
  border: none;
  font-weight: 600;
}

.neon-btn:hover {
  transform: scale(1);
  box-shadow: 0 0 5px #00eaff, 0 0 10px #00eaff;
}

.neon-btn-outline {
  background: transparent;
  color: #00bfff;
  border: 2px solid #00bfff;
  font-weight: 600;
  box-shadow: 0 0 5px #00bfff;
}

.neon-btn-outline:hover {
  background-color: #00bfff;
  color: #000;
}
</style>

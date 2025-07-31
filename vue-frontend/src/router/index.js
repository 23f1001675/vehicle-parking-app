import { createRouter, createWebHistory } from 'vue-router'
import { jwtDecode } from 'jwt-decode'

import Login from '../components/Login.vue'
import Landing from '../components/Landing.vue'
import Register from '../components/Register.vue'
import AdminDash from '../components/AdminDash.vue'
import UserDash from '../components/UserDash.vue'
import NewLot from '../components/NewLot.vue'
import EditLot from '../components/EditLot.vue'
import ViewLot from '../components/ViewLot.vue'
import MyReservations from '../components/MyReservations.vue'
import ViewUsers from '../components/ViewUsers.vue'
import ViewUserReservations from '../components/ViewUserReservations.vue'
import AdminStats from '../components/AdminStats.vue'
import UserStats from '../components/UserStats.vue'

const routes = [
  { path: '/', name: 'Landing', component: Landing },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDash,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/user/:id/dashboard/',
    name: 'UserDashboard',
    component: UserDash,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/admin/create-new-lot',
    name: 'CreateNewLot',
    component: NewLot,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/edit-lot/:id',
    name: 'EditLot',
    component: EditLot,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/view-lot/:id',
    name: 'ViewLot',
    component: ViewLot,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path : '/user/my-reservations',
    name: 'MyReservations',
    component: MyReservations,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path : '/admin/view-all-users',
    name: 'ViewUsers',
    component: ViewUsers,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path : '/admin/view-user-reservations/:userId',
    name: 'ViewUserReservations',
    component: ViewUserReservations,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/statistics',
    name: 'AdminStats',
    component: AdminStats,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path : '/user/my-statistics',
    name: 'UserStats',
    component: UserStats,
    meta: { requiresAuth: true, role: 'user' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth) {
    if (!token) {
      // Give warning
      alert('You must be logged in to access this page.')
      return next('/login')
    }

    try {
      const decoded = jwtDecode(token)
      const currentTime = Math.floor(Date.now() / 1000)

      if (decoded.exp < currentTime) {
        localStorage.removeItem('token')
        return next('/login')
      }

      if (to.meta.role && decoded.role !== to.meta.role) {
        return decoded.role === 'admin'
          ? next('/admin/dashboard')
          : next('/user/dashboard')
      }

      return next()
    } catch (err) {
      localStorage.removeItem('token')
      return next('/login')
    }
  } else {
    return next()
  }
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import RequirementGenerator from '../components/RequirementGenerator.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: RequirementGenerator,
    },
  ],
})

export default router
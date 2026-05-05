import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', component: () => import('@/views/HomeView.vue') },
        { path: '/editor/:id', component: () => import('@/views/EditorView.vue') },
    ],
})

export default router

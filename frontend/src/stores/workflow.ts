import { defineStore } from 'pinia'
import { ref } from 'vue'
import { workflowsApi } from '@/api/modules'
import type { Workflow } from '@/types'

export const useWorkflowStore = defineStore('workflow', () => {
    const workflows = ref<Workflow[]>([])
    const current = ref<Workflow | null>(null)
    const saving = ref(false)

    async function loadAll() {
        const { data } = await workflowsApi.getAll()
        workflows.value = data
    }

    async function load(id: string) {
        const { data } = await workflowsApi.getOne(id)
        current.value = data
        return data
    }

    async function create(name: string, description?: string) {
        const { data } = await workflowsApi.create({ name, description })
        workflows.value.push(data)
        return data
    }

    async function save(id: string, graph: any) {
        saving.value = true
        try {
            const { data } = await workflowsApi.update(id, { graph })
            if (current.value?.id === id) current.value = data
        } finally {
            saving.value = false
        }
    }

    async function toggle(id: string, active: boolean) {
        const { data } = await workflowsApi.update(id, { active })
        const idx = workflows.value.findIndex(w => w.id === id)
        if (idx !== -1) workflows.value[idx] = data
        if (current.value?.id === id) current.value = data
    }

    async function remove(id: string) {
        await workflowsApi.delete(id)
        workflows.value = workflows.value.filter(w => w.id !== id)
    }

    async function execute(id: string) {
        const { data } = await workflowsApi.execute(id)
        return data
    }

    return { workflows, current, saving, loadAll, load, create, save, toggle, remove, execute }
})

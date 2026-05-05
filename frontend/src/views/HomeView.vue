<template>
    <div class="min-h-screen bg-background text-foreground">
        <!-- Header -->
        <div class="border-b border-border px-6 h-14 flex items-center justify-between">
            <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded bg-primary flex items-center justify-center">
                    <i class="ri-node-tree text-white text-xs" />
                </div>
                <span class="text-sm font-bold">MiniNodes</span>
            </div>
            <button
                class="flex items-center gap-1.5 px-3 h-7 rounded-md bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/80"
                @click="createNew"
            >
                <i class="ri-add-line" />
                New Workflow
            </button>
        </div>

        <!-- Content -->
        <div class="max-w-4xl mx-auto p-6 space-y-4">
            <div v-if="loading" class="text-sm text-muted-foreground">Loading…</div>

            <div v-else-if="workflows.length === 0" class="flex flex-col items-center justify-center py-24 gap-4 text-center">
                <div class="w-16 h-16 rounded-full bg-muted flex items-center justify-center">
                    <i class="ri-node-tree text-2xl text-muted-foreground" />
                </div>
                <p class="text-sm font-medium">No workflows yet</p>
                <p class="text-xs text-muted-foreground">Create your first workflow to get started</p>
                <button
                    class="px-4 py-2 rounded-md bg-primary text-primary-foreground text-xs font-medium"
                    @click="createNew"
                >
                    Create Workflow
                </button>
            </div>

            <div v-else class="space-y-2">
                <div
                    v-for="wf in workflows"
                    :key="wf.id"
                    class="flex items-center justify-between p-4 rounded-lg border border-border bg-card hover:bg-muted/30 transition-colors cursor-pointer"
                    @click="router.push(`/editor/${wf.id}`)"
                >
                    <div class="flex items-center gap-3">
                        <div class="w-2 h-2 rounded-full" :class="wf.active ? 'bg-green-500' : 'bg-muted-foreground'" />
                        <div>
                            <p class="text-sm font-medium">{{ wf.name }}</p>
                            <p class="text-xs text-muted-foreground">
                                {{ wf.graph.nodes.length }} nodes · {{ wf.active ? 'Active' : 'Inactive' }}
                                <span v-if="wf.webhook_path"> · Webhook</span>
                            </p>
                        </div>
                    </div>
                    <button
                        class="p-1.5 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive"
                        @click.stop="deleteWorkflow(wf.id)"
                    >
                        <i class="ri-delete-bin-line text-sm" />
                    </button>
                </div>
            </div>
        </div>

        <!-- Create dialog -->
        <div v-if="showCreate" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div class="bg-card rounded-xl border border-border p-6 w-full max-w-sm space-y-4">
                <p class="text-sm font-semibold">New Workflow</p>
                <input
                    v-model="newName"
                    class="w-full h-8 rounded-md border border-input bg-background px-2 text-sm"
                    placeholder="My Workflow"
                    @keydown.enter="confirmCreate"
                    autofocus
                />
                <div class="flex justify-end gap-2">
                    <button class="px-3 h-7 rounded-md border border-border text-xs" @click="showCreate = false">Cancel</button>
                    <button class="px-3 h-7 rounded-md bg-primary text-primary-foreground text-xs" @click="confirmCreate">Create</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWorkflowStore } from '@/stores/workflow'

const router = useRouter()
const store = useWorkflowStore()
const loading = ref(true)
const showCreate = ref(false)
const newName = ref('')

const workflows = computed(() => store.workflows)

onMounted(async () => {
    try { await store.loadAll() } finally { loading.value = false }
})

function createNew() {
    newName.value = ''
    showCreate.value = true
}

async function confirmCreate() {
    if (!newName.value.trim()) return
    const wf = await store.create(newName.value.trim())
    showCreate.value = false
    router.push(`/editor/${wf.id}`)
}

async function deleteWorkflow(id: string) {
    if (confirm('Delete this workflow?')) await store.remove(id)
}
</script>

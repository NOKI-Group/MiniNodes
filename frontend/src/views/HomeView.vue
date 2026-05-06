<template>
    <div class="min-h-screen bg-background text-foreground">
        <div class="max-w-4xl mx-auto p-6 space-y-4">
            <div v-if="loading" class="text-sm text-muted-foreground">Loading…</div>

            <div v-else-if="workflows.length === 0" class="flex items-center justify-center py-24">
                <Empty>
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <RiFlowChart />
                        </EmptyMedia>
                        <EmptyTitle>No Workflows Yet</EmptyTitle>
                        <EmptyDescription>
                            You haven't created any workflows yet. Get started by creating your first workflow.
                        </EmptyDescription>
                    </EmptyHeader>
                    <EmptyContent>
                        <div class="flex gap-2">
                            <Button @click="createNew">Create Workflow</Button>
                        </div>
                    </EmptyContent>
                    <Button variant="link" as-child class="text-muted-foreground" size="sm">
                        <a href="#">
                            Learn More <RiArrowRightUpLine class="size-3.5" />
                        </a>
                    </Button>
                </Empty>
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
                        <RiDeleteBinLine class="size-4" />
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
                    <Button variant="outline" size="sm" @click="showCreate = false">Cancel</Button>
                    <Button size="sm" @click="confirmCreate">Create</Button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RiFlowChart, RiArrowRightUpLine, RiDeleteBinLine } from '@remixicon/vue'
import { Button } from '@/components/ui/button'
import {
    Empty,
    EmptyContent,
    EmptyDescription,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
} from '@/components/ui/empty'
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
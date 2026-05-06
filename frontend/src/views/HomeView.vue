<template>
    <div class="min-h-screen bg-background text-foreground flex flex-col">
        <div class="max-w-4xl w-full mx-auto p-6 space-y-4 flex-1 flex flex-col">

            <div v-if="loading" class="text-sm text-muted-foreground">Loading…</div>

            <!-- Empty state -->
            <div v-else-if="workflows.length === 0" class="flex-1 flex items-center justify-center">
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
                        <Button @click="createNew">Create Workflow</Button>
                    </EmptyContent>
                    <Button variant="link" as-child class="text-muted-foreground" size="sm">
                        <a href="#">
                            Learn More <RiArrowRightUpLine class="size-3.5" />
                        </a>
                    </Button>
                </Empty>
            </div>

            <!-- Workflow list -->
            <div v-else class="space-y-2">
                <!-- Header -->
                <div class="flex items-center justify-between">
                    <h1 class="text-sm font-semibold flex items-center gap-2">
                        Workflows
                        <span class="text-xs font-normal text-muted-foreground bg-muted px-1.5 py-0.5 rounded-md">{{ workflows.length }}</span>
                    </h1>
                    <Button size="sm" @click="createNew">
                        <RiAddLine class="size-3.5" />
                        New Workflow
                    </Button>
                </div>

                <div
                    v-for="wf in workflows"
                    :key="wf.id"
                    class="flex items-center justify-between p-4 rounded-lg border border-border bg-card hover:bg-muted/30 transition-colors cursor-pointer"
                    @click="router.push(`/editor/${wf.id}`)"
                >
                    <div class="flex items-center gap-3">
                        <div class="w-2 h-2 rounded-full shrink-0" :class="wf.active ? 'bg-green-500' : 'bg-muted-foreground'" />
                        <div>
                            <p class="text-sm font-medium">{{ wf.name }}</p>
                            <p class="text-xs text-muted-foreground">
                                {{ wf.graph.nodes.length }} nodes · {{ wf.active ? 'Active' : 'Inactive' }}
                                <span v-if="wf.webhook_path"> · Webhook</span>
                            </p>
                        </div>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        class="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                        @click.stop="openDelete(wf)"
                    >
                        <RiDeleteBinLine class="size-4" />
                    </Button>
                </div>
            </div>
        </div>

        <!-- Delete alert dialog -->
        <AlertDialog v-model:open="showDelete">
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Delete Workflow</AlertDialogTitle>
                    <AlertDialogDescription>
                        Are you sure you want to delete <span class="font-medium text-foreground">{{ pendingDelete?.name }}</span>? This action cannot be undone.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                        class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        @click="confirmDelete"
                    >
                        Delete
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>

        <!-- Create dialog -->
        <Dialog v-model:open="showCreate">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>New Workflow</DialogTitle>
                    <DialogDescription>Give your workflow a name to get started.</DialogDescription>
                </DialogHeader>
                <Input
                    v-model="newName"
                    placeholder="My Workflow"
                    @keydown.enter="confirmCreate"
                    autofocus
                />
                <DialogFooter>
                    <Button variant="outline" @click="showCreate = false">Cancel</Button>
                    <Button @click="confirmCreate">Create</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RiFlowChart, RiArrowRightUpLine, RiDeleteBinLine, RiAddLine } from '@remixicon/vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from '@/components/ui/dialog'
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
    Empty,
    EmptyContent,
    EmptyDescription,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
} from '@/components/ui/empty'
import { useWorkflowStore } from '@/stores/workflow'
import type { Workflow } from '@/types'

const router = useRouter()
const store = useWorkflowStore()
const loading = ref(true)
const showCreate = ref(false)
const showDelete = ref(false)
const newName = ref('')
const pendingDelete = ref<Workflow | null>(null)

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

function openDelete(wf: Workflow) {
    pendingDelete.value = wf
    showDelete.value = true
}

async function confirmDelete() {
    if (!pendingDelete.value) return
    await store.remove(pendingDelete.value.id)
    pendingDelete.value = null
}
</script>
<template>
    <div class="flex flex-col h-screen bg-background text-foreground">

        <!-- Unsaved changes leave dialog -->
        <AlertDialog v-model:open="showLeaveDialog">
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Ungespeicherte Änderungen</AlertDialogTitle>
                    <AlertDialogDescription>
                        Du hast ungespeicherte Änderungen an <span class="font-medium text-foreground">{{ workflow?.name }}</span>. Möchtest du sie speichern, bevor du die Seite verlässt?
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel @click="discardAndLeave">Verwerfen</AlertDialogCancel>
                    <AlertDialogAction @click="saveAndLeave">Speichern & Verlassen</AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>

        <!-- Topbar -->
        <div class="flex items-center justify-between px-4 h-12 border-b border-border shrink-0">
            <div class="flex items-center gap-3">
                <button @click="handleBack" class="text-muted-foreground hover:text-foreground">
                    <RiArrowLeftLine class="size-4" />
                </button>
                <span class="text-sm font-semibold">{{ workflow?.name ?? 'Loading…' }}</span>
                <span v-if="store.saving" class="text-xs text-muted-foreground">Saving…</span>
                <span v-else-if="isDirty" class="text-xs text-muted-foreground">● Unsaved changes</span>
            </div>

            <div class="flex items-center gap-2">
                <div class="flex items-center space-x-2">
                    <Label for="workflow-active">Activate Workflow</Label>
                    <Switch id="workflow-active" v-model="workflowActive" />
                </div>

                <Button v-if="lastExecution" variant="ghost" size="icon" @click="lastExecution = null" title="Clear results">
                    <RiCloseLine class="size-3.5" />
                </Button>

                <Button @click="saveGraph" variant="outline" :disabled="store.saving">
                    <RiSaveLine class="size-3.5" />
                    Save
                </Button>

                <Button @click="runManual" :disabled="running">
                    <RiPlayLine class="size-3.5" />
                    {{ running ? 'Running…' : 'Run' }}
                </Button>
            </div>
        </div>

        <!-- Webhook URL bar -->
        <div v-if="workflow?.webhook_path" class="flex items-center gap-2 px-4 py-1.5 bg-muted/50 border-b border-border text-xs">
            <RiWebhookLine class="size-3.5 text-muted-foreground" />
            <span class="text-muted-foreground">Webhook:</span>
            <code class="font-mono text-foreground">{{ webhookUrl }}</code>
            <button @click="copyWebhook" class="text-muted-foreground hover:text-foreground ml-1">
                <RiClipboardLine class="size-3.5" />
            </button>
        </div>

        <!-- Main area -->
        <div class="flex flex-1 overflow-hidden">
            <NodePalette />

            <!-- Canvas -->
            <div class="flex-1 relative" ref="canvasWrapper" @dragover.prevent @drop="onDrop">
                <VueFlow
                    v-model:nodes="nodes"
                    v-model:edges="edges"
                    :node-types="nodeTypes"
                    :default-edge-options="{ type: 'smoothstep' }"
                    fit-view-on-init
                    class="w-full h-full"
                    @node-click="onNodeClick"
                    @pane-click="onPaneClick"
                    @connect="onConnect"
                    @nodes-change="markDirty"
                    @edges-change="markDirty"
                >
                    <Background class="bg-neutral-100" />
                    <Controls />
                    <MiniMap />
                </VueFlow>

                <!-- Execution status bar -->
                <div v-if="lastExecution" class="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3 px-4 py-2 rounded-full border border-border bg-card shadow-lg text-xs">
                    <span class="flex items-center gap-1.5">
                        <span class="size-2 rounded-full"
                              :class="lastExecution.status === 'success' ? 'bg-green-500' : 'bg-red-500'" />
                        {{ lastExecution.status === 'success' ? 'Execution successful' : 'Execution failed' }}
                    </span>
                    <span class="text-muted-foreground">·</span>
                    <span class="text-muted-foreground">{{ executionDuration }}</span>
                    <span class="text-muted-foreground">·</span>
                    <span class="text-muted-foreground">{{ Object.keys(lastExecution.node_results).length }} nodes</span>
                </div>
            </div>

            <!-- Right panel: execution result OR node config -->
            <template v-if="selectedNode">
                <div v-if="lastExecution && lastExecution.node_results[selectedNode.id]"
                     class="w-80 bg-card border-l border-border flex flex-col h-full overflow-hidden">
                    <div class="p-4 border-b border-border flex items-center justify-between shrink-0">
                        <div>
                            <p class="text-sm font-semibold">{{ selectedNode.data?.label }}</p>
                            <p class="text-xs text-muted-foreground mt-0.5">Execution Result</p>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs px-1.5 py-0.5 rounded font-medium"
                                  :class="lastExecution.node_results[selectedNode.id].error
                                    ? 'bg-red-500/10 text-red-400'
                                    : 'bg-green-500/10 text-green-400'">
                                {{ lastExecution.node_results[selectedNode.id].error ? 'Error' : 'Success' }}
                            </span>
                            <button @click="selectedNode = null" class="text-muted-foreground hover:text-foreground">
                                <RiCloseLine class="size-4" />
                            </button>
                        </div>
                    </div>

                    <div class="flex-1 overflow-y-auto">
                        <div v-if="lastExecution.node_results[selectedNode.id].error" class="p-4">
                            <p class="text-xs font-medium text-red-400 mb-2">Error</p>
                            <pre class="text-xs bg-red-500/10 text-red-400 p-3 rounded-md overflow-x-auto whitespace-pre-wrap">{{ lastExecution.node_results[selectedNode.id].error }}</pre>
                        </div>
                        <div v-else class="p-4">
                            <p class="text-xs font-medium text-muted-foreground mb-2">Output</p>
                            <pre class="text-xs bg-muted p-3 rounded-md overflow-x-auto whitespace-pre-wrap font-mono">{{ JSON.stringify(nodeDisplayOutput(lastExecution.node_results[selectedNode.id].output), null, 2) }}</pre>
                        </div>
                    </div>

                    <div class="p-3 border-t border-border shrink-0">
                        <button @click="openConfigDialog(selectedNode)"
                                class="w-full flex items-center justify-between text-xs text-muted-foreground hover:text-foreground">
                            <span>Edit Node Config</span>
                            <RiArrowDownSLine class="size-3.5" />
                        </button>
                    </div>
                </div>
            </template>
        </div>

        <!-- Node Config Dialog -->
        <NodeConfigDialog
            v-if="configDialogNode"
            v-model:open="configDialogOpen"
            :node-id="configDialogNode.id"
            :node-type="configDialogNode.type"
            :config="configDialogNode.data?.config ?? {}"
            @update="onConfigUpdate"
        />

        <!-- Delete node confirmation -->
        <AlertDialog v-model:open="showDeleteNode">
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Delete Node</AlertDialogTitle>
                    <AlertDialogDescription>
                        Are you sure you want to delete <span class="font-medium text-foreground">{{ pendingDeleteNode?.data?.label }}</span>? All connected edges will also be removed.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                        class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        @click="confirmDeleteNode"
                    >
                        Delete
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, shallowRef } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { VueFlow, useVueFlow, type Connection, addEdge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import {
    RiArrowLeftLine,
    RiPlayLine,
    RiSaveLine,
    RiWebhookLine,
    RiClipboardLine,
    RiCloseLine,
    RiArrowDownSLine,
} from '@remixicon/vue'
import { useWorkflowStore } from '@/stores/workflow'
import { useNodesStore } from '@/stores/nodes'
import MiniNode from '@/components/canvas/MiniNode.vue'
import NodePalette from '@/components/canvas/NodePalette.vue'
import NodeConfigDialog from '@/components/canvas/NodeConfigDialog.vue'
import type { Execution } from '@/types'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
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

const route = useRoute()
const router = useRouter()
const store = useWorkflowStore()
const nodesStore = useNodesStore()

const workflow = computed(() => store.current)
const nodes = ref<any[]>([])
const edges = ref<any[]>([])
const selectedNode = ref<any>(null)
const running = ref(false)
const lastExecution = ref<Execution | null>(null)
const canvasWrapper = ref<HTMLElement | null>(null)
const nodeTypes = shallowRef<Record<string, any>>({})

// Config dialog state
const configDialogOpen = ref(false)
const configDialogNode = ref<any>(null)

// Delete node state
const showDeleteNode = ref(false)
const pendingDeleteNode = ref<any>(null)

// Leave guard state
const isDirty = ref(false)
const showLeaveDialog = ref(false)
let pendingLeaveResolve: ((value: boolean) => void) | null = null

const webhookUrl = computed(() => {
    if (!workflow.value?.webhook_path) return ''

    const webhookNode = nodes.value.find(n => n.type === 'core.webhook_trigger')
    const customPath = webhookNode?.data?.config?.custom_path?.trim().replace(/^\/+/, '')

    const path = customPath
        ? `/webhook/${customPath}`
        : workflow.value.webhook_path

    return `http://${window.location.hostname}:8001${path}`
})

const workflowActive = computed({
    get: () => workflow.value?.active ?? false,
    set: (value: boolean) => toggleActive(value),
})

const executionDuration = computed(() => {
    if (!lastExecution.value?.started_at || !lastExecution.value?.finished_at) return ''
    const ms = new Date(lastExecution.value.finished_at).getTime() - new Date(lastExecution.value.started_at).getTime()
    return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(2)}s`
})

const { project } = useVueFlow()

onMounted(async () => {
    await nodesStore.load()
    const wf = await store.load(route.params.id as string)
    nodes.value = (wf.graph?.nodes ?? []).map((n: any) => ({
        ...n,
        data: {
            ...n.data,
            onEdit: (id: string) => openConfigDialog(nodes.value.find(x => x.id === id)),
            onDelete: (id: string) => requestDeleteNode(nodes.value.find(x => x.id === id)),
        }
    }))
    edges.value = wf.graph?.edges ?? []

    const types: Record<string, any> = {}
    nodesStore.definitions.forEach(d => { types[d.type] = MiniNode })
    nodeTypes.value = types
})

// Intercept any Vue Router navigation away from this page
onBeforeRouteLeave(() => {
    if (!isDirty.value) return true

    return new Promise<boolean>((resolve) => {
        pendingLeaveResolve = resolve
        showLeaveDialog.value = true
    })
})

function markDirty() {
    isDirty.value = true
}

// Back button — router.push triggers onBeforeRouteLeave automatically
function handleBack() {
    router.push('/')
}

async function saveAndLeave() {
    showLeaveDialog.value = false
    await saveGraph()
    if (pendingLeaveResolve) {
        pendingLeaveResolve(true)
        pendingLeaveResolve = null
    }
}

function discardAndLeave() {
    showLeaveDialog.value = false
    isDirty.value = false
    if (pendingLeaveResolve) {
        pendingLeaveResolve(true)
        pendingLeaveResolve = null
    }
}

function nodeDisplayOutput(output: any) {
    if (output && typeof output === 'object' && output._output === true) {
        return output.data
    }
    return output
}

function onConnect(connection: Connection) {
    edges.value = addEdge({ ...connection, type: 'smoothstep' }, edges.value)
    markDirty()
}

function onNodeClick({ node }: { event: MouseEvent; node: any }) {
    selectedNode.value = node
}

function onPaneClick() {
    selectedNode.value = null
}

function openConfigDialog(node: any) {
    if (!node) return
    configDialogNode.value = node
    configDialogOpen.value = true
}

function requestDeleteNode(node: any) {
    if (!node) return
    pendingDeleteNode.value = node
    showDeleteNode.value = true
}

function confirmDeleteNode() {
    if (!pendingDeleteNode.value) return
    const id = pendingDeleteNode.value.id
    nodes.value = nodes.value.filter(n => n.id !== id)
    edges.value = edges.value.filter(e => e.source !== id && e.target !== id)
    if (selectedNode.value?.id === id) selectedNode.value = null
    if (configDialogNode.value?.id === id) {
        configDialogOpen.value = false
        configDialogNode.value = null
    }
    pendingDeleteNode.value = null
    markDirty()
}

function onConfigUpdate(config: Record<string, any>) {
    if (!configDialogNode.value) return
    const id = configDialogNode.value.id
    const idx = nodes.value.findIndex(n => n.id === id)
    if (idx !== -1) {
        nodes.value[idx] = { ...nodes.value[idx], data: { ...nodes.value[idx].data, config } }
        configDialogNode.value = nodes.value[idx]
        if (selectedNode.value?.id === id) selectedNode.value = nodes.value[idx]
        markDirty()
    }
}

function onDrop(event: DragEvent) {
    const type = event.dataTransfer?.getData('application/mininodes-type')
    const label = event.dataTransfer?.getData('application/mininodes-label')
    if (!type || !canvasWrapper.value) return

    const bounds = canvasWrapper.value.getBoundingClientRect()
    const position = project({ x: event.clientX - bounds.left, y: event.clientY - bounds.top })

    const def = nodesStore.getDefinition(type)
    const config: Record<string, any> = {}
    def?.fields?.forEach(f => { if (f.default !== undefined) config[f.key] = f.default })

    const newNode = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: {
            label: label ?? type,
            config,
            onEdit: (id: string) => openConfigDialog(nodes.value.find(x => x.id === id)),
            onDelete: (id: string) => requestDeleteNode(nodes.value.find(x => x.id === id)),
        },
    }
    nodes.value.push(newNode)
    markDirty()
}

async function saveGraph() {
    if (!workflow.value) return
    const cleanNodes = nodes.value.map(n => {
        const { onEdit, onDelete, ...rest } = n.data ?? {}
        return { ...n, data: rest }
    })
    await store.save(workflow.value.id, { nodes: cleanNodes, edges: edges.value })
    isDirty.value = false
}

async function toggleActive(value: boolean) {
    if (!workflow.value) return
    await store.toggle(workflow.value.id, value)
}

async function runManual() {
    if (!workflow.value || running.value) return
    running.value = true
    lastExecution.value = null
    try {
        await saveGraph()
        const execution = await store.execute(workflow.value.id)
        lastExecution.value = execution

        if (execution.node_results) {
            const resultIds = Object.keys(execution.node_results)
            const outputNode = nodes.value.find(n =>
                resultIds.includes(n.id) && n.type === 'core.output'
            )
            const lastNode = nodes.value.find(n => n.id === resultIds[resultIds.length - 1])
            const firstNode = nodes.value.find(n => n.id === resultIds[0])
            selectedNode.value = outputNode ?? lastNode ?? firstNode ?? null
        }
    } finally {
        running.value = false
    }
}

async function copyWebhook() {
    await navigator.clipboard.writeText(webhookUrl.value)
}
</script>
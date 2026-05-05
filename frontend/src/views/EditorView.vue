<template>
    <div class="flex flex-col h-screen bg-background text-foreground">

        <!-- Topbar -->
        <div class="flex items-center justify-between px-4 h-12 border-b border-border shrink-0">
            <div class="flex items-center gap-3">
                <router-link to="/" class="text-muted-foreground hover:text-foreground">
                    <i class="ri-arrow-left-line" />
                </router-link>
                <span class="text-sm font-semibold">{{ workflow?.name ?? 'Loading…' }}</span>
                <span v-if="store.saving" class="text-xs text-muted-foreground">Saving…</span>
            </div>

            <div class="flex items-center gap-2">
                <label class="flex items-center gap-2 cursor-pointer">
                    <span class="text-xs text-muted-foreground">Active</span>
                    <div
                        class="w-8 h-4 rounded-full transition-colors relative cursor-pointer"
                        :class="workflow?.active ? 'bg-primary' : 'bg-muted'"
                        @click="toggleActive"
                    >
                        <div class="absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform"
                            :class="workflow?.active ? 'translate-x-4' : 'translate-x-0.5'" />
                    </div>
                </label>

                <button
                    class="flex items-center gap-1.5 px-3 h-7 rounded-md bg-muted hover:bg-muted/80 text-xs font-medium"
                    @click="runManual"
                    :disabled="running"
                >
                    <i class="ri-play-line" />
                    {{ running ? 'Running…' : 'Run' }}
                </button>

                <button
                    class="flex items-center gap-1.5 px-3 h-7 rounded-md bg-primary text-primary-foreground hover:bg-primary/80 text-xs font-medium"
                    @click="saveGraph"
                >
                    <i class="ri-save-line" />
                    Save
                </button>
            </div>
        </div>

        <!-- Webhook URL bar -->
        <div v-if="workflow?.webhook_path" class="flex items-center gap-2 px-4 py-1.5 bg-muted/50 border-b border-border text-xs">
            <i class="ri-webhook-line text-muted-foreground" />
            <span class="text-muted-foreground">Webhook:</span>
            <code class="font-mono text-foreground">{{ webhookUrl }}</code>
            <button @click="copyWebhook" class="text-muted-foreground hover:text-foreground ml-1">
                <i class="ri-clipboard-line" />
            </button>
        </div>

        <!-- Main area -->
        <div class="flex flex-1 overflow-hidden">
            <NodePalette />

            <!-- Canvas -->
            <div class="flex-1 relative" ref="canvasWrapper"
                @dragover.prevent
                @drop="onDrop"
            >
                <VueFlow
                    v-model:nodes="nodes"
                    v-model:edges="edges"
                    :node-types="nodeTypes"
                    :default-edge-options="{ type: 'smoothstep' }"
                    fit-view-on-init
                    class="w-full h-full"
                    @node-click="onNodeClick"
                    @pane-click="selectedNode = null"
                    @connect="onConnect"
                >
                    <Background />
                    <Controls />
                    <MiniMap />
                </VueFlow>
            </div>

            <!-- Node config sidebar -->
            <NodeSidebar
                v-if="selectedNode"
                :node-id="selectedNode.id"
                :node-type="selectedNode.type"
                :config="selectedNode.data?.config ?? {}"
                @close="selectedNode = null"
                @update="onConfigUpdate"
            />

            <!-- Execution result panel -->
            <div v-if="lastExecution" class="w-64 bg-card border-l border-border flex flex-col overflow-hidden">
                <div class="p-3 border-b border-border flex items-center justify-between">
                    <p class="text-xs font-semibold">Last Run</p>
                    <span class="text-xs px-1.5 py-0.5 rounded"
                        :class="lastExecution.status === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'">
                        {{ lastExecution.status }}
                    </span>
                </div>
                <div class="flex-1 overflow-y-auto p-3 space-y-2">
                    <div v-for="(result, nodeId) in lastExecution.node_results" :key="nodeId" class="space-y-1">
                        <p class="text-[10px] text-muted-foreground font-mono">{{ nodeId }}</p>
                        <pre v-if="result.output" class="text-[10px] bg-muted p-1.5 rounded overflow-x-auto">{{ JSON.stringify(result.output, null, 2) }}</pre>
                        <p v-if="result.error" class="text-[10px] text-red-400">{{ result.error }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, shallowRef } from 'vue'
import { useRoute } from 'vue-router'
import { VueFlow, useVueFlow, type Connection, addEdge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import { useWorkflowStore } from '@/stores/workflow'
import { useNodesStore } from '@/stores/nodes'
import { executionsApi } from '@/api/modules'
import MiniNode from '@/components/canvas/MiniNode.vue'
import NodePalette from '@/components/canvas/NodePalette.vue'
import NodeSidebar from '@/components/canvas/NodeSidebar.vue'
import type { Execution } from '@/types'

const route = useRoute()
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

const webhookUrl = computed(() =>
    workflow.value?.webhook_path
        ? `http://${window.location.hostname}:8001${workflow.value.webhook_path}`
        : ''
)

const { project } = useVueFlow()

onMounted(async () => {
    await nodesStore.load()
    const wf = await store.load(route.params.id as string)

    nodes.value = wf.graph?.nodes ?? []
    edges.value = wf.graph?.edges ?? []

    const types: Record<string, any> = {}
    nodesStore.definitions.forEach(d => { types[d.type] = MiniNode })
    nodeTypes.value = types
})

function onConnect(connection: Connection) {
    edges.value = addEdge({ ...connection, type: 'smoothstep' }, edges.value)
}

function onNodeClick(_: any, node: any) {
    selectedNode.value = node
}

function onConfigUpdate(config: Record<string, any>) {
    if (!selectedNode.value) return
    const idx = nodes.value.findIndex(n => n.id === selectedNode.value.id)
    if (idx !== -1) {
        nodes.value[idx] = {
            ...nodes.value[idx],
            data: { ...nodes.value[idx].data, config },
        }
    }
}

function onDrop(event: DragEvent) {
    const type = event.dataTransfer?.getData('application/mininodes-type')
    const label = event.dataTransfer?.getData('application/mininodes-label')
    if (!type || !canvasWrapper.value) return

    const bounds = canvasWrapper.value.getBoundingClientRect()
    const position = project({
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
    })

    const def = nodesStore.getDefinition(type)
    const config: Record<string, any> = {}
    def?.fields?.forEach(f => {
        if (f.default !== undefined) config[f.key] = f.default
    })

    nodes.value.push({
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: { label: label ?? type, config },
    })
}

async function saveGraph() {
    if (!workflow.value) return
    await store.save(workflow.value.id, { nodes: nodes.value, edges: edges.value })
}

async function toggleActive() {
    if (!workflow.value) return
    await store.toggle(workflow.value.id, !workflow.value.active)
}

async function runManual() {
    if (!workflow.value || running.value) return
    running.value = true
    try {
        await saveGraph()
        const result = await store.execute(workflow.value.id)
        const execution_id = result.execution_id
        for (let i = 0; i < 20; i++) {
            await new Promise(r => setTimeout(r, 500))
            const { data } = await executionsApi.getOne(execution_id)
            if (data.status !== 'running') {
                lastExecution.value = data
                break
            }
        }
    } finally {
        running.value = false
    }
}

async function copyWebhook() {
    await navigator.clipboard.writeText(webhookUrl.value)
}
</script>
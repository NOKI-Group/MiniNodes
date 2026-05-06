<template>
    <div class="flex flex-col h-screen bg-background text-foreground">

        <!-- Topbar -->
        <div class="flex items-center justify-between px-4 h-12 border-b border-border shrink-0">
            <div class="flex items-center gap-3">
                <router-link to="/" class="text-muted-foreground hover:text-foreground">
                    <RiArrowLeftLine class="size-4" />
                </router-link>
                <span class="text-sm font-semibold">{{ workflow?.name ?? 'Loading…' }}</span>
                <span v-if="store.saving" class="text-xs text-muted-foreground">Saving…</span>
            </div>

            <div class="flex items-center gap-2">
                <div class="flex items-center space-x-2">
                    <Label for="workflow-active">Activate Workflow</Label>
                    <Switch id="workflow-active" v-model="workflowActive" />
                </div>

                <Button v-if="lastExecution" variant="ghost" size="icon" @click="lastExecution = null" title="Clear results">
                    <RiCloseLine class="size-3.5" />
                </Button>

                <Button @click="saveGraph" variant="outline">
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
                >
                    <Background />
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
                        <button @click="showConfig = !showConfig"
                            class="w-full flex items-center justify-between text-xs text-muted-foreground hover:text-foreground">
                            <span>{{ showConfig ? 'Hide' : 'Show' }} Node Config</span>
                            <RiArrowDownSLine class="size-3.5 transition-transform" :class="showConfig ? 'rotate-180' : ''" />
                        </button>
                        <div v-if="showConfig" class="mt-3">
                            <NodeConfigFields
                                :definition="nodesStore.getDefinition(selectedNode.type)"
                                :config="selectedNode.data?.config ?? {}"
                                @update="onConfigUpdate"
                            />
                        </div>
                    </div>
                </div>

                <NodeSidebar
                    v-else
                    :node-id="selectedNode.id"
                    :node-type="selectedNode.type"
                    :config="selectedNode.data?.config ?? {}"
                    @close="selectedNode = null"
                    @update="onConfigUpdate"
                />
            </template>
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
import NodeSidebar from '@/components/canvas/NodeSidebar.vue'
import NodeConfigFields from '@/components/canvas/NodeConfigFields.vue'
import type { Execution } from '@/types'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'

const route = useRoute()
const store = useWorkflowStore()
const nodesStore = useNodesStore()

const workflow = computed(() => store.current)
const nodes = ref<any[]>([])
const edges = ref<any[]>([])
const selectedNode = ref<any>(null)
const showConfig = ref(false)
const running = ref(false)
const lastExecution = ref<Execution | null>(null)
const canvasWrapper = ref<HTMLElement | null>(null)
const nodeTypes = shallowRef<Record<string, any>>({})

const webhookUrl = computed(() =>
    workflow.value?.webhook_path
        ? `http://${window.location.hostname}:8001${workflow.value.webhook_path}`
        : ''
)

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
    nodes.value = wf.graph?.nodes ?? []
    edges.value = wf.graph?.edges ?? []

    const types: Record<string, any> = {}
    nodesStore.definitions.forEach(d => { types[d.type] = MiniNode })
    nodeTypes.value = types
})


function nodeDisplayOutput(output: any) {
    if (output && typeof output === 'object' && output._output === true) {
        return output.data
    }
    return output
}
function onConnect(connection: Connection) {
    edges.value = addEdge({ ...connection, type: 'smoothstep' }, edges.value)
}

function onNodeClick({ node }: { event: MouseEvent; node: any }) {
    showConfig.value = false
    selectedNode.value = node
}

function onPaneClick() {
    selectedNode.value = null
}

function onConfigUpdate(config: Record<string, any>) {
    if (!selectedNode.value) return
    const idx = nodes.value.findIndex(n => n.id === selectedNode.value.id)
    if (idx !== -1) {
        nodes.value[idx] = { ...nodes.value[idx], data: { ...nodes.value[idx].data, config } }
        selectedNode.value = nodes.value[idx]
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
        // execute() now returns the full Execution object directly
        const execution = await store.execute(workflow.value.id)
        lastExecution.value = execution

        // Auto-select output node first, then last node, then first node
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
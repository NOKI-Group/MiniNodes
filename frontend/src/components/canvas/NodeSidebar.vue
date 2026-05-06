<template>
    <div class="w-72 bg-card border-l border-border flex flex-col h-full overflow-hidden">
        <div class="p-4 border-b border-border flex items-center justify-between">
            <div>
                <p class="text-sm font-semibold">{{ definition?.label }}</p>
                <p class="text-xs text-muted-foreground mt-0.5">{{ definition?.description }}</p>
            </div>
            <button @click="$emit('close')" class="text-muted-foreground hover:text-foreground">
                <RiCloseLine class="size-5" />
            </button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <div v-if="!definition?.fields?.length" class="text-xs text-muted-foreground">
                This node has no configuration.
            </div>

            <div v-for="field in definition?.fields ?? []" :key="field.key" class="space-y-1">
                <label class="text-xs font-medium text-foreground">{{ field.label }}</label>

                <!-- Select -->
                <select
                    v-if="field.type === 'select'"
                    v-model="localConfig[field.key]"
                    class="w-full h-7 rounded-md border border-input bg-background px-2 text-xs"
                    @change="emit('update', localConfig)"
                >
                    <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                </select>

                <!-- JSON textarea -->
                <textarea
                    v-else-if="field.type === 'json'"
                    v-model="localConfig[field.key]"
                    rows="4"
                    class="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs font-mono resize-y"
                    :placeholder="field.placeholder"
                    @input="emit('update', localConfig)"
                />

                <!-- Text / number -->
                <input
                    v-else
                    v-model="localConfig[field.key]"
                    :type="field.type === 'number' ? 'number' : 'text'"
                    class="w-full h-7 rounded-md border border-input bg-background px-2 text-xs"
                    :placeholder="field.placeholder"
                    @input="emit('update', localConfig)"
                />
            </div>
        </div>

        <!-- Ports info -->
        <div class="p-4 border-t border-border space-y-2">
            <div v-if="definition?.inputs?.length" class="flex flex-wrap gap-1">
                <span class="text-xs text-muted-foreground">Inputs:</span>
                <span v-for="i in definition.inputs" :key="i.id"
                    class="text-xs bg-muted px-1.5 py-0.5 rounded">{{ i.label }}</span>
            </div>
            <div v-if="definition?.outputs?.length" class="flex flex-wrap gap-1">
                <span class="text-xs text-muted-foreground">Outputs:</span>
                <span v-for="o in definition.outputs" :key="o.id"
                    class="text-xs bg-muted px-1.5 py-0.5 rounded">{{ o.label }}</span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { reactive, watch, computed } from 'vue'
import { RiCloseLine } from '@remixicon/vue'
import { useNodesStore } from '@/stores/nodes'

const props = defineProps<{
    nodeId: string
    nodeType: string
    config: Record<string, any>
}>()

const emit = defineEmits<{ close: []; update: [config: Record<string, any>] }>()

const nodesStore = useNodesStore()
const definition = computed(() => nodesStore.getDefinition(props.nodeType))

const localConfig = reactive<Record<string, any>>({})

watch(() => props.config, (val) => {
    Object.assign(localConfig, val)
}, { immediate: true })
</script>
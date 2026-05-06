<template>
    <Dialog :open="open" @update:open="$emit('update:open', $event)">
        <DialogContent class="sm:max-w-sm">
            <DialogHeader>
                <div class="flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-md flex items-center justify-center shrink-0" :style="{ backgroundColor: definition?.color ?? '#6366f1' }">
                        <component :is="resolvedIcon" class="text-white size-4" />
                    </div>
                    <div>
                        <DialogTitle>{{ definition?.label }}</DialogTitle>
                        <DialogDescription>{{ definition?.description }}</DialogDescription>
                    </div>
                </div>
            </DialogHeader>

            <!-- Fields -->
            <div class="space-y-3 py-1">
                <div v-if="!definition?.fields?.length" class="text-xs text-muted-foreground py-2">
                    This node has no configuration options.
                </div>

                <div v-for="field in definition?.fields ?? []" :key="field.key" class="space-y-1.5">
                    <label class="text-xs font-medium text-foreground">{{ field.label }}</label>

                    <select
                        v-if="field.type === 'select'"
                        v-model="localConfig[field.key]"
                        class="w-full h-7 rounded-md border border-input bg-background px-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                        <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                    </select>

                    <textarea
                        v-else-if="field.type === 'json'"
                        v-model="localConfig[field.key]"
                        rows="5"
                        class="w-full rounded-md border border-input bg-background px-2.5 py-1.5 text-xs font-mono resize-y focus:outline-none focus:ring-1 focus:ring-ring"
                        :placeholder="field.placeholder"
                    />

                    <input
                        v-else
                        v-model="localConfig[field.key]"
                        :type="field.type === 'number' ? 'number' : 'text'"
                        class="w-full h-7 rounded-md border border-input bg-background px-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
                        :placeholder="field.placeholder"
                    />
                </div>
            </div>

            <!-- Port info -->
            <div v-if="(definition?.inputs?.length || definition?.outputs?.length)" class="flex flex-wrap gap-x-4 gap-y-1.5 pt-1 border-t border-border">
                <div v-if="definition?.inputs?.length" class="flex items-center flex-wrap gap-1">
                    <span class="text-xs text-muted-foreground">In:</span>
                    <span v-for="i in definition.inputs" :key="i.id"
                          class="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">{{ i.label }}</span>
                </div>
                <div v-if="definition?.outputs?.length" class="flex items-center flex-wrap gap-1">
                    <span class="text-xs text-muted-foreground">Out:</span>
                    <span v-for="o in definition.outputs" :key="o.id"
                          class="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">{{ o.label }}</span>
                </div>
            </div>

            <DialogFooter>
                <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
                <Button @click="save">Apply</Button>
            </DialogFooter>
        </DialogContent>
    </Dialog>
</template>

<script setup lang="ts">
import { reactive, watch, computed } from 'vue'
import * as RemixIcons from '@remixicon/vue'
import { useNodesStore } from '@/stores/nodes'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

const props = defineProps<{
    open: boolean
    nodeId: string
    nodeType: string
    config: Record<string, any>
}>()

const emit = defineEmits<{
    'update:open': [value: boolean]
    'update': [config: Record<string, any>]
}>()

const nodesStore = useNodesStore()
const definition = computed(() => nodesStore.getDefinition(props.nodeType))

const resolvedIcon = computed(() => {
    const name = (definition.value?.icon ?? 'ri-node-tree')
        .split('-').map((s: string) => s.charAt(0).toUpperCase() + s.slice(1)).join('')
    return (RemixIcons as Record<string, unknown>)[name] ?? RemixIcons.RiNodeTree
})

const localConfig = reactive<Record<string, any>>({})

watch(() => props.config, (val) => {
    Object.assign(localConfig, val)
}, { immediate: true })

watch(() => props.open, (val) => {
    if (val) Object.assign(localConfig, props.config)
})

function save() {
    emit('update', { ...localConfig })
    emit('update:open', false)
}
</script>
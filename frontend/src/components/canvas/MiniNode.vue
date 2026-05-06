<template>
    <div
        class="min-w-[180px] rounded-lg border-2 shadow-lg overflow-hidden transition-all"
        :class="selected ? 'border-white/50' : 'border-transparent'"
        :style="{ backgroundColor: definition?.color ?? '#6366f1' }"
    >
        <div class="px-3 py-2 flex items-center gap-2">
            <component
                :is="resolvedIcon"
                class="text-white/80 size-4 shrink-0"
            />
            <span class="text-white text-xs font-semibold truncate">{{ data.label }}</span>
        </div>

        <Handle
            v-for="input in definition?.inputs ?? []"
            :key="input.id"
            :id="input.id"
            type="target"
            :position="Position.Left"
            style="width: 12px; height: 12px; background: rgba(255,255,255,0.6); border: 2px solid rgba(255,255,255,0.2);"
        />

        <Handle
            v-for="output in definition?.outputs ?? []"
            :key="output.id"
            :id="output.id"
            type="source"
            :position="Position.Right"
            style="width: 12px; height: 12px; background: rgba(255,255,255,0.6); border: 2px solid rgba(255,255,255,0.2);"
        />
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import * as RemixIcons from '@remixicon/vue'
import { useNodesStore } from '@/stores/nodes'

const props = defineProps<{
    id: string
    data: { label: string; config: Record<string, any> }
    selected: boolean
    type: string
}>()

const nodesStore = useNodesStore()
const definition = computed(() => nodesStore.getDefinition(props.type))

// ri-node-tree → RiNodeTree
function toComponentName(icon: string): string {
    return icon
        .split('-')
        .map(s => s.charAt(0).toUpperCase() + s.slice(1))
        .join('')
}

const resolvedIcon = computed(() => {
    const name = toComponentName(definition.value?.icon ?? 'ri-node-tree')
    return (RemixIcons as Record<string, unknown>)[name] ?? RemixIcons.RiNodeTree
})
</script>
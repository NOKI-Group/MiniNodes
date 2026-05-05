<template>
    <div
        class="min-w-[180px] rounded-lg border-2 shadow-lg overflow-hidden transition-all"
        :class="selected ? 'border-white/50' : 'border-transparent'"
        :style="{ backgroundColor: definition?.color ?? '#6366f1' }"
    >
        <div class="px-3 py-2 flex items-center gap-2">
            <i :class="[definition?.icon ?? 'ri-node-tree', 'text-white/80 text-sm']" />
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
import { useNodesStore } from '@/stores/nodes'

const props = defineProps<{
    id: string
    data: { label: string; config: Record<string, any> }
    selected: boolean
    type: string
}>()

const nodesStore = useNodesStore()
const definition = computed(() => nodesStore.getDefinition(props.type))
</script>

<template>
    <div class="w-56 bg-card border-r border-border flex flex-col h-full">
        <div class="p-3 border-b border-border">
            <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Nodes</p>
        </div>
        <div class="flex-1 overflow-y-auto p-2 space-y-1">
            <div
                v-for="def in definitions"
                :key="def.type"
                class="flex items-center gap-2 px-2 py-2 rounded-md cursor-grab hover:bg-muted transition-colors"
                draggable="true"
                @dragstart="onDragStart($event, def)"
            >
                <div class="w-6 h-6 rounded flex items-center justify-center shrink-0" :style="{ backgroundColor: def.color }">
                    <component :is="resolveIcon(def.icon)" class="text-white size-3.5 shrink-0" />
                </div>
                <div class="min-w-0">
                    <p class="text-xs font-medium truncate">{{ def.label }}</p>
                    <p class="text-[10px] text-muted-foreground truncate">{{ def.description }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import * as RemixIcons from '@remixicon/vue'
import { useNodesStore } from '@/stores/nodes'
import type { NodeDefinition } from '@/types'

const nodesStore = useNodesStore()
const definitions = computed(() => nodesStore.definitions)

function resolveIcon(icon: string) {
    const name = icon
        .split('-')
        .map(s => s.charAt(0).toUpperCase() + s.slice(1))
        .join('')
    return (RemixIcons as Record<string, unknown>)[name] ?? RemixIcons.RiNodeTree
}

function onDragStart(event: DragEvent, def: NodeDefinition) {
    event.dataTransfer?.setData('application/mininodes-type', def.type)
    event.dataTransfer?.setData('application/mininodes-label', def.label)
    if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move'
}
</script>
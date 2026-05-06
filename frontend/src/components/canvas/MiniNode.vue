<template>
    <div
        class="relative flex flex-col items-center"
        @mouseenter="hovered = true"
        @mouseleave="hovered = false"
    >
        <!-- Hover popup menu -->
        <Transition
            enter-active-class="transition-all duration-150 ease-out"
            enter-from-class="opacity-0 scale-95 -translate-y-1"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition-all duration-100 ease-in"
            leave-from-class="opacity-100 scale-100 translate-y-0"
            leave-to-class="opacity-0 scale-95 -translate-y-1"
        >
            <div
                v-if="hovered"
                class="absolute -top-10 left-1/2 -translate-x-1/2 z-50 flex items-center gap-0.5 bg-card border border-border rounded-lg px-1 py-1 pointer-events-auto nodrag nopan"
                @mouseenter="hovered = true"
                @mouseleave="hovered = false"
            >
                <!-- Edit / config -->
                <button
                    class="flex items-center justify-center w-6 h-6 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                    title="Configure"
                    @click.stop="handleEdit"
                    @mousedown.stop
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                    </svg>
                </button>

                <div class="w-px h-4 bg-border mx-0.5" />

                <!-- Delete -->
                <button
                    class="flex items-center justify-center w-6 h-6 rounded-md hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
                    title="Delete node"
                    @click.stop="handleDelete"
                    @mousedown.stop
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
                    </svg>
                </button>
            </div>
        </Transition>

        <div class="flex items-center">
            <!-- Left handles -->
            <div class="flex flex-col self-stretch justify-around -mr-1.5 z-10">
                <Handle
                    v-for="input in definition?.inputs ?? []"
                    :key="input.id"
                    :id="input.id"
                    type="target"
                    :position="Position.Left"
                    class="!static !transform-none !relative !inset-auto !bg-background !border-2 !border-border !rounded-full !w-3 !h-3 !block"
                />
            </div>

            <!-- Node body -->
            <div
                class="w-20 h-20 rounded-xl border bg-card transition-all flex items-center justify-center"
                :class="[
                    selected ? 'ring-2 ring-primary ' : '',
                    hovered && !selected ? ' border-border/60' : ''
                ]"
            >
                <component :is="resolvedIcon" class="size-7" :style="{ color: definition?.color ?? '#6366f1' }" />

                <span class="absolute top-[84px] text-[11px] font-medium text-center leading-tight break-words text-neutral-800 dark:text-neutral-200 max-w-[88px]">
                    {{ data.label }}
                </span>
            </div>

            <!-- Right handles -->
            <div class="flex flex-col self-stretch justify-around -ml-1.5 z-10">
                <div v-for="output in definition?.outputs ?? []" :key="output.id" class="relative flex items-center">
                    <Handle
                        :id="output.id"
                        type="source"
                        :position="Position.Right"
                        class="!static !transform-none !relative !inset-auto !bg-background !border-2 !border-border !rounded-full !w-3 !h-3 !block"
                    />
                    <span v-if="(definition?.outputs?.length ?? 0) > 1" class="absolute left-4 text-[9px] text-muted-foreground whitespace-nowrap">
                        {{ output.label }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { RiPencilLine, RiDeleteBinLine } from '@remixicon/vue'
import * as RemixIcons from '@remixicon/vue'
import { useNodesStore } from '@/stores/nodes'
import { Button } from '@/components/ui/button'
import { ButtonGroup } from '@/components/ui/button-group'

const props = defineProps<{
    id: string
    data: {
        label: string
        config: Record<string, any>
        onEdit?: (id: string) => void
        onDelete?: (id: string) => void
    }
    selected: boolean
    type: string
}>()

const hovered = ref(false)

const nodesStore = useNodesStore()
const definition = computed(() => nodesStore.getDefinition(props.type))

const resolvedIcon = computed(() => {
    const name = (definition.value?.icon ?? 'ri-node-tree')
        .split('-').map((s: string) => s.charAt(0).toUpperCase() + s.slice(1)).join('')
    return (RemixIcons as Record<string, unknown>)[name] ?? RemixIcons.RiNodeTree
})

function handleEdit() {
    props.data.onEdit?.(props.id)
}

function handleDelete() {
    props.data.onDelete?.(props.id)
}
</script>
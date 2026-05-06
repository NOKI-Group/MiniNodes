<template>
    <div class="relative flex flex-col items-center">
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
                :class="selected ? 'ring-2 ring-primary' : ''"
            >
                <component :is="resolvedIcon" class="size-7" :style="{ color: definition?.color ?? '#6366f1' }" />

                <span class="absolute top-[84px] text-[11px] font-medium text-center leading-tight break-words text-neutral-800">
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

        <!-- Label absolute, centered below the node body (w-20 = 80px) -->

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

const resolvedIcon = computed(() => {
    const name = (definition.value?.icon ?? 'ri-node-tree')
        .split('-').map((s: string) => s.charAt(0).toUpperCase() + s.slice(1)).join('')
    return (RemixIcons as Record<string, unknown>)[name] ?? RemixIcons.RiNodeTree
})
</script>
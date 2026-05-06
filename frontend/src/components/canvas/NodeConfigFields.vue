<template>
    <div class="space-y-3">
        <div v-if="!definition?.fields?.length" class="text-xs text-muted-foreground">
            This node has no configuration.
        </div>

        <div v-for="field in definition?.fields ?? []" :key="field.key" class="space-y-1">
            <label class="text-xs font-medium text-foreground">{{ field.label }}</label>

            <select
                v-if="field.type === 'select'"
                v-model="localConfig[field.key]"
                class="w-full h-7 rounded-md border border-input bg-background px-2 text-xs"
                @change="emit('update', localConfig)"
            >
                <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
            </select>

            <textarea
                v-else-if="field.type === 'json'"
                v-model="localConfig[field.key]"
                rows="4"
                class="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs font-mono resize-y"
                :placeholder="field.placeholder"
                @input="emit('update', localConfig)"
            />

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
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { NodeDefinition } from '@/types'

const props = defineProps<{
    definition?: NodeDefinition
    config: Record<string, any>
}>()

const emit = defineEmits<{ update: [config: Record<string, any>] }>()

const localConfig = reactive<Record<string, any>>({})

watch(() => props.config, (val) => {
    Object.assign(localConfig, val)
}, { immediate: true })
</script>
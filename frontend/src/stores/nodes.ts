import { defineStore } from 'pinia'
import { ref } from 'vue'
import { nodesApi } from '@/api/modules'
import type { NodeDefinition } from '@/types'

export const useNodesStore = defineStore('nodes', () => {
    const definitions = ref<NodeDefinition[]>([])

    async function load() {
        const { data } = await nodesApi.getAll()
        definitions.value = data
    }

    function getDefinition(type: string): NodeDefinition | undefined {
        return definitions.value.find(d => d.type === type)
    }

    return { definitions, load, getDefinition }
})

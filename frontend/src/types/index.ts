export interface NodeDefinition {
    type: string
    label: string
    description: string
    color: string
    icon: string
    inputs: { id: string; label: string }[]
    outputs: { id: string; label: string }[]
    fields: {
        key: string
        label: string
        type: 'text' | 'select' | 'json' | 'number' | 'boolean'
        options?: string[]
        default?: any
        placeholder?: string
    }[]
}

export interface Workflow {
    id: string
    name: string
    description: string | null
    active: boolean
    graph: { nodes: any[]; edges: any[] }
    webhook_path: string | null
    created_at: string
    updated_at: string | null
}

export interface Execution {
    id: string
    workflow_id: string
    status: 'running' | 'success' | 'error'
    trigger: string | null
    input_data: any
    node_results: Record<string, { output: any; error: string | null }>
    error: string | null
    started_at: string
    finished_at: string | null
}

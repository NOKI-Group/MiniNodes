import api from './index'

export const workflowsApi = {
    getAll: () => api.get('/workflows/'),
    getOne: (id: string) => api.get(`/workflows/${id}`),
    create: (data: { name: string; description?: string }) => api.post('/workflows/', data),
    update: (id: string, data: any) => api.patch(`/workflows/${id}`, data),
    delete: (id: string) => api.delete(`/workflows/${id}`),
    execute: (id: string) => api.post(`/workflows/${id}/execute`),
}

export const executionsApi = {
    getAll: (workflowId?: string) => api.get('/executions/', { params: { workflow_id: workflowId } }),
    getOne: (id: string) => api.get(`/executions/${id}`),
}

export const nodesApi = {
    getAll: () => api.get('/nodes/'),
}

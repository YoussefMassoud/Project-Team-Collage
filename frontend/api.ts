const API_BASE = 'http://localhost:5000/api';

const fetchApi = async (endpoint: string, body: any) => {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    return res.json();
};

export const fetchPost = async (url: string) => {
    return fetchApi('/fetch-post', { url });
};

export const analyzePost = async (data: any) => {
    return fetchApi('/analyze', data);
};


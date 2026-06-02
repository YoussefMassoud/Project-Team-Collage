const API_BASE = 'http://127.0.0.1:5001/api';

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
    // Calling the new unified pipeline on port 5001
    const res = await fetch('http://127.0.0.1:5001/api/all-flow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    return res.json();
};
export const checkVideoStatus = async () => {
    const res = await fetch('http://127.0.0.1:5001/api/video-status');
    return res.json();
};

export const checkVideoProgress = async () => {
    const res = await fetch('http://127.0.0.1:5001/api/video-progress');
    return res.json();
};

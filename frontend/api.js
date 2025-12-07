const API_BASE = 'http://localhost:5000/api';

export const fetchPost = async (url) => {
    const res = await fetch(`${API_BASE}/fetch-post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
    });
    return res.json();
};

export const analyzePost = async (data) => {
    const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    return res.json();
};

export const predictPost = async (text) => {
    const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
    });
    return res.json();
};

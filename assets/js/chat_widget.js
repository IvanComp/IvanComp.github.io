import { pipeline, env } from '@xenova/transformers';

// Configuration
const EMBEDDING_MODEL = 'Xenova/all-MiniLM-L6-v2';
const CHAT_MODEL = 'Xenova/flan-t5-small'; // 80MB model, reliable for RAG
const RAG_DATA_URL = '/assets/data/rag_data.json';
const TOP_K = 3;

// State
let embedder = null;
let generator = null;
let ragData = null;
let isModelsLoading = false;
let isModelsReady = false;

// DOM Elements
const chatWindow = document.getElementById('chat-window');
const chatBubbleBtn = document.getElementById('chat-bubble-btn');
const closeBtn = document.getElementById('chat-close-btn');
const inputField = document.getElementById('chat-input-field');
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('chat-messages');
const typingIndicator = document.getElementById('typing-indicator');
const initPanel = document.getElementById('init-panel');
const loadModelBtn = document.getElementById('load-model-btn');
const progressContainer = document.getElementById('progress-container');
const progressEmbed = document.getElementById('progress-embed');
const progressChat = document.getElementById('progress-chat');
const statusDiv = document.getElementById('chat-status');

// Event Listeners
chatBubbleBtn.addEventListener('click', toggleChat);
closeBtn.addEventListener('click', toggleChat);
loadModelBtn.addEventListener('click', initSystem);
sendBtn.addEventListener('click', handleUserMessage);
inputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleUserMessage();
});

// Auto-Init on Load (as requested)
document.addEventListener('DOMContentLoaded', () => {
    // We bind the toggle to auto-init
});

// Redefine toggleChat to handle auto-init
function toggleChat() {
    const display = chatWindow.style.display;

    if (display === 'none' || display === '') {
        chatWindow.style.display = 'flex';
        // Auto-init disabled for maintenance
        // if (!isModelsReady && !isModelsLoading) {
        //     initSystem();
        // }
    } else {
        chatWindow.style.display = 'none';
    }
}

async function initSystem() {
    if (isModelsLoading || isModelsReady) return;

    isModelsLoading = true;
    loadModelBtn.style.display = 'none'; // Hide button since it's auto
    progressContainer.style.display = 'block';

    try {
        // 1. Load RAG Data
        statusDiv.style.display = 'block';
        statusDiv.textContent = "Loading Knowledge Base...";
        const response = await fetch(RAG_DATA_URL);
        if (!response.ok) throw new Error(`Failed to load RAG data: ${response.status} ${response.statusText}`);
        ragData = await response.json();
        console.log(`Loaded ${ragData.length} chunks.`);

        // 2. Load Embedding Model
        statusDiv.textContent = "Loading Embedding Model...";
        progressEmbed.textContent = "Downloading...";
        progressEmbed.style.color = "#666";

        env.allowLocalModels = false; // Force CDN

        embedder = await pipeline('feature-extraction', EMBEDDING_MODEL, {
            progress_callback: (data) => {
                if (data.status === 'progress') {
                    progressEmbed.textContent = `${Math.round(data.progress)}%`;
                } else if (data.status === 'done') {
                    progressEmbed.textContent = "Ready";
                    progressEmbed.style.color = "green";
                }
            }
        });

        // 3. Load Chat Model
        statusDiv.textContent = "Loading Chat Model...";
        progressChat.textContent = "Downloading...";
        progressChat.style.color = "#666";

        generator = await pipeline('text2text-generation', CHAT_MODEL, {
            progress_callback: (data) => {
                if (data.status === 'progress') {
                    progressChat.textContent = `${Math.round(data.progress)}%`;
                } else if (data.status === 'done') {
                    progressChat.textContent = "Ready";
                    progressChat.style.color = "green";
                }
            }
        });

        // Success
        console.log("Models loaded successfully.");
        isModelsReady = true;
        isModelsLoading = false;

        initPanel.style.display = "none";
        statusDiv.textContent = "Local RAG Ready.";
        statusDiv.style.color = "green";
        inputField.disabled = false;
        sendBtn.disabled = false;
        inputField.placeholder = "Ask about Ivan's papers...";
        inputField.focus();

    } catch (error) {
        console.error("Initialization Error:", error);
        statusDiv.textContent = "Error: " + error.message;
        statusDiv.style.color = "red";
        isModelsLoading = false;
        loadModelBtn.style.display = 'inline-block'; // Show retry button
        loadModelBtn.textContent = "Retry Download";
    }
}

// Cosine Similarity
function cosineSimilarity(xs, ys) {
    let dot = 0.0;
    let normx = 0.0;
    let normy = 0.0;
    for (let i = 0; i < xs.length; i++) {
        dot += xs[i] * ys[i];
        normx += xs[i] * xs[i];
        normy += ys[i] * ys[i];
    }
    return dot / (Math.sqrt(normx) * Math.sqrt(normy));
}

async function retrieveChunks(query) {
    // Compute query embedding
    const output = await embedder(query, { pooling: 'mean', normalize: true });
    const queryEmbedding = output.data;

    // Rank chunks
    const scoredChunks = ragData.map(chunk => {
        return {
            ...chunk,
            score: cosineSimilarity(queryEmbedding, chunk.embedding)
        };
    });

    // Sort descending
    scoredChunks.sort((a, b) => b.score - a.score);

    return scoredChunks.slice(0, TOP_K);
}

async function handleUserMessage() {
    const userQuestion = inputField.value.trim();
    if (!userQuestion || !isModelsReady) return;

    appendMessage(userQuestion, 'user');
    inputField.value = '';

    sendBtn.disabled = true;
    inputField.disabled = true;
    typingIndicator.style.display = 'block';

    try {
        // RAG Retrieval
        const topChunks = await retrieveChunks(userQuestion);
        console.log("Retrieved Chunks:", topChunks);

        const contextText = topChunks.map(c => `[From ${c.source}]: ${c.text}`).join("\n\n");

        // Construct Prompt for T5
        // T5 is text-to-text, no chat template. Simple concatenation works best.
        const prompt = `context: ${contextText} question: ${userQuestion}`;

        // Generate
        const output = await generator(prompt, {
            max_new_tokens: 150,
            temperature: 0.5,
            do_sample: false
        });

        const responseText = output[0].generated_text;
        appendMessage(responseText, 'bot');

    } catch (error) {
        console.error("Generation Error:", error);
        appendMessage("Error generating response: " + error.message, 'bot');
    } finally {
        sendBtn.disabled = false;
        inputField.disabled = false;
        typingIndicator.style.display = 'none';
        inputField.focus();
    }
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

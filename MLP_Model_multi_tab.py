!pip install --ignore-installed pyngrok flask flask-socketio eventlet

import sys
import subprocess
try:
    location_info = subprocess.check_output("pip show flask | grep Location", shell=True).decode('utf-8')
    package_path = location_info.split(': ')[1].strip()
    if package_path not in sys.path:
        sys.path.append(package_path)
        print(f"Added {package_path} to system path.")
except Exception as e:
    print(f"Could not automatically find package path, using default. Error: {e}")
    py_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    default_path = f"/usr/local/lib/{py_version}/dist-packages"
    if default_path not in sys.path:
        sys.path.append(default_path)
        print(f"Added default path {default_path} to system path.")

from getpass import getpass
import os
import random
import heapq
import copy
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from pyngrok import ngrok
import eventlet

os.system(f"ngrok config add-authtoken 2yRC04Bqq3HdKaTA4x7ghcYGfi8_4bwcVxeu2JTVXV4zzwxo8")

if not os.path.exists('templates'):
    os.makedirs('templates')

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced MLP Encryption Visualizer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f172a, #1e3a8a, #4c1d95); background-size: 200% 200%; color: #d1d5db; animation: moveGradient 20s ease infinite; }
        @keyframes moveGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .mono { font-family: 'Roboto Mono', monospace; }
        .glass-panel { background: rgba(31, 41, 55, 0.5); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 1rem; }
        .log-panel { padding: 1.5rem; height: 400px; overflow-y: auto; scrollbar-width: thin; scrollbar-color: #4b5563 #1f2937; }
        .log-panel::-webkit-scrollbar { width: 8px; }
        .log-panel::-webkit-scrollbar-track { background: #1f2937; }
        .log-panel::-webkit-scrollbar-thumb { background-color: #4b5563; border-radius: 4px; }
        .log-entry { margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        .custom-button { background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); transition: all 0.3s ease; font-weight: 500; }
        .custom-button:hover:not(:disabled) { background-color: rgba(255, 255, 255, 0.2); }
        .custom-button:disabled { background-color: rgba(55, 65, 81, 0.4); border-color: rgba(255, 255, 255, 0.1); color: #9ca3af; cursor: not-allowed; }
        .switch { position: relative; display: inline-block; width: 34px; height: 20px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(255,255,255,0.3); transition: .4s; border-radius: 20px; }
        .slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #ef4444; }
        input:checked + .slider:before { transform: translateX(14px); }
        #network-graph-svg { width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 0; }
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="max-w-7xl mx-auto">
        <div class="flex justify-between items-center mb-4">
            <h1 class="text-3xl font-bold text-white">Advanced MLP Encryption Visualizer</h1>
            <div class="text-right">
                <p class="text-lg font-semibold text-green-400">Node ID: <span id="myNodeId" class="mono">...</span></p>
            </div>
        </div>

        <div class="glass-panel p-6 mb-8 grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
            <div class="flex flex-col items-start">
                <span class="block text-sm font-medium text-gray-300 mb-2">1. Choose File</span>
                <input type="file" id="fileInput" class="hidden"/>
                <label for="fileInput" class="text-white py-2 px-5 rounded-lg custom-button cursor-pointer w-full text-center">Select File</label>
                <span id="fileName" class="text-xs text-gray-400 mt-1">No file selected</span>
            </div>
             <div class="flex flex-col items-start">
                <span class="block text-sm font-medium text-gray-300 mb-2">2. Choose Recipient</span>
                <select id="recipientSelect" class="bg-slate-700 border border-slate-600 rounded-lg py-2 px-3 text-white custom-button w-full" disabled>
                    <option>No other nodes</option>
                </select>
            </div>
            <button id="findRouteButton" class="text-white py-2 px-5 rounded-lg custom-button" disabled>3. Find Route</button>
            <button id="sendChunkButton" class="text-white py-2 px-5 rounded-lg custom-button" disabled>4. Send Next Chunk</button>
        </div>
        
        <div id="routeInfoPanel" class="glass-panel p-5 mb-8 text-center hidden">
            <h3 class="font-bold text-lg mb-2">Calculated Route & Corruption Control</h3>
            <div id="routeDisplay" class="flex items-center justify-center flex-wrap gap-2 mono"></div>
        </div>

        <div id="statusPanel" class="glass-panel p-5 mb-8 text-center">
            <p class="mono text-lg" id="statusText">Welcome! Waiting for other nodes to connect...</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div class="glass-panel p-6">
                <h2 class="text-2xl font-bold text-center mb-4">Live Network Map</h2>
                <div id="network-map" class="relative h-64 bg-black/20 rounded-lg">
                    <svg id="network-graph-svg"></svg>
                    <div id="network-nodes-container" class="absolute top-0 left-0 w-full h-full"></div>
                </div>
            </div>
            <div class="log-panel glass-panel" id="systemLog">
                <h3 class="text-xl font-bold text-amber-400">System & Network Log</h3>
                <div id="systemLogContent"></div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="log-panel glass-panel" id="senderLog">
                <h3 class="text-xl font-bold text-blue-400">Sender Log</h3>
                <div id="senderLogContent"></div>
            </div>
            <div class="log-panel glass-panel" id="receiverLog">
                <h3 class="text-xl font-bold text-green-400">Receiver Log</h3>
                <div id="receiverLogContent"></div>
            </div>
        </div>
    </div>

<script>
const CHUNK_SIZE_BYTES = 1024;
const INITIAL_VECTOR_STRING = 'MySharedSecretForStartingTheChain';
const MLP_INPUT_SIZE = 32;
const MLP_HIDDEN_SIZE = 64;
const MLP_OUTPUT_SIZE = 32;

class MLP {
    constructor(w1, b1, w2, b2) { this.w1 = w1; this.b1 = b1; this.w2 = w2; this.b2 = b2; }
    static relu(x) { return Math.max(0, x); }
    static sigmoid(x) { return 1 / (1 + Math.exp(-x)); }
    predict(input) {
        let hidden = new Array(MLP_HIDDEN_SIZE).fill(0).map((_, j) => {
            let sum = input.reduce((acc, val, i) => acc + val * this.w1[i][j], 0);
            return MLP.relu(sum + this.b1[j]);
        });
        let output = new Array(MLP_OUTPUT_SIZE).fill(0).map((_, j) => {
            let sum = hidden.reduce((acc, val, i) => acc + val * this.w2[i][j], 0);
            return MLP.sigmoid(sum + this.b2[j]);
        });
        return { hidden, output };
    }
}
const seededRandom = (seed) => { let s = seed; return () => { s = (s * 9301 + 49297) % 233280; return (s / 233280.0) * 2 - 1; }; };
const generateFixedWeights = (iS, oS, seed) => Array(iS).fill(0).map(() => Array(oS).fill(0).map(seededRandom(seed++)));
const generateFixedBiases = (size, seed) => Array(size).fill(0).map(seededRandom(seed));
const mlp = new MLP(generateFixedWeights(MLP_INPUT_SIZE, MLP_HIDDEN_SIZE, 12345), generateFixedBiases(MLP_HIDDEN_SIZE, 54321), generateFixedWeights(MLP_HIDDEN_SIZE, MLP_OUTPUT_SIZE, 67890), generateFixedBiases(MLP_OUTPUT_SIZE, 9876));

const bytesToBinaryString = (bytes) => Array.from(bytes).map(b => b.toString(2).padStart(8, '0')).join('');
const binaryStringToBytes = (bin) => new Uint8Array(bin.match(/.{1,8}/g)?.map(byte => parseInt(byte, 2)) || []);
const stringToSha256Bytes = async (str) => new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str)));
const bytesToSha256Bytes = async (bytes) => new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
const getInitialVector = async () => await stringToSha256Bytes(INITIAL_VECTOR_STRING);
const preprocessChunkForMLP = (chunkBytes) => {
    const inputVector = new Array(MLP_INPUT_SIZE).fill(0);
    for (let i = 0; i < Math.min(chunkBytes.length, MLP_INPUT_SIZE); i++) { inputVector[i] = chunkBytes[i] / 255.0; }
    return inputVector;
};
const hypernetwork_key_generator = async (chunk_bytes) => {
    const inputVector = preprocessChunkForMLP(chunk_bytes);
    const { output } = mlp.predict(inputVector);
    return new Uint8Array(output.map(v => Math.floor(v * 255)));
};
const hash_plaintext_chunk = async (chunk_bytes) => {
    const hashBytes = await bytesToSha256Bytes(chunk_bytes);
    return Array.from(hashBytes).map(b => b.toString(16).padStart(2, '0')).join('');
};
const fast_xor_transform = (binary_data, key_bytes) => {
    if (!binary_data.length) return "";
    let key_binary = bytesToBinaryString(key_bytes);
    if (!key_binary.length) return binary_data;
    const tiled_key_binary = key_binary.repeat(Math.ceil(binary_data.length / key_binary.length)).slice(0, binary_data.length);
    let result_binary = '';
    for (let i = 0; i < binary_data.length; i++) {
        result_binary += binary_data[i] === tiled_key_binary[i] ? '0' : '1';
    }
    return result_binary;
};

const dom = {
    fileInput: document.getElementById('fileInput'),
    fileName: document.getElementById('fileName'),
    recipientSelect: document.getElementById('recipientSelect'),
    findRouteButton: document.getElementById('findRouteButton'),
    sendChunkButton: document.getElementById('sendChunkButton'),
    statusText: document.getElementById('statusText'),
    senderLog: document.getElementById('senderLogContent'),
    receiverLog: document.getElementById('receiverLogContent'),
    systemLog: document.getElementById('systemLogContent'),
    myNodeId: document.getElementById('myNodeId'),
    networkMap: document.getElementById('network-map'),
    networkGraphSvg: document.getElementById('network-graph-svg'),
    networkNodesContainer: document.getElementById('network-nodes-container'),
    routeInfoPanel: document.getElementById('routeInfoPanel'),
    routeDisplay: document.getElementById('routeDisplay'),
};

let state = {
    myId: null,
    isSending: false,
    file: { originalBytes: null, totalChunks: 0, currentChunkIndex: 0 },
    transfer: { senderKey: null, receiverKey: null, path: [], lastFailedPath: [] }
};
const socket = io();

function addLog(panel, content, colorClass = '') {
    const entry = document.createElement('div');
    entry.className = `log-entry text-sm ${colorClass}`;
    entry.innerHTML = content;
    panel.prepend(entry);
    panel.scrollTop = 0;
}
const truncate = (str, len = 32) => str?.length > len ? str.substring(0, len) + '...' : str;
const bytesToHex = (bytes) => bytes ? Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('') : '';

function updateNetworkGraph(nodes, graph) {
    dom.networkNodesContainer.innerHTML = '';
    dom.networkGraphSvg.innerHTML = '';
    const positions = {};
    const mapRect = dom.networkMap.getBoundingClientRect();
    if (mapRect.width === 0) return;
    const angleStep = (2 * Math.PI) / (Object.keys(nodes).length || 1);
    let i = 0;
    for (const nodeId in nodes) {
        const angle = angleStep * i++;
        positions[nodeId] = {
            x: mapRect.width / 2 + (mapRect.width / 2 - 30) * Math.cos(angle),
            y: mapRect.height / 2 + (mapRect.height / 2 - 30) * Math.sin(angle),
        };
    }
    for (const sourceId in graph) {
        if (!positions[sourceId]) continue;
        for (const targetId in graph[sourceId]) {
            if (!positions[targetId]) continue;
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', positions[sourceId].x);
            line.setAttribute('y1', positions[sourceId].y);
            line.setAttribute('x2', positions[targetId].x);
            line.setAttribute('y2', positions[targetId].y);
            line.setAttribute('stroke', 'rgba(156, 163, 175, 0.3)');
            line.setAttribute('stroke-width', '1');
            dom.networkGraphSvg.appendChild(line);
        }
    }
    for (const nodeId in nodes) {
        const pos = positions[nodeId];
        const nodeDiv = document.createElement('div');
        nodeDiv.className = 'absolute w-8 h-8 rounded-full flex items-center justify-center font-bold';
        nodeDiv.style.left = `${pos.x - 16}px`;
        nodeDiv.style.top = `${pos.y - 16}px`;
        nodeDiv.style.backgroundColor = nodeId === state.myId ? '#22c55e' : '#3b82f6';
        nodeDiv.style.border = '2px solid rgba(255,255,255,0.7)';
        nodeDiv.textContent = nodes[nodeId].name.split('-')[1];
        dom.networkNodesContainer.appendChild(nodeDiv);
    }
}

function displayRoute(path, isNewRouteAfterFailure = false) {
    dom.routeDisplay.innerHTML = '';
    path.forEach((node, index) => {
        const nodeContainer = document.createElement('div');
        nodeContainer.className = 'flex items-center';

        const nodeEl = document.createElement('div');
        nodeEl.className = 'p-2 rounded-md flex flex-col items-center';
        nodeEl.textContent = node.name;
        
        if (index > 0 && index < path.length - 1) {
            const corruptionControl = document.createElement('div');
            corruptionControl.className = 'flex items-center mt-1';
            corruptionControl.innerHTML = `
                <span class="text-xs text-red-400 mr-2">Corrupt</span>
                <label class="switch">
                    <input type="checkbox" class="corruption-checkbox" data-node-id="${node.id}">
                    <span class="slider"></span>
                </label>`;
            nodeEl.appendChild(corruptionControl);
        }
        nodeContainer.appendChild(nodeEl);

        if (index < path.length - 1) {
            const arrow = document.createElement('span');
            arrow.className = 'text-xl mx-2 self-center';
            arrow.textContent = '→';
            nodeContainer.appendChild(arrow);
        }
        dom.routeDisplay.appendChild(nodeContainer);
    });
    if (isNewRouteAfterFailure) {
        const notice = document.createElement('p');
        notice.className = "w-full text-center text-yellow-400 text-sm mt-2";
        notice.textContent = "A new route has been found. Please re-send the failed chunk.";
        dom.routeDisplay.appendChild(notice);
    }
    dom.routeInfoPanel.classList.remove('hidden');
}


function checkCanFindRoute() {
    dom.findRouteButton.disabled = !(dom.fileInput.files.length > 0 && dom.recipientSelect.value);
}
dom.fileInput.addEventListener('change', () => {
    dom.fileName.textContent = dom.fileInput.files.length > 0 ? dom.fileInput.files[0].name : 'No file selected';
    checkCanFindRoute();
});
dom.recipientSelect.addEventListener('change', checkCanFindRoute);

dom.findRouteButton.addEventListener('click', async () => {
    const file = dom.fileInput.files[0];
    if (!file) { alert("Please select a file first."); return; }

    dom.findRouteButton.disabled = true;
    dom.sendChunkButton.disabled = true;
    dom.statusText.textContent = "Initializing file transfer...";
    addLog(dom.systemLog, "Reading file and initializing transfer...");

    const arrayBuffer = await file.arrayBuffer();
    state.file.originalBytes = new Uint8Array(arrayBuffer);
    state.file.totalChunks = Math.ceil(state.file.originalBytes.length / CHUNK_SIZE_BYTES);
    if (state.file.totalChunks === 0) {
        addLog(dom.systemLog, "File is empty, aborting.", "text-red-400");
        dom.findRouteButton.disabled = false;
        return;
    }
    state.file.currentChunkIndex = 0;

    const initialVector = await getInitialVector();
    state.transfer.senderKey = initialVector;
    state.transfer.receiverKey = initialVector;

    addLog(dom.senderLog, `<div class="log-title">Init Sent</div><div>Chunks: ${state.file.totalChunks}</div>`);
    addLog(dom.systemLog, `Requesting route to ${dom.recipientSelect.options[dom.recipientSelect.selectedIndex].text}...`);
    socket.emit('request_initial_route', {
        recipient_id: dom.recipientSelect.value,
        initial_vector_hex: bytesToHex(initialVector),
        total_chunks: state.file.totalChunks,
        file_name: file.name
    });
});

dom.sendChunkButton.addEventListener('click', async () => {
    dom.sendChunkButton.disabled = true;
    if (state.file.currentChunkIndex >= state.file.totalChunks) {
        dom.statusText.textContent = `Success! All ${state.file.totalChunks} chunks sent.`;
        addLog(dom.systemLog, "File transfer complete.", "text-green-400 font-bold");
        return;
    }

    dom.statusText.textContent = `Sending chunk ${state.file.currentChunkIndex + 1}/${state.file.totalChunks}...`;
    const chunkIndex = state.file.currentChunkIndex;
    const start = chunkIndex * CHUNK_SIZE_BYTES;
    const end = Math.min(start + CHUNK_SIZE_BYTES, state.file.originalBytes.length);
    const plaintextChunkBytes = state.file.originalBytes.slice(start, end);

    const keyForEncoding = state.transfer.senderKey;
    const plaintextChunkBinary = bytesToBinaryString(plaintextChunkBytes);
    const encodedChunkBinary = fast_xor_transform(plaintextChunkBinary, keyForEncoding);
    const plaintextHash = await hash_plaintext_chunk(plaintextChunkBytes);
    const nextSenderKey = await hypernetwork_key_generator(plaintextChunkBytes);

    addLog(dom.senderLog, `<div class="log-title">Sending C${chunkIndex + 1}</div><div class="mono text-xs">Hash: ${truncate(plaintextHash)}<br>Key Used: ${truncate(bytesToHex(keyForEncoding))}</div>`);
    state.transfer.senderKey = nextSenderKey;

    const nodesToCorrupt = Array.from(document.querySelectorAll('.corruption-checkbox:checked')).map(cb => cb.dataset.nodeId);

    socket.emit('transfer_chunk', {
        path: state.transfer.path.map(p => p.id),
        nodes_to_corrupt: nodesToCorrupt,
        payload: {
            encoded_chunk_binary: encodedChunkBinary,
            plaintext_hash: plaintextHash,
            chunk_index: chunkIndex
        }
    });
});


socket.on('connect', () => {});

socket.on('assign_id', (data) => {
    state.myId = data.id;
    dom.myNodeId.textContent = data.name;
    addLog(dom.systemLog, `This client is <strong>${data.name}</strong>`);
});

socket.on('network_update', (data) => {
    const { nodes, graph } = data;
    addLog(dom.systemLog, `Network updated. Total nodes: ${Object.keys(nodes).length}`);
    updateNetworkGraph(nodes, graph);

    const otherNodes = Object.keys(nodes).filter(id => id !== state.myId);
    dom.recipientSelect.innerHTML = '';
    if (otherNodes.length > 0) {
        dom.recipientSelect.disabled = false;
        dom.recipientSelect.innerHTML = '<option value="">Select a node</option>';
        otherNodes.forEach(id => {
            let option = document.createElement('option');
            option.value = id;
            option.textContent = `${nodes[id].name}`;
            dom.recipientSelect.appendChild(option);
        });
    } else {
        dom.recipientSelect.disabled = true;
        dom.recipientSelect.innerHTML = '<option>No other nodes</option>';
    }
    checkCanFindRoute();
});

socket.on('route_info', (data) => {
    if (data.error) {
        dom.statusText.textContent = `Error: ${data.error}`;
        addLog(dom.systemLog, `Routing failed: ${data.error}`, 'text-red-400');
        dom.findRouteButton.disabled = false;
        return;
    }
    state.transfer.path = data.path;
    const pathString = data.path.map(p => p.name).join(' -> ');
    addLog(dom.systemLog, `Route found: ${pathString}`, data.is_new_route ? 'text-yellow-400' : 'text-green-400');
    displayRoute(data.path, data.is_new_route);
    dom.sendChunkButton.disabled = false;
    dom.statusText.textContent = data.is_new_route 
        ? `New route found! Please re-send failed chunk ${state.file.currentChunkIndex + 1}.`
        : `Route found. Ready to send chunk ${state.file.currentChunkIndex + 1}.`;
});

socket.on('receive_transfer_request', (data) => {
    state.transfer.receiverKey = binaryStringToBytes(bytesToBinaryString(new Uint8Array(data.initial_vector_hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)))));
    state.file.totalChunks = data.total_chunks;
    state.file.currentChunkIndex = 0;
    dom.statusText.textContent = `Incoming file "${data.file_name}" from ${data.sender_name}.`;
    addLog(dom.receiverLog, `<div class="log-title">Incoming file from ${data.sender_name}</div><div>Total Chunks: ${data.total_chunks}</div>`);
});

socket.on('forward_chunk', (data) => {
    const { from_node, to_node, payload, corrupt_this_packet } = data;
    addLog(dom.systemLog, `Received chunk C${payload.chunk_index + 1} from ${from_node.name}, forwarding to ${to_node.name}.`);
    if (corrupt_this_packet) {
        const len = payload.encoded_chunk_binary.length;
        const corruptIndex = Math.floor(Math.random() * len);
        const newBit = payload.encoded_chunk_binary[corruptIndex] === '0' ? '1' : '0';
        payload.encoded_chunk_binary = payload.encoded_chunk_binary.substring(0, corruptIndex) + newBit + payload.encoded_chunk_binary.substring(corruptIndex + 1);
        addLog(dom.systemLog, `Packet C${payload.chunk_index + 1} was CORRUPTED at this node as instructed!`, 'text-red-400 font-bold');
    }
    socket.emit('forward_chunk_response', payload);
});

socket.on('deliver_chunk', async (data) => {
    const { payload } = data;
    const chunkIndex = payload.chunk_index;
    const keyForDecoding = state.transfer.receiverKey;
    const decodedChunkBinary = fast_xor_transform(payload.encoded_chunk_binary, keyForDecoding);
    const decodedChunkBytes = binaryStringToBytes(decodedChunkBinary);
    const receivedHash = await hash_plaintext_chunk(decodedChunkBytes);

    if (receivedHash === payload.plaintext_hash) {
        addLog(dom.receiverLog, `<div class="log-title text-green-400">Received C${chunkIndex + 1} OK</div><div class="mono text-xs">Hashes Match!</div>`, 'text-green-400');
        state.transfer.receiverKey = await hypernetwork_key_generator(decodedChunkBytes);
        state.file.currentChunkIndex++;
        socket.emit('chunk_receipt', { status: 'ok', chunk_index: chunkIndex });
    } else {
        addLog(dom.receiverLog, `<div class="log-title text-red-400">CORRUPTION on C${chunkIndex + 1}</div><div class="mono text-xs text-red-400">HASH MISMATCH!</div>`, 'text-red-400');
        dom.statusText.textContent = `FATAL ERROR: Corruption detected. Transfer aborted.`;
        socket.emit('chunk_receipt', { status: 'fail', chunk_index: chunkIndex });
    }
});

socket.on('delivery_report', (data) => {
    if (data.status === 'ok') {
        addLog(dom.senderLog, `Recipient acknowledged C${data.chunk_index + 1}.`, 'text-green-400');
        state.file.currentChunkIndex++;
        if (state.file.currentChunkIndex < state.file.totalChunks) {
            dom.sendChunkButton.disabled = false;
            dom.statusText.textContent = `Ready to send chunk ${state.file.currentChunkIndex + 1}.`;
        } else {
            dom.statusText.textContent = 'All chunks sent successfully!';
            addLog(dom.systemLog, 'Transfer Complete!', 'text-green-400 font-bold');
        }
    } else {
        addLog(dom.senderLog, `Corruption reported on C${data.chunk_index + 1}!`, 'text-red-400 font-bold');
        dom.statusText.textContent = `Corruption detected! Requesting new route and running diagnostics...`;
        state.transfer.lastFailedPath = state.transfer.path;
        
        socket.emit('request_new_route', {
            recipient_id: dom.recipientSelect.value,
            failed_path_ids: state.transfer.lastFailedPath.map(p => p.id)
        });

        const chunkIndex = state.file.currentChunkIndex;
        const start = chunkIndex * CHUNK_SIZE_BYTES;
        const end = Math.min(start + CHUNK_SIZE_BYTES, state.file.originalBytes.length);
        const plaintextChunkBytes = state.file.originalBytes.slice(start, end);
        socket.emit('start_diagnostic', {
            failed_path: state.transfer.lastFailedPath.map(p => p.id),
            plaintext_chunk_hex: bytesToHex(plaintextChunkBytes)
        });
    }
});

socket.on('diagnostic_started', (data) => {
    addLog(dom.systemLog, `Diagnosing failed path: ${data.path_names.join(' -> ')}`, 'text-yellow-400');
});

socket.on('forward_diagnostic', async (data) => {
    const { from_node, to_node, probe } = data;
    addLog(dom.systemLog, `Diagnostic: relaying probe from ${from_node.name} to ${to_node.name}. Running local MLP...`, 'text-yellow-400');
    
    const receivedPlaintext = new Uint8Array(probe.plaintext_chunk_hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
    const nextKeyFromThisNode = await hypernetwork_key_generator(receivedPlaintext);
    
    probe.report[state.myId] = bytesToHex(nextKeyFromThisNode);
    
    socket.emit('forward_diagnostic_response', probe);
});

socket.on('diagnostic_complete', async (data) => {
    const { probe } = data;
    addLog(dom.systemLog, `Diagnostic complete. Analyzing results...`, 'text-yellow-400 font-bold');
    
    const failedPath = state.transfer.lastFailedPath;
    const chunkIndex = state.file.currentChunkIndex;
    const start = chunkIndex * CHUNK_SIZE_BYTES;
    const end = Math.min(start + CHUNK_SIZE_BYTES, state.file.originalBytes.length);
    const plaintextChunkBytes = state.file.originalBytes.slice(start, end);
    const correctNextKey = bytesToHex(await hypernetwork_key_generator(plaintextChunkBytes));
    
    let culpritNodeName = "Unknown (corruption may be at the final hop or receiver)";
    
    let lastGoodKey = correctNextKey;
    for (let i = 1; i < failedPath.length - 1; i++) {
        const node = failedPath[i];
        const keyFromThisNode = probe.report[node.id];
        
        if (keyFromThisNode !== lastGoodKey) {
            culpritNodeName = failedPath[i-1].name;
            break; 
        }
        lastGoodKey = keyFromThisNode;
    }

    addLog(dom.systemLog, `FAULT LOCALIZED: MLP output diverged after <strong>${culpritNodeName}</strong>.`, 'text-red-500 font-extrabold');
});

window.onload = () => {};

</script>
</body>
</html>
"""

with open('templates/index.html', 'w') as f:
    f.write(html_content)

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

nodes = {}
graph = {}
sessions = {}

MAX_INITIAL_PEERS = 2

def find_shortest_path(start_id, end_id, current_graph):
    distances = {node: float('inf') for node in current_graph}
    if start_id not in distances: return None
    distances[start_id] = 0
    previous_nodes = {node: None for node in current_graph}
    pq = [(0, start_id)]

    while pq:
        current_distance, current_node_id = heapq.heappop(pq)
        if current_node_id not in distances or current_distance > distances[current_node_id]: continue
        if current_node_id == end_id: break

        for neighbor, weight in current_graph.get(current_node_id, {}).items():
            if neighbor in distances:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node_id
                    heapq.heappush(pq, (distance, neighbor))
    path, current = [], end_id
    while current is not None:
        path.insert(0, current)
        current = previous_nodes.get(current)
    return path if path and path[0] == start_id else None

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    node_name = f"Node-{len(nodes) + 1}"
    nodes[sid] = {'name': node_name, 'id': sid}
    graph[sid] = {}
    
    potential_peers = [peer_sid for peer_sid in nodes if peer_sid != sid]
    random.shuffle(potential_peers)
    peers_to_connect = potential_peers[:MAX_INITIAL_PEERS]
    
    for peer_sid in peers_to_connect:
        weight = random.randint(1, 10)
        graph[sid][peer_sid] = weight
        if peer_sid not in graph: graph[peer_sid] = {}
        graph[peer_sid][sid] = weight

    emit('assign_id', {'id': sid, 'name': node_name})
    emit('network_update', {'nodes': nodes, 'graph': graph}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in nodes:
        del nodes[sid]
        if sid in graph: del graph[sid]
        for node in graph:
            if sid in graph[node]: del graph[node][sid]
        sessions.pop(sid, None)
        emit('network_update', {'nodes': nodes, 'graph': graph}, broadcast=True)

@socketio.on('request_initial_route')
def handle_initial_route(data):
    sender_id, recipient_id = request.sid, data['recipient_id']
    path_ids = find_shortest_path(sender_id, recipient_id, graph)

    if not path_ids or len(path_ids) < 2:
        emit('route_info', {'error': 'No route found.'})
        return

    path_info = [{'id': pid, 'name': nodes[pid]['name']} for pid in path_ids]
    emit('route_info', {'path': path_info, 'is_new_route': False})

    emit('receive_transfer_request', {
        'sender_name': nodes[sender_id]['name'],
        'initial_vector_hex': data['initial_vector_hex'],
        'total_chunks': data['total_chunks'],
        'file_name': data['file_name']
    }, room=recipient_id)

@socketio.on('request_new_route')
def handle_new_route_request(data):
    sender_id, recipient_id = request.sid, data['recipient_id']
    failed_path_ids = data.get('failed_path_ids', [])
    
    temp_graph = copy.deepcopy(graph)
    if len(failed_path_ids) > 1:
        for i in range(len(failed_path_ids) - 1):
            u, v = failed_path_ids[i], failed_path_ids[i+1]
            if u in temp_graph and v in temp_graph[u]:
                del temp_graph[u][v]
            if v in temp_graph and u in temp_graph[v]:
                del temp_graph[v][u]
            
    path_ids = find_shortest_path(sender_id, recipient_id, temp_graph)

    if not path_ids or len(path_ids) < 2:
        emit('route_info', {'error': 'No alternative route could be found.'})
        return
        
    path_info = [{'id': pid, 'name': nodes[pid]['name']} for pid in path_ids]
    emit('route_info', {'path': path_info, 'is_new_route': True})


@socketio.on('transfer_chunk')
def handle_transfer_chunk(data):
    path, payload, nodes_to_corrupt = data['path'], data['payload'], data['nodes_to_corrupt']
    sender_id = request.sid
    sessions[sender_id] = {'recipient_id': path[-1]}
    
    next_node_id = path[1]
    sessions[next_node_id] = {'sender_id': sender_id, 'path': path, 'nodes_to_corrupt': nodes_to_corrupt}
    
    emit('forward_chunk', {
        'from_node': nodes[path[0]], 'to_node': nodes[path[1]],
        'payload': payload, 'corrupt_this_packet': next_node_id in nodes_to_corrupt
    }, room=next_node_id)

@socketio.on('forward_chunk_response')
def handle_forward_response(payload):
    intermediate_id = request.sid
    session = sessions.pop(intermediate_id, None)
    if not session: return

    path, sender_id, nodes_to_corrupt = session['path'], session['sender_id'], session['nodes_to_corrupt']
    current_index_in_path = path.index(intermediate_id)
    
    if current_index_in_path < len(path) - 2:
        next_node_id = path[current_index_in_path + 1]
        sessions[next_node_id] = session
        emit('forward_chunk', {
            'from_node': nodes[intermediate_id], 'to_node': nodes[next_node_id],
            'payload': payload, 'corrupt_this_packet': next_node_id in nodes_to_corrupt
        }, room=next_node_id)
    else:
        recipient_id = path[-1]
        emit('deliver_chunk', {'payload': payload}, room=recipient_id)

@socketio.on('chunk_receipt')
def handle_chunk_receipt(data):
    recipient_id = request.sid
    sender_id = next((sid for sid, s in sessions.items() if s.get('recipient_id') == recipient_id), None)
    if sender_id:
        emit('delivery_report', data, room=sender_id)

@socketio.on('start_diagnostic')
def start_diagnostic(data):
    sender_id, failed_path_ids = request.sid, data['failed_path']
    if not failed_path_ids or len(failed_path_ids) < 2: return
    
    next_node_id = failed_path_ids[1]
    probe = {'plaintext_chunk_hex': data['plaintext_chunk_hex'], 'report': {}}
    sessions[next_node_id] = {'sender_id': sender_id, 'path': failed_path_ids}
    
    path_names = [nodes[nid]['name'] for nid in failed_path_ids if nid in nodes]
    emit('diagnostic_started', {'path_names': path_names}, room=sender_id)
    emit('forward_diagnostic', {
        'from_node': nodes[sender_id], 'to_node': nodes[next_node_id], 'probe': probe
    }, room=next_node_id)

@socketio.on('forward_diagnostic_response')
def handle_diagnostic_response(probe):
    intermediate_id = request.sid
    session = sessions.pop(intermediate_id, None)
    if not session: return

    path, sender_id = session['path'], session['sender_id']
    current_index_in_path = path.index(intermediate_id)
    
    if current_index_in_path < len(path) - 2:
        next_node_id = path[current_index_in_path + 1]
        sessions[next_node_id] = session
        emit('forward_diagnostic', {
            'from_node': nodes[intermediate_id], 'to_node': nodes[next_node_id], 'probe': probe
        }, room=next_node_id)
    else:
        emit('diagnostic_complete', {'probe': probe}, room=sender_id)

if __name__ == '__main__':
    public_url = ngrok.connect(5000)
    print("="*80)
    print("Flask server with Robust Rerouting is starting...")
    print(f" * Visualizer URL: {public_url}")
    print(" * Open this URL in at least 3-4 browser tabs to create a sparse network.")
    print("="*80)
    socketio.run(app, port=5000)

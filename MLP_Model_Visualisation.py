!pip install --ignore-installed pyngrok flask

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

import os
from flask import Flask, render_template
from pyngrok import ngrok

os.system(f"ngrok config add-authtoken 2yRC04Bqq3HdKaTA4x7ghcYGfi8_4bwcVxeu2JTVXV4zzwxo8")

if not os.path.exists('templates'):
    os.makedirs('templates')

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLP Chained Encryption Visualizer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f172a, #1e3a8a, #4c1d95);
            background-size: 200% 200%;
            color: #d1d5db;
            animation: moveGradient 20s ease infinite;
            overflow-x: hidden;
        }

        @keyframes moveGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .mono { font-family: 'Roboto Mono', monospace; }

        .glass-panel {
            background: rgba(31, 41, 55, 0.5);
            -webkit-backdrop-filter: blur(12px);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }

        .node {
            width: 90px;
            height: 90px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
            flex-direction: column;
            font-size: 12px;
            transition: all 0.3s ease;
        }
        .node.sender { border-color: #3b82f6; background-color: rgba(59, 130, 246, 0.2); }
        .node.receiver { border-color: #22c55e; background-color: rgba(34, 197, 94, 0.2); }
        .node.intermediate { border-color: #9ca3af; background-color: rgba(156, 163, 175, 0.2); }

        .link {
            flex-grow: 1;
            height: 6px;
            background-color: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
            position: relative;
        }
        .chunk-packet {
            position: absolute;
            width: 55px;
            height: 55px;
            background: linear-gradient(45deg, #f59e0b, #fbbf24);
            border: 2px solid #fca5a5;
            border-radius: 12px;
            top: 50%;
            transform: translateY(-50%);
            left: -55px;
            transition: left 1s linear, box-shadow 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            z-index: 10;
            color: #422006;
            box-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
        }
        .log-panel {
            padding: 1.5rem;
            height: 400px;
            overflow-y: auto;
        }
        .log-panel h3 {
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }
        .log-entry {
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .log-title { font-weight: bold; color: #9ca3af; }
        .log-math {
            white-space: pre-wrap;
            word-break: break-all;
            background-color: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .corruption-toggle {
            margin-top: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
        }
        .switch {
            position: relative;
            display: inline-block;
            width: 34px;
            height: 20px;
        }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: rgba(255,255,255,0.3);
            transition: .4s;
            border-radius: 20px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 14px; width: 14px;
            left: 3px; bottom: 3px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider { background-color: #ef4444; }
        input:checked + .slider:before { transform: translateX(14px); }
        #modal { transition: opacity 0.3s ease; }

        .custom-button {
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            font-weight: 500;
        }
        .custom-button:hover:not(:disabled) {
            background-color: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }
        .custom-button:disabled {
            background-color: rgba(55, 65, 81, 0.4);
            border-color: rgba(255, 255, 255, 0.1);
            color: #9ca3af;
            cursor: not-allowed;
        }

        .mlp-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            height: 300px;
            padding: 20px;
        }
        .mlp-layer {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            z-index: 2;
        }
        .mlp-neuron {
            width: 10px;
            height: 10px;
            background-color: rgba(107, 114, 128, 0.3);
            border-radius: 50%;
            transition: all 0.2s ease;
        }
        .mlp-neuron.active {
            transform: scale(1.8);
        }
        #mlp-input-layer .mlp-neuron.active { background-color: #3b82f6; box-shadow: 0 0 10px #3b82f6, 0 0 5px #3b82f6 inset; }
        #mlp-hidden-layer .mlp-neuron.active { background-color: #a855f7; box-shadow: 0 0 10px #a855f7, 0 0 5px #a855f7 inset; }
        #mlp-output-layer .mlp-neuron.active { background-color: #f59e0b; box-shadow: 0 0 10px #f59e0b, 0 0 5px #f59e0b inset; }

        #mlp-connections-svg {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 1;
        }
        .mlp-connection {
            stroke: rgba(107, 114, 128, 0.1);
            stroke-width: 0.5px;
            transition: all 0.3s ease-out;
        }
        .mlp-connection.active {
            stroke: #facc15;
            stroke-width: 1.5px;
        }
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="max-w-7xl mx-auto">
        <h1 class="text-4xl font-bold text-center mb-4 text-white">MLP Chained Encryption Visualizer</h1>
        <p class="text-center text-gray-300 mb-8">A visual simulation using a true MLP to generate chained keys.</p>

        <div class="glass-panel p-6 mb-8 flex flex-col md:flex-row items-center justify-center gap-8">
            <div class="flex flex-col items-start">
                <span class="block text-sm font-medium text-gray-300 mb-2">1. Choose a File</span>
                <div class="flex items-center gap-4">
                    <input type="file" id="fileInput" class="hidden"/>
                    <label for="fileInput" class="text-white py-2 px-5 rounded-lg custom-button cursor-pointer">
                        Select File
                    </label>
                    <span id="fileName" class="text-sm text-gray-400">No file selected</span>
                </div>
            </div>
            <button id="initButton" class="w-full md:w-auto text-white py-2 px-5 rounded-lg custom-button">2. Load & Initialize</button>
            <button id="sendButton" class="w-full md:w-auto text-white py-2 px-5 rounded-lg custom-button" disabled>3. Send Next Chunk</button>
        </div>

        <div id="statusPanel" class="glass-panel p-5 mb-8 text-center">
             <p class="mono text-lg" id="statusText">Please load a file to begin.</p>
        </div>

        <div id="mlp-section" class="hidden">
            <div class="glass-panel p-6 mb-8">
                 <h2 class="text-2xl font-bold text-center mb-4">MLP Key Generation</h2>
                 <div class="mlp-container">
                     <div id="mlp-input-layer" class="mlp-layer"></div>
                     <svg id="mlp-connections-svg"></svg>
                     <div id="mlp-hidden-layer" class="mlp-layer"></div>
                     <div id="mlp-output-layer" class="mlp-layer"></div>
                 </div>
            </div>
            <div class="log-panel glass-panel mb-8" id="mlpLog">
                <h3 class="text-xl font-bold text-purple-400">MLP Math Log (Example from one Neuron Path)</h3>
                <div id="mlpLogContent"></div>
            </div>
        </div>

        <div class="glass-panel p-8 mb-8">
            <h2 class="text-2xl font-bold text-center mb-4">Network Transfer</h2>
            <div class="flex items-center w-full" id="network-path"></div>
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
        <div class="log-panel glass-panel mt-8" id="systemLog">
            <h3 class="text-xl font-bold text-amber-400">System & Network Log</h3>
            <div id="systemLogContent"></div>
        </div>
    </div>

    <div id="modal" class="fixed inset-0 flex items-center justify-center p-4 hidden z-50">
        <div class="glass-panel max-w-lg text-center shadow-2xl p-8" style="background: rgba(127, 29, 29, 0.5); border-color: rgba(239, 68, 68, 0.5);">
            <h2 class="text-4xl font-extrabold text-white mb-4">CORRUPTION DETECTED!</h2>
            <p class="text-red-200 text-lg mb-6" id="modal-text"></p>
            <button id="closeModal" class="bg-red-500/50 hover:bg-red-500/75 text-white font-bold py-2 px-6 rounded-lg custom-button">Acknowledge</button>
        </div>
    </div>

    <script>
    let state = {
        originalBytes: null,
        currentChunkIndex: 0,
        senderKey: null,
        receiverKey: null,
        isAnimating: false,
        isInitialized: false,
        isCorrupted: false,
        totalChunks: 0,
    };
    const CHUNK_SIZE_BYTES = 1024;
    const INITIAL_VECTOR_STRING = 'MySharedSecretForStartingTheChain';
    const NUM_INTERMEDIATE_NODES = 3;
    const MLP_INPUT_SIZE = 32;
    const MLP_HIDDEN_SIZE = 64;
    const MLP_OUTPUT_SIZE = 32;
    class MLP {
        constructor(w1, b1, w2, b2) {
            this.w1 = w1; this.b1 = b1; this.w2 = w2; this.b2 = b2;
        }
        static relu(x) { return Math.max(0, x); }
        static sigmoid(x) { return 1 / (1 + Math.exp(-x)); }
        predict(input) {
            let hidden = new Array(MLP_HIDDEN_SIZE).fill(0);
            for (let j = 0; j < MLP_HIDDEN_SIZE; j++) {
                for (let i = 0; i < MLP_INPUT_SIZE; i++) {
                    hidden[j] += input[i] * this.w1[i][j];
                }
                hidden[j] += this.b1[j];
            }
            hidden = hidden.map(MLP.relu);
            let output = new Array(MLP_OUTPUT_SIZE).fill(0);
            for (let j = 0; j < MLP_OUTPUT_SIZE; j++) {
                for (let i = 0; i < MLP_HIDDEN_SIZE; i++) {
                    output[j] += hidden[i] * this.w2[i][j];
                }
                output[j] += this.b2[j];
            }
            output = output.map(MLP.sigmoid);
            return { hidden, output };
        }
    }
    const seededRandom = (seed) => {
        let state = seed;
        return () => {
            state = (state * 9301 + 49297) % 233280;
            return (state / 233280.0) * 2 - 1;
        };
    };
    function generateFixedWeights(inputSize, outputSize, seed) {
        const rand = seededRandom(seed);
        let weights = Array(inputSize).fill(0).map(() => Array(outputSize).fill(0));
        for (let i = 0; i < inputSize; i++) {
            for (let j = 0; j < outputSize; j++) { weights[i][j] = rand(); }
        }
        return weights;
    }
    function generateFixedBiases(size, seed) {
        const rand = seededRandom(seed);
        let biases = new Array(size);
        for (let i = 0; i < size; i++) { biases[i] = rand(); }
        return biases;
    }
    const w1 = generateFixedWeights(MLP_INPUT_SIZE, MLP_HIDDEN_SIZE, 12345);
    const b1 = generateFixedBiases(MLP_HIDDEN_SIZE, 54321);
    const w2 = generateFixedWeights(MLP_HIDDEN_SIZE, MLP_OUTPUT_SIZE, 67890);
    const b2 = generateFixedBiases(MLP_OUTPUT_SIZE, 9876);
    const mlp = new MLP(w1, b1, w2, b2);
    const fileInput = document.getElementById('fileInput'), initButton = document.getElementById('initButton'),
          sendButton = document.getElementById('sendButton'), statusText = document.getElementById('statusText'),
          senderLogContent = document.getElementById('senderLogContent'), receiverLogContent = document.getElementById('receiverLogContent'),
          systemLogContent = document.getElementById('systemLogContent'), networkPath = document.getElementById('network-path'),
          modal = document.getElementById('modal'), closeModal = document.getElementById('closeModal'),
          modalText = document.getElementById('modal-text'), fileName = document.getElementById('fileName'),
          mlpSection = document.getElementById('mlp-section'), mlpLogContent = document.getElementById('mlpLogContent'),
          mlpInputLayer = document.getElementById('mlp-input-layer'), mlpHiddenLayer = document.getElementById('mlp-hidden-layer'),
          mlpOutputLayer = document.getElementById('mlp-output-layer'), mlpConnectionsSvg = document.getElementById('mlp-connections-svg');
    function bytesToBinaryString(bytes) {
        return Array.from(bytes).map(b => b.toString(2).padStart(8, '0')).join('');
    }
    async function stringToSha256Bytes(str) {
        const data = new TextEncoder().encode(str);
        return new Uint8Array(await crypto.subtle.digest('SHA-256', data));
    }
    async function bytesToSha256Bytes(bytes) {
        return new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
    }
    async function getInitialVector() {
        return await stringToSha256Bytes(INITIAL_VECTOR_STRING);
    }
    function preprocessChunkForMLP(chunkBytes) {
        const inputVector = new Array(MLP_INPUT_SIZE).fill(0);
        const len = Math.min(chunkBytes.length, MLP_INPUT_SIZE);
        for (let i = 0; i < len; i++) { inputVector[i] = chunkBytes[i] / 255.0; }
        return inputVector;
    }
    async function hypernetwork_key_generator(chunk_bytes) {
        const inputVector = preprocessChunkForMLP(chunk_bytes);
        const { output } = mlp.predict(inputVector);
        return new Uint8Array(output.map(v => Math.floor(v * 255)));
    }
    async function hash_plaintext_chunk(chunk_bytes) {
        const hashBytes = await bytesToSha256Bytes(chunk_bytes);
        return Array.from(hashBytes).map(b => b.toString(16).padStart(2, '0')).join('');
    }
    function fast_xor_transform(binary_data, key_bytes) {
        const data_len = binary_data.length;
        if (data_len === 0) return "";
        let key_binary = bytesToBinaryString(key_bytes);
        const key_len = key_binary.length;
        if (key_len === 0) return binary_data;
        let tiled_key_binary = key_binary.repeat(Math.ceil(data_len / key_len)).slice(0, data_len);
        let result_binary = '';
        for (let i = 0; i < data_len; i++) {
            result_binary += binary_data[i] === tiled_key_binary[i] ? '0' : '1';
        }
        return result_binary;
    }
    function addLog(panel, content) {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = content;
        panel.prepend(entry);
    }
    function truncate(str, len = 64) {
        return str && str.length > len ? str.substring(0, len) + '...' : str;
    }
    function bytesToHex(bytes) {
        return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
    }
    function getMathsDisplay(data_bin, key_bytes, result_bin) {
        let key_bin = bytesToBinaryString(key_bytes);
        const display_len = 32;
        const tiled_key_bin = key_bin.repeat(Math.ceil(display_len / key_bin.length));
        return `<div class="mono text-xs p-3 rounded-lg mt-2 log-math">` +
               `<span class="text-gray-400">   Data: </span>${truncate(data_bin, display_len)}<br>` +
               `<span class="text-gray-400">    Key: </span>${truncate(tiled_key_bin, display_len)} (tiled)<br>` +
               `<span class="text-gray-400">XOR(^) --------------------------------</span><br>` +
               `<span class="text-gray-400"> Result: </span>${truncate(result_bin, display_len)}</div>`;
    }
    function buildNetworkPath() {
        networkPath.innerHTML = '';
        const senderNode = document.createElement('div');
        senderNode.className = 'node sender glass-panel';
        senderNode.innerHTML = 'SENDER';
        networkPath.appendChild(senderNode);
        for (let i = 0; i < NUM_INTERMEDIATE_NODES; i++) {
            const link = document.createElement('div');
            link.className = 'link mx-2';
            const chunkPacket = document.createElement('div');
            chunkPacket.className = 'chunk-packet hidden';
            chunkPacket.id = `chunk-packet-${i}`;
            link.appendChild(chunkPacket);
            networkPath.appendChild(link);
            const intermediateNode = document.createElement('div');
            intermediateNode.className = 'node intermediate glass-panel';
            intermediateNode.id = `node-${i}`;
            intermediateNode.innerHTML = `<span>NODE ${i+1}</span><div class="corruption-toggle"><span class="mr-1 text-red-400">Corrupt</span><label class="switch"><input type="checkbox" id="corrupt-node-${i}"><span class="slider"></span></label></div>`;
            networkPath.appendChild(intermediateNode);
        }
        const finalLink = document.createElement('div');
        finalLink.className = 'link mx-2';
        const finalChunkPacket = document.createElement('div');
        finalChunkPacket.className = 'chunk-packet hidden';
        finalChunkPacket.id = `chunk-packet-${NUM_INTERMEDIATE_NODES}`;
        finalLink.appendChild(finalChunkPacket);
        networkPath.appendChild(finalLink);
        const receiverNode = document.createElement('div');
        receiverNode.className = 'node receiver glass-panel';
        receiverNode.innerHTML = 'RECEIVER';
        networkPath.appendChild(receiverNode);
    }
    function setupMlpVisualizer() {
        mlpInputLayer.innerHTML = ''; mlpHiddenLayer.innerHTML = ''; mlpOutputLayer.innerHTML = '';
        mlpConnectionsSvg.innerHTML = '';
        for (let i = 0; i < MLP_INPUT_SIZE; i++) mlpInputLayer.innerHTML += `<div class="mlp-neuron" id="mlp-in-${i}"></div>`;
        for (let i = 0; i < MLP_HIDDEN_SIZE; i++) mlpHiddenLayer.innerHTML += `<div class="mlp-neuron" id="mlp-hidden-${i}"></div>`;
        for (let i = 0; i < MLP_OUTPUT_SIZE; i++) mlpOutputLayer.innerHTML += `<div class="mlp-neuron" id="mlp-out-${i}"></div>`;
        setTimeout(() => {
            const connectLayers = (layer1, layer2, svg, connectionClass) => {
                const neurons1 = Array.from(layer1.children);
                const neurons2 = Array.from(layer2.children);
                for (let i = 0; i < neurons1.length; i++) {
                    for (let j = 0; j < neurons2.length; j++) {
                        const n1Rect = neurons1[i].getBoundingClientRect();
                        const n2Rect = neurons2[j].getBoundingClientRect();
                        const svgRect = svg.getBoundingClientRect();
                        if (svgRect.width === 0) return;
                        const x1 = n1Rect.left + n1Rect.width / 2 - svgRect.left;
                        const y1 = n1Rect.top + n1Rect.height / 2 - svgRect.top;
                        const x2 = n2Rect.left + n2Rect.width / 2 - svgRect.left;
                        const y2 = n2Rect.top + n2Rect.height / 2 - svgRect.top;
                        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                        path.setAttribute('d', `M${x1},${y1} L${x2},${y2}`);
                        path.setAttribute('class', connectionClass);
                        path.id = `${connectionClass}-${i}-${j}`;
                        svg.appendChild(path);
                    }
                }
            };
            connectLayers(mlpInputLayer, mlpHiddenLayer, mlpConnectionsSvg, 'conn-1');
            connectLayers(mlpHiddenLayer, mlpOutputLayer, mlpConnectionsSvg, 'conn-2');
        }, 100);
    }
    async function animateMLP(chunkBytes) {
        mlpSection.classList.remove('hidden');
        mlpLogContent.innerHTML = '';
        const inputVector = preprocessChunkForMLP(chunkBytes);
        const { hidden: hiddenResult } = mlp.predict(inputVector);
        const highlightElements = async (selector, delay) => {
            document.querySelectorAll(selector).forEach(el => el.classList.add('active'));
            await sleep(delay);
        };
        const clearElements = (selector) => {
             document.querySelectorAll(selector).forEach(el => el.classList.remove('active'));
        };
        await highlightElements('#mlp-input-layer .mlp-neuron', 250);
        await highlightElements('.conn-1', 350);
        clearElements('#mlp-input-layer .mlp-neuron');
        await highlightElements('#mlp-hidden-layer .mlp-neuron', 250);
        clearElements('.conn-1');
        await highlightElements('.conn-2', 350);
        clearElements('#mlp-hidden-layer .mlp-neuron');
        await highlightElements('#mlp-output-layer .mlp-neuron', 250);
        clearElements('.conn-2');
        await sleep(400);
        clearElements('.mlp-neuron');
        const sampleByte = chunkBytes[0];
        const sampleInput = inputVector[0];
        const hiddenSum = mlp.b1[0] + inputVector.reduce((sum, val, i) => sum + val * mlp.w1[i][0], 0);
        const hiddenActivation = MLP.relu(hiddenSum);
        const outputSum = mlp.b2[0] + hiddenResult.reduce((sum, val, i) => sum + val * mlp.w2[i][0], 0);
        const outputActivation = MLP.sigmoid(outputSum);
        const finalKeyByte = Math.floor(outputActivation * 255);
        mlpLogContent.innerHTML = `
            <div class="log-entry mono text-xs"><b>1. Input Normalization (Neuron 0):</b><div class="pl-4">Byte Value ${sampleByte} / 255.0 = <b>${sampleInput.toFixed(4)}</b></div></div>
            <div class="log-entry mono text-xs"><b>2. Hidden Layer (Neuron 0):</b><div class="pl-4">Weighted Sum + Bias = <b>${hiddenSum.toFixed(4)}</b></div><div class="pl-4">ReLU( ${hiddenSum.toFixed(4)} ) = <b>${hiddenActivation.toFixed(4)}</b></div></div>
            <div class="log-entry mono text-xs"><b>3. Output Layer (Neuron 0):</b><div class="pl-4">Weighted Sum + Bias = <b>${outputSum.toFixed(4)}</b></div><div class="pl-4">Sigmoid( ${outputSum.toFixed(4)} ) = <b>${outputActivation.toFixed(4)}</b></div></div>
            <div class="log-entry mono text-xs"><b>4. Final Key Generation (Byte 0):</b><div class="pl-4">floor( ${outputActivation.toFixed(4)} * 255 ) = <b>${finalKeyByte}</b></div></div>`;
        await sleep(500);
    }
    async function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
    async function animateChunk(payload) {
        state.isAnimating = true; sendButton.disabled = true;
        let currentPayload = { ...payload };
        for (let i = 0; i <= NUM_INTERMEDIATE_NODES; i++) {
            const chunkPacket = document.getElementById(`chunk-packet-${i}`);
            chunkPacket.innerText = `C${state.currentChunkIndex + 1}`;
            chunkPacket.classList.remove('hidden');
            chunkPacket.style.left = '-55px';
            await sleep(50);
            chunkPacket.style.left = 'calc(100% - 27px)';
            addLog(systemLogContent, `<div class="log-title">Chunk ${state.currentChunkIndex + 1} travelling...</div>`);
            await sleep(1000);
            chunkPacket.classList.add('hidden');
            if (i < NUM_INTERMEDIATE_NODES) {
                if (document.getElementById(`corrupt-node-${i}`).checked) {
                    const len = currentPayload.encodedChunkBinary.length;
                    const corruptIndex = Math.floor(Math.random() * len);
                    const newBit = currentPayload.encodedChunkBinary[corruptIndex] === '0' ? '1' : '0';
                    currentPayload.encodedChunkBinary = currentPayload.encodedChunkBinary.substring(0, corruptIndex) + newBit + currentPayload.encodedChunkBinary.substring(corruptIndex + 1);
                    addLog(systemLogContent, `<div class="log-title text-red-400 font-bold">Chunk ${state.currentChunkIndex + 1} corrupted at Node ${i+1}!</div>`);
                } else {
                    addLog(systemLogContent, `<div class="log-title">Chunk ${state.currentChunkIndex + 1} passed Node ${i+1} securely.</div>`);
                }
            }
        }
        state.isAnimating = false;
        return currentPayload;
    }
    fileInput.addEventListener('change', () => {
        fileName.textContent = fileInput.files.length > 0 ? fileInput.files[0].name : 'No file selected';
    });
    initButton.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) { statusText.textContent = 'Error: No file selected.'; return; }
        initButton.disabled = true; initButton.textContent = 'Loading...';
        statusText.textContent = 'Reading file...';
        senderLogContent.innerHTML = ''; receiverLogContent.innerHTML = ''; systemLogContent.innerHTML = '';
        mlpSection.classList.add('hidden');
        try {
            const arrayBuffer = await file.arrayBuffer();
            state.originalBytes = new Uint8Array(arrayBuffer);
            state.currentChunkIndex = 0;
            state.isCorrupted = false;
            state.totalChunks = Math.ceil(state.originalBytes.length / CHUNK_SIZE_BYTES);
            if(state.totalChunks === 0) {
                statusText.textContent = 'Error: File is empty.';
                initButton.disabled = false;
                return;
            }
            const initialVector = await getInitialVector();
            state.senderKey = initialVector;
            state.receiverKey = initialVector;
            state.isInitialized = true;
            sendButton.disabled = false;
            const initLog = `<div class="log-title">Initialization Complete</div><div>File Size: ${(state.originalBytes.length / 1024).toFixed(2)} KB</div><div>Chunks: ${state.totalChunks}</div><div class="mono text-xs mt-1"><span class="text-gray-400">IV: </span>${truncate(bytesToHex(initialVector))}</div>`;
            addLog(senderLogContent, initLog); addLog(receiverLogContent, initLog);
            addLog(systemLogContent, `<div class="log-title">System Initialized. Ready to send ${state.totalChunks} chunks.</div>`);
            statusText.textContent = `Ready to send Chunk 1 of ${state.totalChunks}`;
        } catch (error) {
            statusText.textContent = `Error: ${error.message}`;
        } finally {
            initButton.disabled = false;
            initButton.textContent = '2. Load & Initialize';
        }
    });
    sendButton.addEventListener('click', async () => {
        if (!state.isInitialized || state.isAnimating || state.isCorrupted || state.currentChunkIndex >= state.totalChunks) return;
        state.isAnimating = true; sendButton.disabled = true;
        const chunkIndex = state.currentChunkIndex;
        const start = chunkIndex * CHUNK_SIZE_BYTES;
        const end = Math.min(start + CHUNK_SIZE_BYTES, state.originalBytes.length);
        const plaintextChunkBytes = state.originalBytes.slice(start, end);
        await animateMLP(plaintextChunkBytes);
        const keyForEncoding = state.senderKey;
        const plaintextChunkBinary = bytesToBinaryString(plaintextChunkBytes);
        const encodedChunkBinary = fast_xor_transform(plaintextChunkBinary, keyForEncoding);
        const plaintextHash = await hash_plaintext_chunk(plaintextChunkBytes);
        const nextSenderKey = await hypernetwork_key_generator(plaintextChunkBytes);
        const senderMaths = getMathsDisplay(plaintextChunkBinary, keyForEncoding, encodedChunkBinary);
        addLog(senderLogContent, `<div class="log-title">Sending C${chunkIndex + 1}</div><div class="mono text-xs"><div><span class="text-gray-400">Hash (for check):</span> ${truncate(plaintextHash)}</div><div><span class="text-gray-400">Key Used (from C${chunkIndex}):</span> ${truncate(bytesToHex(keyForEncoding))}</div></div><details><summary class="cursor-pointer text-sm text-blue-400 mt-2">XOR Math</summary>${senderMaths}</details>`);
        state.senderKey = nextSenderKey;
        const payload = { encodedChunkBinary, plaintextHash };
        const receivedPayload = await animateChunk(payload);
        const keyForDecoding = state.receiverKey;
        const decodedChunkBinary = fast_xor_transform(receivedPayload.encodedChunkBinary, keyForDecoding);
        const decodedChunkBytes = new Uint8Array(decodedChunkBinary.match(/.{1,8}/g).map(byte => parseInt(byte, 2)));
        const receivedHash = await hash_plaintext_chunk(decodedChunkBytes);
        const receiverMaths = getMathsDisplay(receivedPayload.encodedChunkBinary, keyForDecoding, decodedChunkBinary);
        if (receivedHash === receivedPayload.plaintextHash) {
            const nextReceiverKey = await hypernetwork_key_generator(decodedChunkBytes);
            state.receiverKey = nextReceiverKey;
            addLog(receiverLogContent, `<div class="log-title text-green-400">Received C${chunkIndex + 1}</div><div class="mono text-xs text-green-400">Hashes Match!</div><details><summary class="cursor-pointer text-sm text-blue-400 mt-2">XOR Math</summary>${receiverMaths}</details>`);
            state.currentChunkIndex++;
            if (state.currentChunkIndex >= state.totalChunks) {
                statusText.textContent = `Success! All ${state.totalChunks} chunks transferred securely.`;
                sendButton.disabled = true;
                addLog(systemLogContent, `<div class="log-title text-green-400 font-bold">TRANSFER COMPLETE</div>`);
            } else {
                statusText.textContent = `Ready to send Chunk ${state.currentChunkIndex + 1} of ${state.totalChunks}`;
                sendButton.disabled = false;
            }
        } else {
            state.isCorrupted = true; sendButton.disabled = true;
            addLog(receiverLogContent, `<div class="log-title text-red-400 font-bold">CORRUPTION on C${chunkIndex + 1}</div><div class="mono text-xs text-red-400">Hashes Mismatch!</div><details><summary class="cursor-pointer text-sm text-blue-400 mt-2">XOR Math</summary>${receiverMaths}</details>`);
            modalText.innerHTML = `Integrity check for <strong>Chunk ${chunkIndex + 1}</strong> failed. Data tampered with in transit.`;
            modal.classList.remove('hidden'); modal.style.opacity = 1;
            statusText.textContent = `FATAL ERROR: Corruption detected. Transfer aborted.`;
        }
        state.isAnimating = false;
    });
    closeModal.addEventListener('click', () => {
        modal.style.opacity = 0; setTimeout(() => modal.classList.add('hidden'), 300);
    });
    window.onload = () => {
        buildNetworkPath();
        setupMlpVisualizer();
    }

    </script>
</body>
</html>
"""

with open('templates/index.html', 'w') as f:
    f.write(html_content)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    public_url = ngrok.connect(5000)
    print("="*50)
    print("Flask server is starting...")
    print(f" * Visualizer is running on: {public_url}")
    print("="*50)

    app.run(port=5000)

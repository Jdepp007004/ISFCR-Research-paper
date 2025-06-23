Flask MLP-Based Chained Encryption Visualizer (Single-Cell Version)
This application provides a simplified, single-page visual simulation of an MLP-based chained encryption protocol. It is designed to run entirely within a single Google Colab cell, making it easy to set up and demonstrate the core concepts of the encryption technique without the complexity of a multi-user network.

The visualizer simulates a fixed network path (Sender -> Intermediate Nodes -> Receiver) and focuses on visualizing the step-by-step mathematical operations, including the MLP's key generation process and the XOR-based encryption.

Key Features
Single-Page Simulation: Everything happens on one page, providing a clear and focused demonstration.

Fixed Network Path: Simulates a transfer across a predefined number of intermediate nodes.

Detailed MLP Visualization:

A dedicated panel shows the Multi-Layer Perceptron (Input, Hidden, Output layers).

When a key is generated, the visualizer animates the flow of data through the network, highlighting active neurons and connections.

A math log provides a concrete example of the calculations for one neuron path, from input normalization to the final key byte generation.

Step-by-Step Logging: Separate, scrollable panels provide detailed logs for the Sender, Receiver, and the overall System. The logs include cryptographic hashes, keys used, and the results of XOR operations.

Simulated Packet Corruption: Users can toggle a "Corrupt" switch on any intermediate node to simulate data tampering during transit.

Integrity Verification: The receiver verifies the integrity of each chunk by comparing a locally generated hash of the decrypted data with the hash provided by the sender. A mismatch immediately halts the transfer and displays a prominent warning.

How It Works
Backend: A minimal Flask server is used simply to serve the index.html file. pyngrok exposes this local server to the web. All logic is handled client-side in JavaScript.

Frontend: A single HTML page with vanilla JavaScript contains the entire simulation logic.

Encryption Chain:

The process is initiated with a shared, hardcoded Initial Vector (IV).

Sending Chunk N: The sender uses Key N to perform a bitwise XOR operation on the plaintext data, producing the encrypted chunk.

The sender calculates a SHA-256 hash of the plaintext chunk, which will be used for the integrity check.

The sender then feeds the plaintext chunk into the MLP to generate the next key in the sequence, Key N+1.

Receiving Chunk N: The receiver uses its own Key N (which it generated after receiving the previous chunk) to perform a reverse XOR operation on the encrypted data, yielding the decrypted plaintext.

The receiver calculates a SHA-256 hash of this newly decrypted data and compares it to the hash sent by the sender.

If hashes match: The transfer is successful. The receiver feeds the decrypted plaintext into its identical MLP to generate its Key N+1, ensuring it stays in sync with the sender for the next chunk.

If hashes mismatch: The transfer is marked as corrupt, and the simulation stops.

Setup and Usage in Google Colab
Run the Cell: Copy and paste the entire Python script into a single cell in a Google Colab notebook.

Provide Ngrok Token: When prompted, paste your ngrok authtoken and press Enter. You can get a free token from the ngrok dashboard.

Open the URL: The script will start the server and print a public ngrok.io URL. Click this link to open the visualizer in a new browser tab.

Run the Simulation:

Click "Select File" and choose any file from your local machine.

Click "Load & Initialize". This reads the file, calculates the total number of chunks, and sets up the initial state.

Click "Send Next Chunk" to start the process. The animation will show the MLP generating a key, and then a packet moving across the network path.

To test the security, click one of the "Corrupt" toggles on an intermediate node before sending a chunk. When the packet passes through, it will be altered, and the receiver will detect the failure.

Technologies Used
Backend: Python, Flask

Tunneling: pyngrok

Frontend: HTML, Vanilla JavaScript

Styling: Tailwind CSS
